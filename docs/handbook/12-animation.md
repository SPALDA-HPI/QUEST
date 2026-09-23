# 12. Visualizing a Constellation

Animation is an optional, local preview of satellite motion and geometric
connectivity. You can use it before building or running any microVMs. It is
not a live monitor of the remote worker or a visualization of application
results.

**Important:** the current animation path does not implement all of QUEST's
topology-generation features. Read the limitations below before interpreting
satellite brightness or counting ground contacts.

## Prepare your local environment

Use a local desktop with a working graphical display. Run the following from
the QUEST repository root, where `animate.py` and `requirements.txt` live.
If you have not created a Python environment, follow
[Chapter 03](03-development-environments.md#python-virtual-environments)
first. Then, in your local terminal:

```sh
. .venv/bin/activate
python3 -m pip install -r requirements.txt -r requirements-animation.txt
python3 -c 'import vtk; print(vtk.vtkVersion.GetVTKVersion())'
```

The final command should print `9.3.0`, the VTK version pinned by the project.
VTK is the library that creates the interactive 3D window. This import check
does not test whether your graphical display works.

Animation needs neither Docker, Go, a guest kernel, root filesystem images,
KVM, nor sudo. The TOML configuration still needs valid compute fields to pass
configuration validation, but animation does not boot the named images.
Keep this on your workstation, not in the shared remote VM's SSH terminal.
WSL2 needs working GUI support; a command-line-only session is insufficient.

## Run the quickstart preview

From the repository root, in the same local terminal:

```sh
python3 animate.py quickstart/quickstart.toml
```

Pass the **TOML configuration**, not `quickstart.zip`. You do not need to run
`satgen.py` first: animation calculates positions itself. It neither creates
a topology ZIP nor reads the archive used by the remote coordinator.

The quickstart defines one shell of 32 satellites and two ground stations,
Potsdam and Berlin. Expect a separate window with a globe, satellite points,
ground-station points, and links. The nearby ground stations can look like a
single point at the initial zoom level; points on the far side of the opaque
Earth can be hidden. A sparse constellation need not have a visible ground
contact at every timestep.

The terminal prints `step 0`, `step 5`, and so on through `step 115` for this
configuration. These are modeled seconds, not satellite identifiers or
completed application tasks. Initial orbit/JIT compilation and graphics
setup can take time before the display becomes usable.

The viewer uses VTK's trackball-camera interaction. Drag with the left mouse
button to rotate the view and use the mouse wheel to zoom. Resizing the window
can help if the initial window is too large.

To stop, return to the terminal that launched the command and press `Ctrl+C`.
Do not rely on closing the window alone: the launcher and rendering process
can remain alive. At the end of the configured timeline, the launcher waits
for the renderer, so the window may remain open rather than exiting
automatically. If it does not stop, inspect and terminate animation process.

## Read the display

The following describes the display after a timestep update; initialization
can briefly show points or links before their updated state is applied.

| Display element | Meaning |
| --- | --- |
| Light-blue globe and black land shapes | Earth and geographic orientation |
| Colored satellite dots | Satellite positions; each shell receives a palette color |
| Opaque satellite dots | Satellite subpoints inside the configured `bbox` |
| Faded satellite dots | Satellite subpoints outside `bbox`, rendered at half opacity |
| Thin, shell-colored lines | Inter-satellite links marked `active` by the shell model; link colors are less saturated than satellite colors |
| Bright-green dots | Ground-station positions |
| Pale-green lines to satellites | Ground contacts returned by each shell's visibility/connection calculation |

The bounding box itself is not drawn. Satellite dots are screen markers, not
physical satellite sizes or observation footprints. Line widths and colors
are display settings, not measured latency or throughput. The implementation
does not provide an on-screen legend or an application-result overlay.

## Understand animation time

`resolution` is the number of modeled seconds between position/topology
updates. `duration` is the length of the modeled interval, and `offset` is its
starting time. The launcher steps from `offset` to less than
`offset + duration` in increments of `resolution`.

The launcher attempts roughly real-time pacing: five modeled seconds per
update means roughly five wall-clock seconds between updates when calculation
keeps up. Expensive calculations can make it fall behind. The renderer's
separate 7-millisecond timer does not add orbital samples or interpolate
positions. Increasing `resolution` makes updates coarser; it is not a playback
speed control. The initial scene is constructed at time zero before the
requested offset is applied.

## Limits when previewing QUEST features

The animation uses `AnimationConstellation`, whereas archive generation uses
`SatgenConstellation`. Sharing the configuration does **not** make their
outputs equivalent:

- **Contact-based activation:** animation constructs shells with their default
  bounding-box activation and colors points using `in_bbox`. It does not pass
  `satellite_activation` to those shells. With the quickstart's
  `ground_station_contact` policy, dot opacity must not be interpreted as the
  actual VM activation state.
- **Finite antennas and multiple shells:** animation steps shells separately
  without the shared `AntennaScheduler`. Its displayed ground contacts are
  not filtered by the global `antenna_number` limits and may exceed them.
  Changing an antenna count is therefore not a reliable visual experiment.
- **Ground-station backhaul:** the viewer draws satellite-to-satellite and
  ground-to-satellite lines, not direct ground-to-ground backhaul. No line
  between Potsdam and Berlin does not mean backhaul is disabled in emulation.
- **Application results:** animation does not run guests, read validator CSVs,
  show raster joins or sensor footprints, or measure traffic and latency.
  Use the [quickstart results workflow](../../quickstart/README.md#14-retrieve-and-analyse-the-results)
  for measured validator output.

Use the preview to understand orbital layout and geometric opportunities for
communication. Use the generated topology and the actual emulation's logs
and results to assess scheduling, VM activity, reachability, and performance.

## Explore other configurations

The [`animation/`](../../animation/) directory contains more example
constellations. For example, from the repository root:

```sh
python3 animate.py animation/iridium.toml
```

These are example model configurations, not verified descriptions of current
operational constellations. Inspect their `duration`, `resolution`, `planes`,
and `sats` before running them: some are much larger and longer than the
quickstart. Stop with `Ctrl+C` when you have seen enough.
## Troubleshooting and source pointers

- **`No module named vtk`:** activate the local `.venv` and install
  `requirements-animation.txt` with that environment's `python3 -m pip`.
- **No window or a graphics/display error:** check that you are on the local
  desktop, not an SSH-only or headless session. On WSL2, verify GUI support.
  A successful VTK import alone does not establish rendering support.
- **No ground links:** this can be a valid geometry/elevation outcome. Check
  the ground-station coordinates, `min_elevation`, orbital layout, and modeled
  time before interpreting it as a fault.
- **Faded dots despite visible contacts:** opacity follows `bbox`, not
  contact-based activation. See the limitations above.
- **The process stays alive after the final step:** the launcher waits for
  the rendering process; stop it from the launching terminal.

For source reading, follow
[`animate.py`](../../animate.py) →
[`AnimationConstellation` and `Animation`](../../celestial/animation.py) →
[`Shell`](../../celestial/shell.py). The launcher parses the configuration and
starts a separate renderer process. `AnimationConstellation` sends positions
and links over a multiprocessing pipe; `Animation` updates VTK actors.
