# 3. Development Environments

QUEST crosses three environments. So executing a
correct command in the wrong one will induce errors.

## Local workstation

Your local Linux, macOS, or Windows Subsystem for Linux 2 (WSL2) shell holds a
checkout, editor, Python environment, and Docker installation. It builds
the Linux/amd64 `celestial.bin` worker and guest root filesystems, downloads
the supplied Linux 5.12 guest kernel, generates topology archives, and runs
unit tests.

<ins>Docker is appropriate here</ins> because these container networks are
separate from the clean Celestial runtime host.

## Remote VM

The remote VM should run in a Linux/amd64 environment. It receives the worker,
guest kernel, and root filesystem images built or downloaded locally, then
runs the worker and the Python coordinator in separate terminals.

Always use the assigned name through a variable:

```sh
REMOTE_HOST="<your assigned host>"
ssh "$REMOTE_HOST"
```

Do not install or run Docker remotely; its host
bridges and firewall state can conflict with Celestial networking.

The worker changes host networking and starts Firecracker with elevated
privileges. Coordinate one experiment at a time because the worker's host
networking, port, and `/celestial` state are shared.

## Guest microVM

A guest is the execution environment for a satellite or ground-station
application. It has its own `eth0`, DNS, gateway information service, read-only
root filesystem, and writable overlay. It does not contain the QUEST source
checkout unless you explicitly put source into the root image.

`builder/ceinit` prepares the guest, and the image's `/app.sh` starts the
application. Debugging a guest therefore begins with its host-side output under
`/celestial/out`, not with the coordinator terminal alone.

## POSIX shell essentials

QUEST documentation uses Portable Operating System Interface (POSIX) shell
syntax:

```sh
pwd                       # print the current directory
cd QUEST                  # enter the repository
ls -la                    # list files, including hidden ones
command -v python3        # show whether a command is available
NAME="value"              # set a shell variable
printf '%s\n' "$NAME"    # read it safely
```

Quotes preserve spaces and special characters. A line ending in `\` continues
one command. Do not include the explanatory `$` prompt symbols sometimes shown
in external tutorials.

## Python virtual environments

Use Python **3.11**, matching CI and `setup.cfg`. Check
`python3.11 --version` first; an unversioned `python3` may select the macOS
system Python or a different installed release. On macOS with Homebrew,
`brew install python@3.11` installs the required interpreter. On Linux, use
your distribution's Python 3.11 and venv packages.

Create one environment per checkout:

```sh
python3.11 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements.txt
```

Activation changes command lookup for the current shell only. Run `deactivate`
or close the terminal to leave it. `.venv/` is ignored and must not be copied
into a commit or guest image.

For local source development, also install the development dependencies:

```sh
python3 -m pip install -r requirements-dev.txt
```

This includes the existing core, animation, and quickstart requirements, plus
SciPy for `celestial/fw_test.py`, Requests for inspecting validator scripts,
and type stubs matching pandas 2.1 and protobuf 4.24. It does not replace the packages
installed inside guest images. Keep `mypy==1.9.0` as pinned in the core list.

## Go toolchain

`go.mod` declares the module and `toolchain go1.22.1`. The normal workflow
uses the pinned Go toolchain inside `compile.Dockerfile`. From the local
repository root, build the Linux/amd64 worker with:

```sh
./celestial-make celestial.bin
test -x celestial.bin
```

The wrapper first builds the `celestial-make` image, mounts the checkout at
`/celestial`, and runs the named Make target in a Linux/amd64 container. A
local Go installation is useful for source navigation and focused development,
but it is not required for this container build.

## Docker and generated artifacts

Local Docker builds three kinds of artifacts or tools:

- `celestial-make`: pinned toolchain that produces `celestial.bin`;
- `rootfsbuilder`: guest filesystem builder;
- `satgen-docker`: optional isolated topology generator.

Generate topology archives from the local Python environment:

```sh
. .venv/bin/activate
python3 satgen.py INPUT.toml OUTPUT.zip
```

The original Celestial setup also provides a Docker alternative. It produces
the same kind of archive and is useful when you want dependency isolation:

```sh
make satgen-docker
docker run --rm \
    -v "$(pwd)":/app \
    satgen-docker \
    /app/INPUT.toml \
    /app/OUTPUT.zip
```

## Preflight and privilege boundary

Run [`quickstart/preflight.sh`](../../quickstart/preflight.sh) remotely before
the first experiment. It reads the operating system, architecture, command
availability, Docker presence, KVM device access, and default interface. It
does not install, delete, or reconfigure anything.


## Checkpoint

For each file below, name the environment that creates it:
`quickstart/quickstart.zip`, `kernel/vmlinux-5.12.bin`,
`/celestial/cegst-potsdam.ext4`, and `quickstart/graphs/results_scatter.png`.
