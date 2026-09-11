# 1. Project Overview

## Purpose

QUEST—**Querying and Understanding Earth across Space and Time**—is a
long-lived teaching and research platform for distributed spatial data
processing across Low-Earth Orbit (LEO) satellite constellations. It gives
student cohorts a common testbed in which satellite motion, intermittent
ground contact, constrained antennas, virtual machines, and changing network
paths can affect a distributed application.

The repository begins with a clean validator workload rather than a completed
spatial database. Your project work should add a clearly scoped spatial
operator or workload and measure it under documented assumptions.

## Research Questions QUEST Supports

QUEST can support questions such as:

- Where should a spatial operation run: on a satellite, another satellite, or
  a ground station?
- How do intermittent contacts and finite ground antennas affect result
  latency?
- When does inter-satellite forwarding help data reach a useful processor or
  downlink opportunity?
- How much data can an onboard spatial filter, join, or aggregation avoid
  transmitting?
- How should multiple ground stations and their terrestrial backhaul be
  represented in a reproducible experiment?

Wildfire, flood, environmental monitoring, maritime activity, and change
detection are possible workloads. They are not built-in claims or the full
scope of QUEST.

## What QUEST Provides

The platform provides:

- orbital position generation for configurable satellite shells;
- inter-satellite and ground-contact calculation;
- bounding-box or selected-contact satellite activation;
- finite, fairly scheduled ground-station antenna capacity;
- multiple ground-station microVMs and optional direct backhaul links;
- a time-indexed topology archive;
- a Python coordinator and Linux/amd64 Go worker;
- Firecracker microVM execution with changing link state;
- guest Domain Name System (DNS) and Hypertext Transfer Protocol (HTTP)
  information services;
- a small latency-validator quickstart and focused platform tests.

## What QUEST Does Not Provide

QUEST does not provide a finished query language, distributed database,
Earth-observation data product, physical radio simulator, or calibrated model
of a specific commercial constellation. It also does not hide the experiment
environment: you must record the input configuration, code commit, host
conditions, workload, and interpretation of each metric.

The platform does not install or repair privileged remote-host settings. The
HPI Scientific Compute Helpdesk supplies sudo policy and working Kernel-based
Virtual Machine (KVM) access. Students manage project-level Go and Python
tools; Docker is used only on the local workstation.

## Celestial Foundation

QUEST is derived from the open-source Celestial LEO edge emulator by Tobias
Pfandzelter, David Bermbach, and the OpenFogStack contributors. It preserves
Celestial's internal package names, commands, protocol namespace, and GNU
General Public License version 3 (GPLv3) notices while adding and documenting
the retained extensions used by this platform.

Celestial is described in “Celestial: Virtual Software System Testbeds for the
LEO Edge,” Middleware 2022, DOI
[10.1145/3528535.3531517](https://doi.org/10.1145/3528535.3531517).

Multiple configured ground stations were already supported by Celestial.
QUEST retains that capability together with later contact activation, antenna
scheduling, direct ground-station backhaul, validator, build, and runtime
fixes. Documentation distinguishes those facts rather than attributing all
functionality to QUEST.

## Learning Path

1. Read [Core Concepts](02-core-concepts.md).
2. Follow the [Quickstart](../../quickstart/README.md) once without modifying
   its known-good files.
3. Read [Development Environments](03-development-environments.md) and
   [Configuration](04-configuration.md).
4. Learn the [System Architecture](05-system-architecture.md) and
   [Startup Call Flow](06-startup-call-flow.md).
5. Follow the [Source-Code Reading Guide](07-source-code-reading-guide.md)
   with the repository open beside it.
6. Build a workload, test it, and design an experiment using chapters 8–10.
7. Use the [Glossary](11-glossary.md) and
   [technical reference](../reference/configuration.md) while working.

At a glance, the implementation path is:

```text
configuration → topology generation → contact selection → serialization
→ coordinator → gRPC → orchestrator → VM and network runtime
```
