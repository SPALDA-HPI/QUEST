# 1. Project Overview

## Purpose

QUEST—**Querying and Understanding Earth across Space and Time**—is a platform for distributed spatial data
processing across Low-Earth Orbit (LEO) satellite constellations. It gives a common testbed in which satellite motion, intermittent
ground contact, constrained antennas, virtual machines, and changing network
paths can affect a distributed application.

The repository begins with a clean validator application rather than a completed
spatial database. Your project work should add a clearly scoped spatial
operator or application and measure it under documented assumptions.


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
Earth-observation data product, or calibrated model
of a specific commercial constellation. It also does not hide the experiment
environment: you must record the input configuration, code commit, host
conditions, application and dataset, and interpretation of each metric.



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
6. Build an application, test it, and design an experiment using chapters 8–10.
7. Use the [Glossary](11-glossary.md) and
   [technical reference](../reference/configuration.md) while working.


