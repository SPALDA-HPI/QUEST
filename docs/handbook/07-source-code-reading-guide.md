# 7. Source-Code Reading Guide

Read source in data-flow order, not alphabetical order. For every stage below,
use the same four questions: what directory owns this concern, which files are
the minimum reading set, what enters/leaves them, and what can you now explain?

## Stage 1: configuration contract

### Directory Overview

The repository root holds runnable examples; `celestial/` holds Python model
and generation code.

### Files to Read

1. `quickstart/quickstart.toml`
2. `celestial/config.py`
3. `celestial/activation.py`

### Call/Data Flow

`toml.load` produces a dictionary. `Config` validates it, supplies defaults,
merges global and local tables, and constructs `Shell`, `GroundStation`, and
`MachineConfig` objects. `SatelliteActivation` converts the string policy to
an enum.

Source fact: backhaul pairing, contact-mode ground-station presence, unique
names, and the `antenna_number`/`all` combination are checked here.

Why it matters: add or remove a TOML feature at this boundary first, then
follow its typed value downstream.

### Checkpoint

Explain the final effective root image, memory, contact bandwidth, and antenna
count for both quickstart ground stations.

## Stage 2: orbit and shell state

### Directory Overview

`satgen.py` is the command entry point. The misspelled historical filename
`celestial/satgen_connstellation.py` coordinates multiple shells;
`celestial/shell.py` models one shell; `celestial/sgp4_solver.py` propagates
orbits using Simplified General Perturbations 4 (SGP4).

### Files to Read

1. `satgen.py`
2. `celestial/satgen_connstellation.py`
3. `celestial/shell.py`
4. `celestial/sgp4_solver.py`

### Call/Data Flow

`satgen.py` advances from `offset` in `resolution` steps.
`SatgenConstellation.step` tells every shell to prepare positions, coordinates
shared contact selection, tells every shell to finish, and forwards
differences to the serializer.

`Shell.prepare_step` advances satellite arrays, rotates ground positions,
updates inter-satellite links, and exposes visible ground contacts.
`Shell.finish_step` filters those contacts, applies activation, recalculates
paths, and compares current state with the previous timestep.

### Checkpoint

Find where a satellite's `in_bbox` value is written and where the same
satellite becomes `VMState.ACTIVE` or `VMState.STOPPED`.

## Stage 3: retained contact extensions

### Directory Overview

Three small Python modules separate policy from orbital calculations.

### Files to Read

1. `celestial/activation.py`
2. `celestial/antenna.py`
3. `celestial/ground_station_backhaul.py`
4. `test/test_contact_activation.py`
5. `test/test_antenna_scheduler.py`
6. `test/test_ground_station_backhaul.py`

### Call/Data Flow

`activation_mask` chooses bounding-box or selected-contact activation.
`AntennaScheduler.select` receives visible `(shell, satellite)` keys per ground
station, retains still-visible assignments, and fills free antennas by oldest
waiting time and deterministic IDs. `ground_station_backhaul_links` yields one
unblocked link for each unordered station pair.

Source fact: backhaul propagation uses a 6,371 km Earth radius, 200,000,000 m/s
fiber propagation speed, and the configured path stretch.

Why it matters: those are controlled model constants, not measured HPI or
operator-network values.

### Checkpoint

Use the tests to predict which satellite wins a tie, what happens when a
selected satellite leaves visibility, and how many backhaul pairs three
stations create.

## Stage 4: archive format

### Directory Overview

`celestial/serializer.py` defines the writer interface;
`celestial/zip_serializer.py` implements the persistent format and its reader.

### Files to Read

1. `celestial/serializer.py`
2. `celestial/zip_serializer.py`
3. `test/test_zip_serializer.py`

### Call/Data Flow

`init_machine` records every machine once. `diff_machine` and `diff_link`
append changes under a timestep. `persist` packages the validated config,
initialization CSV, and binary difference files. `ZipDeserializer` exposes the
inverse `config`, `init_machines`, `diff_machines`, and `diff_links` methods.

Source fact: an initialization record contains nine columns: three identifier
values and six machine-configuration groups, with boot parameters joined by a
private separator.

Why it matters: changing `MachineConfig` requires updating writer, reader,
protobuf conversion, Go types, and tests together.

### Checkpoint

Generate the quickstart ZIP, list it with `unzip -l`, and map each entry to the
method that writes and reads it.

## Stage 5: Python coordination

### Directory Overview

The root `celestial.py` owns timing and assignment. `celestial/host.py` wraps
one gRPC stub. `celestial/proto_util.py` converts Python types to protocol
messages.

### Files to Read

1. `celestial.py`
2. `celestial/host.py`
3. `celestial/proto_util.py`

### Call/Data Flow

The coordinator creates hosts, registers them concurrently, distributes
machines round-robin, initializes all workers, obtains each timestep's archive
differences, converts them to streamed requests, and calls every host's
`update`. A `finally` block stops the workers.

### Checkpoint

Locate default port 1969, the round-robin expression, the point where the next
timestep is prepared, and the final stop path.

## Stage 6: protocol and Go server boundary

### Directory Overview

`proto/celestial/` contains one hand-authored schema and generated bindings.
The root Go entry point wires services; `pkg/server` implements gRPC methods.

### Files to Read

1. `proto/celestial/celestial.proto`
2. `celestial.go`
3. `pkg/server/server.go`

### Call/Data Flow

Python `Host` calls `Register`, `Init`, streamed `Update`, and `Stop`.
`pkg/server` converts protobuf IDs/config/state to orchestrator types and
invokes peering or orchestration. Generated `.pb.go`, `_pb2.py`, and `.pyi`
files are build outputs; regenerate rather than editing them.

### Checkpoint

For one `StateUpdateRequest`, trace a machine state and one link's latency,
bandwidth, blocked flag, source, and target into `orchestrator.State`.

## Stage 7: runtime implementation

### Directory Overview

- `pkg/orchestrator/`: desired/current state and path information.
- `pkg/virt/`: guest subnet, TAP, overlay, Firecracker, and state transitions.
- `pkg/peer/`: WireGuard peering between workers.
- `pkg/ebpfem/`: default bandwidth/delay/block backend.
- `pkg/netem/`: alternate traffic-control backend.
- `pkg/dns/`: guest `.celestial` lookup.
- `pkg/info/`: guest HTTP information API.

### Files to Read

Start with `pkg/orchestrator/orchestrator.go`, `pkg/orchestrator/virt.go`,
`pkg/virt/virt.go`, `pkg/virt/vm.go`, `pkg/virt/machine.go`, and
`pkg/virt/link.go`. Then follow only the backend relevant to your question.

### Call/Data Flow

`Orchestrator.Initialize` registers machines and hosts.
`Orchestrator.Update` compares desired machine/link state and invokes the
virtualization interface. `Virt` resolves IDs to subnets and calls Firecracker
or the selected network backend. DNS and HTTP query orchestrator information
without owning the topology.

### Checkpoint

Trace `Orchestrator.Update → Virt.SetLatency → setlatency →
NetworkEmulationBackend.SetLatency` manually. Interface dispatch means a
static call-graph tool may not display the whole path.

## Stage 8: tests as executable contracts

### Directory Overview

`test/` contains Python platform tests. Go package tests live beside the Go
source.

### Files to Read

Read these focused Python tests in order:

1. `test/test_config_activation.py`
2. `test/test_contact_activation.py`
3. `test/test_antenna_scheduler.py`
4. `test/test_constellation_antenna_limits.py`
5. `test/test_ground_station_backhaul.py`
6. `test/test_shell_activation.py`
7. `test/test_quickstart_config.py`
8. `test/test_zip_serializer.py`

Then read `pkg/orchestrator/*_test.go`, `pkg/peer/*_test.go`, and safe unit
tests in other packages. Privileged `pkg/virt`/eBPF tests may require Linux,
root, KVM, and host networking; compilation is separate from execution.

### Call/Data Flow

Each focused test names a retained contract and constructs the smallest real
input that exercises it. Use tests to confirm an interpretation, then return
to production code for the complete path.

### Checkpoint

For the source file you plan to change, identify the nearest existing test,
the observable behavior a regression would break, and the smallest additional
test needed before editing production code.

## Final reading summary

```text
directory overview → concrete files → call/data flow → checkpoint
```

Do not infer successful KVM execution, physical realism, or measured
performance from a class name, documentation claim, or passing local unit
test. Verify each at the boundary it actually exercises.
