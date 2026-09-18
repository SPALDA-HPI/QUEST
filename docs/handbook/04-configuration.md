# 4. Configuration Walkthrough

Open [`quickstart/quickstart.toml`](../../quickstart/quickstart.toml) beside
this chapter. Tom's Obvious Minimal Language (TOML) uses `key = value`,
`[table]`, and repeated
`[[array-of-table]]` blocks.

## Activation and experiment region

```toml
satellite_activation = "ground_station_contact"
bbox = [35.0, -15.0, 65.0, 35.0]
resolution = 5
duration = 120
```

`ground_station_contact` means a satellite microVM runs only while a direct
contact has been selected. Selection occurs after visibility and antenna
limits are known. 

By contrast, `bbox` activates every satellite whose modeled
subpoint lies inside the geographic bounding box.
The bounding box is `[south latitude, west longitude, north latitude, east
longitude]` in degrees. 

A five-second resolution produces 24 update
intervals over 120 seconds.

An omitted `offset` defaults to zero. Offset changes the starting point along
the generated orbital timeline; it does not change wall-clock run duration.

## Global network defaults

```toml
[network_params]
bandwidth_kbits = 1_000_000
min_elevation = 25.0
ground_station_connection_type = "all"
ground_station_bandwidth_kbits = 1_000_000
ground_station_path_stretch = 1.3
```

`bandwidth_kbits` is one million kilobits per second for inter-satellite links
and, unless overridden, ground contacts. `min_elevation` excludes contacts
below 25 degrees.

`all` first exposes all visible contacts to the antenna scheduler. This is
required when `antenna_number` is configured; `one` would already restrict the
station to the nearest satellite per shell and conflicts with a separate
global antenna cap.

The last two fields enable direct ground-station backhaul. Bandwidth is in
kbit/s. Path stretch multiplies the ground great-circle distance before delay
is derived, approximating a terrestrial route that is longer than the
geodesic. Both fields must appear or both must be absent.

## Global microVM defaults

```toml
[compute_params]
vcpu_count = 1
mem_size_mib = 256
disk_size_mib = 1
kernel = "vmlinux-5.12.bin"
rootfs = "server.img"
```

Every satellite node initially inherits one virtual CPU, 256 mebibytes (MiB) of
memory, a sparse writable overlay with a one-MiB maximum, and the named guest
kernel/root filesystem. The worker resolves the two filenames below
`/celestial`.

The root image is read-only. `disk_size_mib` sizes the per-machine writable
overlay rather than changing that image.

## Orbital shell

```toml
[[shell]]
planes = 4
sats = 8
altitude_km = 550
inclination = 53.0
arc_of_ascending_nodes = 360.0
eccentricity = 0.0
```

Four planes times eight satellites create 32 nodes. Altitude is kilometers
above the modeled Earth radius. Inclination is the angle to the equatorial
plane. A 360-degree ascending-node arc spreads planes around the Earth.
Eccentricity zero gives circular orbits.

## Potsdam ground station and override

```toml
[[ground_station]]
name = "potsdam"
lat = 52.3906
long = 13.0645
antenna_number = 2

[ground_station.compute_params]
vcpu_count = 1
mem_size_mib = 512
disk_size_mib = 2
rootfs = "validator.img"
```

Potsdam is fixed at the given latitude/longitude. At most two direct satellite
contacts can be selected across all shells. Its compute override inherits the
global kernel but replaces memory, overlay size, and root image so the
validator workload runs there.

## Berlin ground station

```toml
[[ground_station]]
name = "berlin"
lat = 52.5200
long = 13.4050
antenna_number = 1
```

Berlin creates a second, always-active ground-station microVM and inherits the
global server image. Its single antenna permits one selected direct satellite
contact.
## Inheritance model

The effective value is built from global defaults and then a local override:

```text
global network/compute table → shell or ground-station table → typed object
```

An override need contain only changed keys. Direct backhaul is global and is
not a local override.

The [complete configuration reference](../reference/configuration.md) lists
types, units, enforced limits, and the places where physical recommendations
are stricter than code validation.

## Checkpoint

Predict which fields Potsdam inherits, which it overrides, and
what must change before `antenna_number` can be combined with connection type
`one` (answer: remove the antenna field or use `all`).
