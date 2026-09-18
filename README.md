# QUEST: Querying and Understanding Earth across Space and Time

## What QUEST Is

QUEST is derived from
[Celestial](https://github.com/OpenFogStack/celestial), which combines
orbital/network topology generation with the execution of real applications
in Firecracker microVMs. Satellite motion changes contacts, routes, link
properties, and which satellite microVMs are active over time. The platform is
intended for research prototypes such as distributed spatial filters, joins,
aggregations, placement strategies, and application prototypes.

## Start Here

1. Read the [project overview](docs/handbook/01-project-overview.md).
2. Learn the [core concepts](docs/handbook/02-core-concepts.md).
3. Complete the [beginner quickstart](quickstart/README.md).
4. Follow the [source-code reading guide](docs/handbook/07-source-code-reading-guide.md).

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
activation, and timed differences.

`celestial.py` replays the resulting ZIP to
one or more workers.

`celestial.bin`, built from `celestial.go` and `pkg/`,
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
├── celestial.go           Go worker/orchestrator entry point
├── celestial/             Python config, orbit, contact, and serialization code
├── pkg/                   Go server, orchestration, VM, network, DNS, and HTTP code
├── proto/                 gRPC schema and generated bindings
├── builder/               guest root-filesystem builder
├── kernel/                guest-kernel configuration and advanced builder
├── animation/             topology visualization support
├── quickstart/            beginner validator example
├── docs/handbook/         progressive student handbook
├── docs/reference/        exact technical reference
└── test/                  Python and system/integration tests
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
8. [Building applications](docs/handbook/08-building-applications.md)
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

The code is licensed under the terms of the
[GNU General Public License version 3](LICENSE).
