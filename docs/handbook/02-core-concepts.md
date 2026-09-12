# 2. Core Concepts

This chapter defines the terms used throughout QUEST. The examples refer to
the 32-satellite quickstart configuration.

## Orbit and Earth terms

**Low-Earth Orbit (LEO).** An Earth orbit at relatively low altitude. The
quickstart models satellites at 550 km; QUEST uses the configured altitude in
its propagator.

**Constellation.** A coordinated collection of satellites. In QUEST, the full
constellation contains every configured shell and ground station.

**Orbital shell.** A group of satellites with common orbital parameters. The
quickstart shell has four planes and eight satellites per plane, for 32 total.

**Orbital plane.** A geometric plane containing an orbit. `planes = 4` creates
four copies whose ascending nodes are distributed over the configured arc.

**Satellite node.** One modeled satellite and, when active, its Firecracker
microVM. A satellite remains part of the topology even while its microVM is
suspended.

**Ground station.** A fixed Earth location with an always-active microVM and
direct radio-style links to selected visible satellites. `potsdam` and
`berlin` are the two quickstart stations.

**Spatial workload.** Code whose behavior depends on location, geometry, or
Earth-observation coverage.

## Contact and network terms

**Line of sight.** An unobstructed geometric view between two nodes. QUEST
uses orbital geometry to determine which satellite pairs and ground contacts
are possible.

**Elevation angle.** The angle of a satellite above a ground station's local
horizon. With `min_elevation = 25.0`, lower contacts are not eligible.

**Contact.** A currently eligible direct link between a ground station and a
satellite. Eligibility alone does not guarantee selection when antennas are
limited.

**Antenna capacity.** The maximum number of simultaneous direct satellite
contacts a ground station can select. Potsdam's `antenna_number = 2` permits
up to two; Berlin's value `1` permits one. The scheduler keeps existing
contacts when possible and gives waiting satellites fair priority.

**Inter-satellite link (ISL).** A link between satellites. A route may cross
several ISLs before reaching a ground station.

**Backhaul.** A direct modeled link between ground stations representing a
terrestrial path. QUEST derives its delay from great-circle distance times the
configured path-stretch factor; it is distinct from a satellite route.

**Bandwidth.** The configured link capacity in kilobits per second (kbit/s).
Each selected antenna contact receives the full configured contact bandwidth;
`antenna_number` does not divide one link's bandwidth among contacts.

**Delay.** One-way modeled propagation delay, represented at runtime in
microseconds. Guest ping normally observes a round trip plus execution and
physical-host effects.

## Time and state terms

**Topology timestep.** One generated instant at which QUEST can apply changed
machine or link state. With `resolution = 5`, the quickstart advances every
five seconds.

**Topology archive.** The ZIP produced by `satgen.py`. It contains validated
configuration, initial machine descriptions, and time-indexed differences for
machines and links.

**Activation.** The rule deciding which satellite microVMs should run. `bbox`
uses geographic position; `ground_station_contact` uses selected direct
contacts. Ground-station microVMs remain active.

**Suspend versus stop.** Suspending preserves guest state and memory so a
satellite can resume later. Stopping tears down the machine at the end of the
run.

## Virtualization terms

**Virtual machine (VM).** Software emulating a computer. QUEST uses small
microVMs rather than general-purpose desktop VMs.

**MicroVM.** A minimal virtual machine optimized for fast, isolated workloads.
Each active QUEST node runs one Firecracker microVM.

**Firecracker.** The virtual machine monitor that creates and controls QUEST
microVMs on the remote Linux worker.

**Kernel-based Virtual Machine (KVM).** The Linux virtualization interface
Firecracker accesses through `/dev/kvm`. Nested KVM must be supported when the worker itself is a VM.

**Guest kernel.** The Linux `vmlinux` binary booted inside every microVM. It is
built locally and copied to `/celestial` on the worker.

**Root filesystem.** The read-only `.img` containing the guest operating
system, dependencies, and workload startup script.

**Overlay disk.** A per-machine writable ext4 file layered over the read-only
root. The validator writes its CSV to this disk.

## Distributed-system terms

**Coordinator.** The Python program `celestial.py`. It reads the topology
archive, distributes initial machines to workers, and sends timed updates.

**Worker.** The privileged Linux/amd64 program `celestial.bin`. It controls
microVMs, guest networking, information services, and link emulation.

**gRPC.** The remote procedure call framework used between coordinator
and worker. Its messages and service methods are defined in
`proto/celestial/celestial.proto`.

**Orchestrator.** The Go component that translates initialization and state
updates into operations on virtualization, peer, and network backends.

**Topology generation.** The offline calculation performed by `satgen.py`.
It computes positions, contacts, routing, activation, and time-indexed changes.

**Emulation.** Executing real workload code in microVMs while applying the
generated network and machine state in wall-clock time. The emulator is not a
physical satellite or radio.

## One complete lifecycle

```text
configure
→ generate topology
→ build guest artifacts
→ start worker
→ start coordinator
→ apply timed updates
→ collect results
```

