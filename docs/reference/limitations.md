# Known Limitations

These are implementation constraints, not claims about what an ideal LEO
testbed could support.

| Component | Current limit or boundary | Source of boundary |
| --- | --- | --- |
| Python coordinator | one coordinator process | topology replay and fast update fan-out are centralized |
| Worker hosts | no fixed configured maximum | machines are assigned round-robin; physical resources dominate |
| Shells | 245 configuration entries | `celestial/config.py` validation |
| Satellites per shell | 16,384 | machine identifier and network allocation limits |
| vCPU, memory, storage | host-dependent | each active or suspended microVM consumes host resources |

Emulated latency cannot be lower than delay already present in the physical
host and any path between multiple workers.

## Privileged host effects

The worker creates TAP devices, WireGuard state, traffic-control/eBPF rules,
Firecracker processes, sparse overlays, and output files. Use only the clean
shared HPI host under the administrator's sudo policy, and coordinate one
Celestial experiment at a time. Do not run it on a personal or multi-purpose
server.

Large runs can reach process, file-descriptor, Address Resolution Protocol
(ARP) cache, memory, or swap limits. These are host-administration concerns.
Measure the requested scale and ask the HPI Scientific Compute Helpdesk to
review changes; student documentation must not silently modify global limits.

## Docker networking

The original Celestial documentation records that installing Docker on the
host can prevent Firecracker networking from working, and that uninstalling it
did not necessarily restore a clean network state. QUEST therefore builds with
Docker locally and runs the worker natively on a clean remote host.

## Suspended-machine memory

Satellites outside the active set are suspended, not destroyed, so their state
can resume later. Suspended Firecracker processes can retain allocated memory.
Long duration and large constellations must be sized against host RAM and the
administrator-provided swap policy.

## Model boundary

QUEST calculates orbits, visibility, routes, and link properties from its
configuration. A successful run demonstrates software behavior under that
model; it does not by itself validate antenna physics, atmospheric effects,
payload behavior, or the calibration of a real constellation.
