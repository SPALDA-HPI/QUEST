# 3. Development Environments

QUEST crosses three environments. So executing a
correct command in the wrong one will induce errors.

## Local workstation

Your local Linux, macOS, or Windows Subsystem for Linux 2 (WSL2) shell holds a
checkout, editor, Python environment, and Docker installation. It builds
Linux/amd64 guest root filesystems and the guest kernel. It can also generate
topologies and run unit tests, but it does not run the privileged worker on
macOS or Windows.

<ins>Docker is appropriate here</ins> because these container networks are separate from
the clean Celestial runtime host.

## Remote VM

The remote VM should run in a Linux/amd64 environment. It builds `celestial.bin` with Go, generates the quickstart topology
with Python, and runs the worker and coordinator in separate terminals.

Always use the assigned name through a variable:

```sh
REMOTE_HOST="<your assigned host>"
ssh "$REMOTE_HOST"
```

The HPI Scientific Compute Helpdesk supplies remote access, sudo policy, and a
working KVM configuration. Students maintain the repository-level Go, Python,
and virtual-environment setup. Do not install or run Docker remotely; its host
bridges and firewall state can conflict with Celestial networking.

The worker changes host networking and starts Firecracker with elevated
privileges. Coordinate one experiment at a time because the worker's host
networking, port, and `/celestial` state are shared. Do not run it on a personal
or unrelated server.

## Guest microVM

A guest is the machine seen by a satellite or ground-station workload. It has
its own `eth0`, DNS, gateway information service, read-only root filesystem,
and writable overlay. It does not contain the QUEST source checkout unless you
explicitly put source into the root image.

`builder/ceinit` prepares the guest, and the image's `/app.sh` starts the
workload. Debugging a guest therefore begins with its host-side output under
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

In VS Code, open the QUEST directory and run **Python: Select Interpreter**
from the Command Palette. Choose `.venv/bin/python` (Python 3.11). If you
recreated an environment, run **Developer: Reload Window** to refresh the
language server. Activating a terminal does not necessarily change the
interpreter used by the editor. Verify it with:

```sh
python3 -c 'import sys; print(sys.version); print(sys.executable)'
python3 -m pip check
```

`pyrightconfig.json` configures Pylance/Pyright basic checking for Python 3.11
and the local `.venv`. Its extra import path mirrors the existing runtime
path setup in `proto/celestial/__init__.py`. Diagnostics inside the four
generated protobuf/gRPC binding files are ignored because their pinned
generators emit constructs incompatible with newer Pyright checks; their
types remain available to callers. Handwritten source and tests remain
checked. Do not edit generated files to remove editor warnings.

## Go toolchain

`go.mod` declares the module and `toolchain go1.22.1`. Confirm the effective
tool before building:

```sh
go version
make celestial.bin
```

The worker has Linux-specific source and requires amd64. Build it natively on
the remote VM, or use the local compile container for code checks.

## Docker and generated artifacts

Local Docker builds three kinds of artifacts:

- `celestial-make`: compile and protobuf toolchain;
- `rootfsbuilder`: guest filesystem builder;
- `kernelbuilder`: guest kernel builder.

Images, kernels, binaries, and topology ZIPs are reproducible outputs and are
ignored. Source code, Dockerfiles, shell scripts, kernel configs, and TOML are
tracked inputs.

## Preflight and privilege boundary

Run [`quickstart/preflight.sh`](../../quickstart/preflight.sh) remotely before
the first experiment. It reads the operating system, architecture, command
availability, Docker presence, KVM device access, and default interface. It
does not install, delete, or reconfigure anything.

Treat an error as evidence, not an invitation to guess. Students can repair
their own repository environment; host KVM, sudo, and network-policy problems
go to the administrator with the exact output.

Checkpoint: for each file below, name the environment that creates it:
`quickstart/quickstart.zip`, `kernel/vmlinux-5.12.bin`,
`/celestial/cegst-potsdam.ext4`, and `quickstart/graphs/results_scatter.png`.
