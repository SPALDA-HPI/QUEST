# Runtime Networking

Each guest has one `eth0` interface in a dedicated `/30` subnet. The address
space is derived from `10.0.0.0/8`:

1. first octet: `10`;
2. second octet: shell ID, with `0` reserved for ground stations;
3. third and fourth octets: bits of the satellite or ground-station ID;
4. subnet address + 1: guest gateway;
5. subnet address + 2: guest address.

The gateway provides DNS and the HTTP information service. Applications should
use `.celestial` names instead of embedding derived addresses.

## Link state

`satgen.py` produces paths and time-indexed link differences. At each
coordinator timestep, the worker blocks or unblocks links and updates delay and
bandwidth. The default backend uses eBPF; `-em-backend netem` selects Linux
network emulation instead.

Inter-satellite link bandwidth comes from a shell's effective
`bandwidth_kbits`. Direct ground contacts use the ground station's effective
network values. Optional direct ground-station backhaul uses the paired global
backhaul configuration.

## Multiple workers

When several workers are supplied to `celestial.py`, machines are assigned
round-robin. `pkg/peer` links hosts with WireGuard so a path may cross the
physical network. The quickstart deliberately uses one worker and loopback to
remove physical inter-host latency from the beginner run.

## Host boundary

The worker creates TAP devices and host packet-processing rules with elevated
privileges. Docker-created bridges and firewall rules can conflict with this
setup, so Docker is local-build-only and must not be installed or run on the
remote Celestial host.
