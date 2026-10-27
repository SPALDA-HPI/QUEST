# 13. Guide for Local Observation Mapping

## 1. Code map

```text
QUEST/
├── quickstart/quickstart.toml      * Example configuration
├── satgen.py                       * Offline topology generator*
├── celestial/
│   ├── config.py                   * Configuration objects and validation
│   ├── sgp4_solver.py              * Orbit propagation
│   ├── shell.py                    * Positions and topology within one shell
│   ├── satgen_constellation.py     * Coordination across shells
│   ├── types.py                    Time, node IDs, and link types
│   ├── activation.py               Satellite VM activation
│   ├── antenna.py                  Ground-station antenna scheduling
│   ├── serializer.py               Topology serialization interfaces
└── └── zip_serializer.py           Topology archive reader and writer
```

Start with the Python models in `celestial/`.
### Core files reading order

| Order | Source | What to look for |
| --- | --- | --- |
|  1 | [quickstart.toml](../../quickstart/quickstart.toml) | Satellite count, orbital parameters, and simulation duration. |
| 2 | [satgen.py](../../satgen.py#L58) | The complete offline path from configuration to topology archive. |
| 3 | [config.py](../../celestial/config.py#L498): `Config`, `Shell`, `BoundingBox` | Validation, defaults, and the objects in `config.shells`. |
| 4 | [satgen_constellation.py](../../celestial/satgen_constellation.py#L35): `SatgenConstellation` | How all shells advance together and share ground-station antennas. |
| 5 | [shell.py](../../celestial/shell.py#L113): `Shell` | How positions, geographic bounds, and links are updated within one shell. |
| 6 | [sgp4_solver.py](../../celestial/sgp4_solver.py#L47): `SGP4Solver` | How `init_sat_array()` initializes positions and `set_time()` updates them. |



There are two classes named `Shell`: the one in `config.py` holds configuration;
the one in `shell.py` holds the evolving model state.

## 2. Execution flow

### Initialization

```text
quickstart.toml
    ↓ toml.load()
Config
    ↓ parse configuration
SatgenConstellation
    ↓ creates one model per configured shell
Shell
    ↓ init()
SGP4Solver
    ↓ init_sat_array()
Initial x, y, z values in satellites_array
```

### Each time step

Follow [SatgenConstellation.step()](../../celestial/satgen_constellation.py#L146)
and [Shell.prepare_step()](../../celestial/shell.py#L266):

```text
satgen.py time loop
    ↓ SatgenConstellation.step(t)
** Each Shell.prepare_step(t) **
    ├── SGP4Solver.set_time(...) → update satellite positions
    ├── Earth rotation and geographic checks → update in_bbox
    ├── Rotate ground-station positions
    └── Update inter-satellite links and candidate ground contacts
    ↓
AntennaScheduler.select(...) → select contacts across shells
    ↓
Each Shell.finish_step(...)
    ├── Filter contacts and determine VM activity
    └── Calculate paths and state differences
    ↓
ZipSerializer.diff_machine() / diff_link()
```

Satellite positions are available after `prepare_step()`. Antenna selection
and path calculation belong to the communication model.

`SGP4Solver` is the independent orbit-calculation interface. 
`Shell` adds
position-array access and topology state.
## 3. Concepts to understand before mapping
### Configuration and time

Read [quickstart.toml](../../quickstart/quickstart.toml) alongside the
[configuration schema](../../celestial/config.py#L255).

| Setting | Meaning |
| --- | --- |
| `planes`, `sats` | Orbital planes and satellites per plane. Their product is the satellite count in a shell. |
| `altitude_km`, `inclination` | Orbital altitude parameter and inclination. |
| `arc_of_ascending_nodes`, `eccentricity` | Ascending-node distribution and orbital eccentricity. |
| `offset` | Starting point on the orbit timeline, in seconds; defaults to `0`. |
| `duration` | Length of the simulated interval, in seconds. |
| `resolution` | Time between topology updates, in seconds. This is not image resolution. |
| `bbox` | `[lat1, lon1, lat2, lon2]`, used for geographic checks. |

The loop in [satgen.py](../../satgen.py#L84) starts at `offset`, advances by
`resolution`, and stops before `offset + duration`. The current quickstart has
32 satellites and 24 time steps: `0, 5, …, 115` seconds. These are topology
samples, not sensor acquisition events.

### Satellite identity

[Shell.__init__()](../../celestial/shell.py#L121) assigns IDs within each shell:

```python
unique_id = (plane * self.nodes_per_plane) + node
```

Satellite IDs start at `0` within each shell. `SatgenConstellation` assigns shell
groups starting at `1`; ground stations use group `0`. A satellite ID alone is
therefore not unique across the constellation.

`MachineID(group, id, name)` in `types.py` represents the full node identity.
Keep this meaning when designing the dataset's satellite identifiers.

### Position calculation and access

Read the three methods in [SGP4Solver](../../celestial/sgp4_solver.py#L47):

| Method | Behavior |
| --- | --- |
| `__init__()` | Stores orbital parameters and the time reference. |
| `init_sat_array()` | Creates the per-satellite SGP4 objects and fills the initial `x`, `y`, and `z` fields of a structured NumPy array. |
| `set_time(time, satellites_array)` | Computes positions at the requested time, updates the array in place, and returns it. |

For `set_time()`, the following statements are from this interface:

```python
fr = self.start_fr + (time / SECONDS_PER_DAY)
e, r, d = self.sgp4_solvers[sat_id].sgp4(self.start_jd, fr)
satellites_array[sat_id]["x"] = np.int32(r[0]) * 1000
```

Several details matter when using this interface:

- `time` is seconds from the solver's time reference, not an increment since
  the previous call. A requested time can be calculated directly.
- `START_TIME` is fixed at `2023-01-01T00:00:00+00:00`. And we can just use logical timestamps for our scenario simulation and observation mapping.
- `set_time()` mutates the supplied array. Distinguish a saved snapshot from another reference to that same array.
- The implementation truncates SGP4 coordinates in kilometers before multiplying
  by `1000`. Values are stored in meters but quantized in 1,000-meter steps. This may limit the geometric precision available to later mapping.

For `init_sat_array()`, it fills coordinates only. And `Shell.__init__()` initializes the
satellite IDs and other metadata in
[SATELLITE_DTYPE](../../celestial/shell.py#L39):

| Field | Meaning |
| --- | --- |
| `ID` | Satellite ID within the shell. |
| `plane_number`, `offset_number` | Orbital plane and position within that plane. |
| `x`, `y`, `z` | Three-dimensional position, stored in meters. |
| `in_bbox` | Geographic-bound flag under the current model. |

[Shell.get_sat_positions()](../../celestial/shell.py#L440) can return a copy of
`ID, x, y, z, in_bbox`.
### 

### Earth rotation and geographic checks

Read [prepare_step()](../../celestial/shell.py#L266),
[_get_rotation_matrix()](../../celestial/shell.py#L483), and
[_is_in_bbox()](../../celestial/shell.py#L503) together:

1. The solver updates satellite `x, y, z` coordinates.
2. The shell calculates Earth's rotation using a period of `86,400` seconds.
3. An inverse rotation is applied to satellite positions for latitude/longitude
   and bounding-box checks.
4. Ground stations are rotated forward from their initial positions for link
   calculations in the same coordinate frame.

`_init_ground_stations()` shows how geographic coordinates become initial
three-dimensional positions. `_is_in_bbox()` includes geographic-coordinate
calculations and handles bounding boxes that cross the antimeridian, but
**returns only a boolean**.

## 4. Your design work











### Implementation Workflow
The boundary between existing code and mapping is:

```text
Existing Celestial code:
           Constellation configuration + simulation time
                                 ↓
                 Satellite identities and positions
                                 ↓
           [Your design: observation coverage/footprint]
                                 │
Simulated wildfire from Task 1 ──┤
                                 ↓
            [Your design: spatial and temporal mapping]
                                 ↓
           [Your design: observation dataset generation]
```



### Key Questions

Develop and justify your own choices before implementation. No algorithm,
parameter values, or file format is prescribed here.

| Design topic | Question | Your design |
| --- | --- | --- |
| Fire-grid location | How do Task 1 grid locations correspond to Earth's surface? | __________ |
| Time alignment | How does fire-simulation time correspond to Celestial time? | __________ |
| Sensor footprint | What assumptions are needed beyond satellite position to define coverage? | __________ |
| Acquisition timing | How are produced observations relate to topology `resolution`? | __________ |
| Mapping | How is the content of a satellite observation determined from the fire simulation? | __________ |



