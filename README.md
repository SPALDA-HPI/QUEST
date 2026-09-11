# QUEST

## Querying and Understanding Earth across Space and Time

QUEST is a long-lived teaching and research platform for developing and
evaluating distributed spatial data processing across Low-Earth Orbit (LEO)
satellite constellations. It gives student cohorts a reproducible emulator,
clean starter workload, and guided path from configuration to source code.

If Docker, Go, Python virtual environments, shell commands, Firecracker, or
satellite networks are new to you, begin with the documentation order below.
The guides explain terms before relying on them.

## What QUEST Is

QUEST combines orbital/network topology generation with real workload
execution in Firecracker microVMs. Satellite motion changes contacts, routes,
link properties, and which satellite microVMs are active over time.

The platform is intended for research prototypes such as distributed spatial
filters, joins, aggregations, placement strategies, and workload generators.
Wildfire, flood, environmental, maritime, and change-detection scenarios are
possible applications, not built-in capabilities.

QUEST is not a finished spatial database, query language, Earth-observation
dataset, or calibrated model of a particular operational constellation.

## Start Here

1. Read the [project overview](docs/handbook/01-project-overview.md).
2. Learn the [core concepts](docs/handbook/02-core-concepts.md).
3. Complete the [beginner quickstart](quickstart/README.md) without changing
   its known-good files.
4. Follow the [source-code reading guide](docs/handbook/07-source-code-reading-guide.md)
   with the repository open beside it.

The quickstart uses a local workstation for Docker builds and one unnamed,
shared HPI remote VM for the native Linux runtime. Never guess or publish that
VM's hostname. The HPI Scientific Compute Helpdesk supplies sudo policy and
working Kernel-based Virtual Machine (KVM) configuration; students manage Go,
Python, builds, and artifact transfer. Docker must not be installed or run
remotely because it can interfere with Celestial networking.

## Key Platform Features

- configurable orbital shells and ground stations;
- inter-satellite and ground-contact topology generation;
- bounding-box or selected-ground-contact satellite activation;
- finite ground-station antenna counts with fair cross-shell scheduling;
- multiple ground-station microVMs;
- optional direct ground-station backhaul with configurable bandwidth and path
  stretch;
- time-indexed topology serialization and replay;
- a Python coordinator and Linux/amd64 Go worker;
- Firecracker microVMs with dynamic eBPF or netem link enforcement;
- guest DNS and HTTP information services;
- focused tests and a small latency-validator workload.

Multiple configured ground stations are an existing Celestial capability.
QUEST retains it and the later activation, antenna, backhaul, build, validator,
and runtime extensions in this codebase.

## How QUEST Works

```text
configuration
→ topology generation
→ contact selection
→ serialization
→ coordinator
→ gRPC remote procedure calls
→ orchestrator
→ VM and network runtime
```

`satgen.py` validates TOML input and computes positions, contacts, routes,
activation, and timed differences. `celestial.py` replays the resulting ZIP to
one or more workers. `celestial.bin`, built from `celestial.go` and `pkg/`,
controls Firecracker guests and host networking.

Read the [architecture](docs/handbook/05-system-architecture.md) and exact
[startup call flow](docs/handbook/06-startup-call-flow.md) before changing a
cross-module feature.

## Repository Map

```text
QUEST/
├── README.md              starting page
├── celestial.py           Python coordinator entry point
├── satgen.py              topology-generation entry point
├── celestial.go           Go worker entry point
├── celestial/             Python config, orbit, contact, and serialization code
├── pkg/                   Go server, orchestration, VM, network, DNS, and HTTP code
├── proto/                 gRPC schema and generated bindings
├── builder/               guest root-filesystem builder
├── kernel/                guest-kernel builder and configs
├── animation/             topology visualization support
├── quickstart/            beginner validator example
├── docs/handbook/         progressive student handbook
├── docs/reference/        exact technical reference
└── test/                  Python and system/integration test material
```

## Recommended Reading Order

The handbook is deliberately progressive:

1. [Project overview](docs/handbook/01-project-overview.md)
2. [Core concepts](docs/handbook/02-core-concepts.md)
3. [Development environments](docs/handbook/03-development-environments.md)
4. [Configuration walkthrough](docs/handbook/04-configuration.md)
5. [System architecture](docs/handbook/05-system-architecture.md)
6. [Startup call flow](docs/handbook/06-startup-call-flow.md)
7. [Source-code reading guide](docs/handbook/07-source-code-reading-guide.md)
8. [Building workloads](docs/handbook/08-building-workloads.md)
9. [Testing and debugging](docs/handbook/09-testing-and-debugging.md)
10. [Running experiments](docs/handbook/10-running-experiments.md)
11. [Glossary](docs/handbook/11-glossary.md)

## Documentation

- [Documentation index](docs/README.md)
- [Quickstart](quickstart/README.md)
- [Configuration reference](docs/reference/configuration.md)
- [Compilation reference](docs/reference/compilation.md)
- [Guest kernel](docs/reference/kernel.md)
- [Nested virtualization and KVM](docs/reference/nested-virtualization.md)
- [Known limitations](docs/reference/limitations.md)
- [Output and result retrieval](docs/reference/output.md)
- [Runtime APIs and networking](docs/reference/runtime/README.md)

## Celestial Foundation

QUEST is derived from
[Celestial](https://github.com/OpenFogStack/celestial), the open-source LEO edge
emulator by Tobias Pfandzelter, David Bermbach, and the OpenFogStack
contributors. Internal `celestial` package, command, binary, protocol, and DNS
names remain for compatibility, and original copyright/GPL notices are
preserved.

Celestial is described in T. Pfandzelter and D. Bermbach, “Celestial: Virtual
Software System Testbeds for the LEO Edge,” Middleware 2022,
[DOI 10.1145/3528535.3531517](https://doi.org/10.1145/3528535.3531517).

## License

The code is distributed under the
[GNU General Public License version 3](LICENSE). Preserve upstream notices when
modifying derived files.
