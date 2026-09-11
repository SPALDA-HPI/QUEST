# Configuration Reference

QUEST reads a [TOML](https://toml.io/) document in `satgen.py` and validates it
with `celestial/config.py`. The same validated `Config` object is stored in the
generated topology archive, so the coordinator replays the configuration that
produced the archive.

For a commented runnable file, start with
[`quickstart/quickstart.toml`](../../quickstart/quickstart.toml).

## Top-level fields

| Field | Type and unit | Required | Code-enforced contract |
| --- | --- | --- | --- |
| `bbox` | four floats, degrees | yes | `[south, west, north, east]`; latitudes -90..90 and longitudes -180..180 |
| `resolution` | integer seconds | yes | 1..10,000,000,000; interval between topology updates |
| `duration` | integer seconds | yes | 30..10,000,000,000; generated experiment duration |
| `offset` | integer seconds | no | non-negative; defaults to `0` |
| `satellite_activation` | string | no | `"bbox"` or `"ground_station_contact"`; defaults to `"bbox"` |
| `network_params` | table | yes | complete global network defaults |
| `compute_params` | table | yes | complete global microVM defaults |
| `[[shell]]` | array of tables | yes | 1..245 shell definitions |
| `[[ground_station]]` | array of tables | no | defaults to an empty list |

`bbox` is always generated for position output. With `satellite_activation =
"bbox"`, it also decides which satellite microVMs are active. With
`"ground_station_contact"`, a satellite is active only while the antenna
scheduler selects at least one direct ground-station contact; at least one
ground station is then required.

```toml
satellite_activation = "ground_station_contact"
bbox = [35.0, -15.0, 65.0, 35.0]
resolution = 5
duration = 120
offset = 0
```

## Network parameters

The global `[network_params]` table requires the first three fields below.
Shell and ground-station override tables may contain only the fields they
change and inherit the rest.

| Field | Type and unit | Constraint | Effect |
| --- | --- | --- | --- |
| `bandwidth_kbits` | integer kbit/s | at least 0 | inter-satellite bandwidth globally or contact bandwidth in a ground-station override |
| `min_elevation` | float degrees | at least 0 | minimum ground-to-satellite elevation used when finding visible contacts |
| `ground_station_connection_type` | string | `"all"` or `"one"` | all visible satellites, or the nearest visible satellite per shell |
| `ground_station_bandwidth_kbits` | integer kbit/s | at least 1; global only | bandwidth of each direct ground-station backhaul link |
| `ground_station_path_stretch` | float ratio | finite and at least 1.0; global only | multiplies great-circle distance before converting it to backhaul delay |

The two backhaul fields are optional but must be supplied together. Omitting
both emits no direct ground-station pair links.

```toml
[network_params]
bandwidth_kbits = 1_000_000
min_elevation = 25.0
ground_station_connection_type = "all"
ground_station_bandwidth_kbits = 1_000_000
ground_station_path_stretch = 1.3
```

The validator does not enforce a maximum elevation of 90 degrees; 0..90 is the
physically meaningful range. This distinction is important when separating a
source-code fact from a modeling recommendation.

## Compute parameters

Global `[compute_params]` supplies defaults for every satellite and ground
station. `[shell.compute_params]` and `[ground_station.compute_params]`
override individual values.

| Field | Type and unit | Global requirement | Meaning |
| --- | --- | --- | --- |
| `vcpu_count` | integer vCPUs | required | virtual CPUs assigned to an active microVM |
| `mem_size_mib` | integer MiB | required, at least 1 | guest memory |
| `disk_size_mib` | integer MiB | required, at least 1 | maximum sparse writable-overlay size |
| `kernel` | non-empty string | required | guest kernel filename under `/celestial` on the worker |
| `rootfs` | non-empty string | required | read-only root filesystem filename under `/celestial` |
| `boot_parameters` | list of strings | optional | additional kernel arguments; defaults to `[]` |

The schema currently checks only that `vcpu_count` is an integer; choose a
positive value supported by the host.

```toml
[compute_params]
vcpu_count = 1
mem_size_mib = 256
disk_size_mib = 1
kernel = "vmlinux-5.12.bin"
rootfs = "server.img"
boot_parameters = []
```

Do not repeat built-in worker parameters such as `console=ttyS0`, `reboot=k`,
`panic=1`, `pci=off`, `tsc=reliable`, `quiet`, `ipv6.disable=1`,
`overlay_root=vdb`, or the IP/root/device arguments supplied by Firecracker.

## Shell definitions

Each `[[shell]]` describes a symmetric orbital shell.

| Field | Type and unit | Constraint | Meaning |
| --- | --- | --- | --- |
| `planes` | integer | at least 1 | number of orbital planes |
| `sats` | integer | at least 1 | satellites per plane |
| `altitude_km` | integer km | at least 0 | height above the modeled Earth radius |
| `inclination` | float degrees | 0..360 | angle between orbital and equatorial planes |
| `arc_of_ascending_nodes` | float degrees | no code range | arc over which plane ascending nodes are distributed |
| `eccentricity` | float | no code range | orbital eccentricity passed to the propagator |

`planes * sats` may not exceed 16,384 for one shell. A circular Low-Earth
Orbit (LEO) model normally uses `eccentricity = 0.0`; the validator does not
enforce the physically usual 0..1 interval.

```toml
[[shell]]
planes = 4
sats = 8
altitude_km = 550
inclination = 53.0
arc_of_ascending_nodes = 360.0
eccentricity = 0.0

[shell.network_params]
bandwidth_kbits = 2_000_000

[shell.compute_params]
mem_size_mib = 512
```

The shell network override affects inter-satellite links. Compute overrides
affect every satellite in that shell.

## Ground-station definitions

Every `[[ground_station]]` creates one always-active ground-station microVM.
Names must be unique, non-empty, and contain only letters, digits, or hyphens.

| Field | Type and unit | Constraint | Meaning |
| --- | --- | --- | --- |
| `name` | string | required and unique | stable identifier used in logs, DNS, and the information API |
| `lat` | float degrees | -90..90 | latitude |
| `long` | float degrees | -180..180 | longitude |
| `antenna_number` | integer antennas | optional, at least 1 | maximum simultaneous selected direct satellite contacts across all shells |
| `network_params` | table | optional | partial ground-contact network override |
| `compute_params` | table | optional | partial microVM override |

If `antenna_number` is present, the effective
`ground_station_connection_type` must be `"all"`. The scheduler then chooses
up to that many contacts fairly; each selected contact retains the complete
`bandwidth_kbits` value.

```toml
[[ground_station]]
name = "potsdam"
lat = 52.3906
long = 13.0645
antenna_number = 2

[ground_station.compute_params]
mem_size_mib = 512
disk_size_mib = 2
rootfs = "validator.img"
```

Add another `[[ground_station]]` block to model another site. Multiple
ground-station definitions are an existing Celestial capability retained by
QUEST; antenna scheduling, contact activation, and direct backhaul are the
extensions demonstrated by the quickstart.

## Inheritance order

`Config` validates the input, fills defaults, then constructs typed objects.
For network and compute values, the order is:

```text
global table → shell or ground-station override → typed configuration
```

An override changes only named fields. Backhaul remains global and cannot be
placed in a shell or ground-station network override.

## Validate and generate

The normal validation path is topology generation:

```sh
. .venv/bin/activate
python3 satgen.py INPUT.toml OUTPUT.zip
```

Invalid TOML syntax fails while loading. A valid TOML document can still fail
the QUEST schema or cross-field checks. A successful parse is not evidence
that the orbital or network assumptions are physically realistic.
