# 11. Glossary

**Activation.** The policy controlling whether a satellite microVM is active.
See [Core Concepts](02-core-concepts.md#time-and-state-terms).

**Antenna capacity.** A ground station's configured maximum simultaneous
selected direct contacts across all shells.

**Area of interest (AOI).** A geographic region relevant to a spatial query or
application; it is an application-level concept, not a built-in QUEST database
object.

**Backhaul.** A modeled direct terrestrial-style link between ground stations,
configured by bandwidth and path stretch.

**Bandwidth.** Link capacity expressed by QUEST in kilobits per second
(kbit/s).

**Bounding box.** Four coordinates delimiting a rectangular geographic region;
in `bbox` activation mode it selects active satellite subpoints.

**Constellation.** All configured satellite shells and ground stations.

**Contact.** A currently visible and, when antennas are limited, selected
direct ground-to-satellite link.

**Coordinator.** The Python `celestial.py` process that replays a topology
archive to one or more workers.

**Delay.** One-way modeled link propagation time, represented in microseconds
at the runtime interface.

**Domain Name System (DNS).** The guest naming service for `.celestial`
satellite and ground-station addresses.

**eBPF.** Extended Berkeley Packet Filter, the default worker backend used to
enforce bandwidth, delay, and blocked link state.

**Emulation.** Running real software in microVMs while imposing generated
machine and network state over wall-clock time.

**Elevation angle.** The angle from a ground station's horizon to a satellite;
contacts below `min_elevation` are excluded.

**Firecracker.** The virtual machine monitor used by the worker to run one
microVM per active node.

**gRPC.** The remote procedure call framework used for the coordinator-worker
protocol
generated from `proto/celestial/celestial.proto`.

**Ground station.** A fixed Earth location with an always-active microVM and
links to selected visible satellites.

**Guest.** The Linux environment inside a satellite or ground-station microVM.

**Guest kernel.** The `vmlinux` binary booted inside a microVM.

**Hypertext Transfer Protocol (HTTP) information API.** The read-only guest
service providing identity, constellation, active state, and path data.

**Inter-satellite link (ISL).** A modeled direct link between two satellites.

**Kernel-based Virtual Machine (KVM).** The Linux virtualization facility
required by Firecracker through `/dev/kvm`.

**Low-Earth Orbit (LEO).** An Earth orbit at relatively low altitude; QUEST
uses the altitude supplied for each shell.

**Machine ID.** A pair of numeric group/satellite identifiers plus an optional
ground-station name.

**Mebibyte (MiB).** 1,048,576 bytes; the unit for guest memory and maximum
writable-overlay size.

**MicroVM.** A minimal virtual machine optimized for lightweight isolated
applications.

**Network emulation (netem).** QUEST's alternate Linux traffic-control backend
selected with `-em-backend netem`.

**Orbital plane.** The geometric plane containing an orbit.

**Orbital shell.** Satellites sharing one set of altitude, inclination,
eccentricity, plane count, and spacing parameters.

**Orchestrator.** The Go component translating desired machine/link state into
virtualization and network operations.

**Overlay disk.** The per-machine writable ext4 filesystem placed above a
read-only root image.

**Path stretch.** A ratio at least 1.0 multiplying great-circle ground distance
before backhaul propagation delay is calculated.

**POSIX shell.** The common command-language subset used by the documentation
on Linux, macOS, and WSL2.

**Precision Time Protocol (PTP).** A clock-synchronization mechanism that can
expose host time to a KVM guest through `/dev/ptp0`.

**Root filesystem.** The read-only guest `.img` containing Linux, dependencies,
and `/app.sh`.

**Route.** The currently selected sequence of direct links between two
machines.

**Satellite node.** A modeled satellite identity and its microVM when active.

**SGP4.** Simplified General Perturbations 4, the orbit propagator used during
topology generation.

**Spatial application.** Software whose computation depends on location,
geometry, coverage, or spatial relationships.

**Suspend.** Pause a microVM while retaining its memory/state for later resume.

**Timestep.** One configured instant at which generated machine/link changes
can be applied.

**TOML.** Tom's Obvious Minimal Language, the human-readable configuration
format used by `satgen.py`.

**Topology archive.** The ZIP containing validated configuration, initial
machine descriptions, and time-indexed machine/link differences.

**Topology generation.** The offline orbit/contact/path calculation performed
by `satgen.py`.

**Worker.** The privileged Linux/amd64 `celestial.bin` runs on remote machine(host) process controlling
Firecracker and host networking.

**WSL2.** Windows Subsystem for Linux 2, the supported way to follow the common
POSIX local workflow on Windows.
