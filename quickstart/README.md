# QUEST Quickstart

This tutorial takes you from a clean checkout to one short QUEST emulation.
It assumes no prior experience with Go, Python virtual environments,
containers, Firecracker, or Celestial. Read each checkpoint before continuing.

## What You Will Do

You will use two environments:

- your local workstation builds the guest kernel and root filesystem images
  with Docker;
- one HPI Linux virtual machine builds and runs the Celestial worker,
  generates the topology, and runs the Python coordinator.

The example contains 32 satellites and two ground stations. It demonstrates
contact-based activation, finite antenna counts, multiple ground stations, and
direct ground-station backhaul. The run lasts 120 seconds and records the
difference between emulated ping latency and the latency reported by
Celestial's information service.

## Before You Begin

Ask the HPI Scientific Compute Helpdesk for access to the clean Linux virtual
machine shared by the student cohort. The administrator supplies the sudo
policy and a working `/dev/kvm` configuration. Do not guess the machine name:
use only the name the administrator assigns to you.

Coordinate an exclusive experiment time with the other students. Separate
home-directory checkouts are safe, but the worker uses shared host networking,
TCP port 1969, and `/celestial`, so two Celestial experiments must not run at
the same time.

You manage the project-level tools: Git, a POSIX-compatible shell, Go, Python,
and the Python virtual environment. Docker belongs on the local workstation
only. Do not install or run Docker on the remote VM; host Docker networking can
interfere with Celestial's Firecracker networking.

The worker is built for Linux on x86-64/amd64. A macOS or Windows computer can
still be the local build machine because Docker builds Linux/amd64 guest
artifacts. On Windows, use Windows Subsystem for Linux 2 (WSL2) and run the same
POSIX commands shown here. Native PowerShell commands are outside this guide.

You need:

- local: Git, a POSIX shell, Python 3.11, `make`, `ssh`, `scp`, and Docker;
- remote: Linux/amd64, Git, a POSIX shell, Go 1.22.1 or compatible, Python 3.11,
  `make`, Firecracker, WireGuard tools, `ip`, `iptables`, `tc`, and KVM access;
- GitHub access to `hzhang4433/QUEST` while the repository is private.

## Local and Remote Commands

Every command block is labelled `[LOCAL]` or `[REMOTE]`.

- `[LOCAL]` means your workstation or WSL2 shell.
- `[REMOTE]` means a shell opened on the HPI VM.

In a `[LOCAL]` shell, define the remote name exactly once:

**[LOCAL]**

```sh
REMOTE_HOST="<your assigned host>"
```

Replace the angle-bracket text with the hostname supplied to you. Do not copy
an example hostname from another student. The variable exists only in that
terminal; define it again after opening a new terminal.

Shell reminders:

- `cd PATH` changes the current directory.
- `pwd` prints the current directory.
- `.` followed by a filename loads environment settings into the current
  shell; `. .venv/bin/activate` activates the Python environment.
- `Ctrl+C` asks a foreground program to stop.
- Lines ending in `\` continue as one command on the next line.

## Quickstart File Layout

The tracked files are:

```text
quickstart/
├── README.md                 this tutorial
├── preflight.sh              read-only remote prerequisite check
├── quickstart.toml           constellation and microVM configuration
├── requirements.txt          local result-analysis packages
├── check_validator.py        converts validator CSV data into graphs
└── validator/
    ├── server.sh             long-running satellite workload
    ├── validator-base.sh     installs validator dependencies in its image
    ├── validator.py          compares reported and measured latency
    └── validator.sh          starts validator.py inside the ground station
```

The following files are generated and intentionally ignored by Git:

- `quickstart/quickstart.zip`: serialized topology and timed state changes;
- `quickstart/validator/server.img`: satellite root filesystem;
- `quickstart/validator/validator.img`: validator root filesystem;
- `kernel/vmlinux-5.12.bin`: guest Linux kernel;
- `quickstart/results-potsdam.csv` and `quickstart/graphs/`: results.

## 1. Clone QUEST

Clone the repository on the local workstation. SSH cloning is shown; use the
GitHub method configured for your account.

**[LOCAL]**

```sh
git clone git@github.com:hzhang4433/QUEST.git
cd QUEST
pwd
```

Checkpoint: `pwd` ends in `/QUEST` and `test -f quickstart/quickstart.toml`
returns without an error.

Clone the same commit on the remote VM.

**[LOCAL]**

```sh
ssh "$REMOTE_HOST"
```

**[REMOTE]**

```sh
git clone git@github.com:hzhang4433/QUEST.git
cd QUEST
git rev-parse HEAD
```

Keep the printed commit ID. The local and remote checkouts should use the same
commit for a reproducible run.

## 2. Prepare the Local Workstation

Check the local tools from the repository root.

**[LOCAL]**

```sh
git --version
python3.11 --version
make --version
docker version
```

Create a Python virtual environment. A virtual environment keeps this
project's Python packages separate from system Python. Use Python 3.11,
matching CI; see the [environment guide](../docs/handbook/03-development-environments.md#python-virtual-environments)
for installation and VS Code interpreter selection.

**[LOCAL]**

```sh
python3.11 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements.txt
```

The shell prompt often gains a `(.venv)` prefix. Confirm that Python now comes
from the repository:

**[LOCAL]**

```sh
python3 -c 'import sys; print(sys.executable)'
```

Checkpoint: the path contains `QUEST/.venv/`.

## 3. Prepare the HPI Remote VM

First inspect the operating system; do not assume a distribution.

**[REMOTE]**

```sh
cat /etc/os-release
uname -m
```

The architecture must be `x86_64` or `amd64`. On Debian or Ubuntu, the
following installs the basic project and networking commands if the Helpdesk's
sudo policy permits it:

**[REMOTE]**

```sh
sudo apt-get update
sudo apt-get install -y git make python3 python3-venv curl tar wireguard-tools iproute2 iptables
```

For another distribution, ask the administrator for equivalent package names.
Do not paste Debian commands into an unrelated system.

The repository declares Go 1.22.1. If `go version` is missing or older, install
Go in your home directory without replacing a system installation:

**[REMOTE]**

```sh
GO_VERSION="1.22.1"
curl -fLO "https://go.dev/dl/go${GO_VERSION}.linux-amd64.tar.gz"
mkdir -p "$HOME/.local"
tar -C "$HOME/.local" -xzf "go${GO_VERSION}.linux-amd64.tar.gz"
export PATH="$HOME/.local/go/bin:$HOME/.local/bin:$PATH"
go version
```

Use the same `PATH` export in each new remote shell, or add it to the startup
file for the shell you actually use.

The original Celestial workflow uses Firecracker 1.6.0. If the administrator
has not already installed it, place it in your user path:

**[REMOTE]**

```sh
FIRECRACKER_VERSION="1.6.0"
curl -fLO "https://github.com/firecracker-microvm/firecracker/releases/download/v${FIRECRACKER_VERSION}/firecracker-v${FIRECRACKER_VERSION}-x86_64.tgz"
tar -xzf "firecracker-v${FIRECRACKER_VERSION}-x86_64.tgz"
mkdir -p "$HOME/.local/bin"
install -m 0755 \
    "release-v${FIRECRACKER_VERSION}-x86_64/firecracker-v${FIRECRACKER_VERSION}-x86_64" \
    "$HOME/.local/bin/firecracker"
export PATH="$HOME/.local/go/bin:$HOME/.local/bin:$PATH"
firecracker --version
```

Do not install Docker here. Do not change KVM ownership, kernel modules,
network interfaces, or sudo configuration yourself; report those host-level
problems to the Helpdesk.

## 4. Check the Remote VM

The preflight script only reads host state. It does not install packages or
change networking.

**[REMOTE]**

```sh
cd QUEST
./quickstart/preflight.sh
```

Every line should begin with `OK:` or `INFO:`. An `ERROR:` line is a stop
condition. In particular, contact the Helpdesk if `/dev/kvm` is missing or not
readable/writable. If Docker is detected, do not uninstall it or repair the
network: ask for a clean Celestial host.

## 5. Build Guest Images Locally

The images are small Linux filesystems used *inside* Firecracker microVMs.
Docker only constructs them; Docker is not the experiment runtime.

Build the existing image-builder container:

**[LOCAL]**

```sh
cd QUEST
make rootfsbuilder
cd quickstart/validator
```

Build the validator ground-station image:

**[LOCAL]**

```sh
docker run --rm \
    --platform linux/amd64 \
    --privileged \
    -v "$(pwd)/validator.py":/files/validator.py \
    -v "$(pwd)/validator.sh":/app.sh \
    -v "$(pwd)/validator-base.sh":/base.sh \
    -v "$(pwd)":/opt/code \
    rootfsbuilder validator.img
```

Build the satellite server image:

**[LOCAL]**

```sh
docker run --rm \
    --platform linux/amd64 \
    --privileged \
    -v "$(pwd)/server.sh":/app.sh \
    -v "$(pwd)":/opt/code \
    rootfsbuilder server.img
cd ../..
```

Checkpoint:

**[LOCAL]**

```sh
test -s quickstart/validator/validator.img
test -s quickstart/validator/server.img
```

## 6. Build the Guest Kernel Locally

The repository contains a known kernel configuration. Building it downloads
Linux source in a local container and can take several minutes.

**[LOCAL]**

```sh
make -C kernel vmlinux-5.12.bin
test -s kernel/vmlinux-5.12.bin
```

The resulting kernel is for the guest microVM, not for your workstation or the
remote host operating system.

## 7. Build QUEST on the Remote VM

Create the remote Python environment and build the Linux worker natively.

**[REMOTE]**

```sh
cd QUEST
export PATH="$HOME/.local/go/bin:$HOME/.local/bin:$PATH"
python3.11 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements.txt
go version
make celestial.bin
test -x celestial.bin
```

`celestial.bin` is the privileged worker. `satgen.py` and `celestial.py` are
Python entry points for topology generation and coordination.

## 8. Transfer Guest Artifacts

Return to a local shell in the repository root. Copy exactly three generated
guest artifacts to the remote home directory.

**[LOCAL]**

```sh
scp kernel/vmlinux-5.12.bin "$REMOTE_HOST:"
scp quickstart/validator/server.img "$REMOTE_HOST:"
scp quickstart/validator/validator.img "$REMOTE_HOST:"
```

Install them in the worker's fixed artifact directory. `sudo install -d`
creates the directory; each following command copies one read-only input with
ordinary file permissions.

**[REMOTE]**

```sh
sudo install -d -m 0755 /celestial
sudo install -m 0644 "$HOME/vmlinux-5.12.bin" /celestial/vmlinux-5.12.bin
sudo install -m 0644 "$HOME/server.img" /celestial/server.img
sudo install -m 0644 "$HOME/validator.img" /celestial/validator.img
ls -lh /celestial/vmlinux-5.12.bin /celestial/server.img /celestial/validator.img
```

Do not copy the topology ZIP into `/celestial`; the coordinator reads it from
the repository.

## 9. Generate the Topology

The TOML file is human-readable input. `satgen.py` calculates positions,
contacts, routes, VM states, and link properties, then stores timed differences
in a ZIP archive.

**[REMOTE]**

```sh
cd QUEST
. .venv/bin/activate
python3 satgen.py quickstart/quickstart.toml quickstart/quickstart.zip
test -s quickstart/quickstart.zip
```

Checkpoint: generation reaches `100%` and prints `Output written to
quickstart/quickstart`.

## 10. Start the Worker

Open remote terminal 1 and keep it open. Determine the actual default network
interface instead of assuming a name.

**[REMOTE, terminal 1]**

```sh
cd QUEST
CELESTIAL_IFACE="$(ip route show default | awk 'NR == 1 { print $5 }')"
printf 'Using interface: %s\n' "$CELESTIAL_IFACE"
sudo ./celestial.bin -debug -network-interface "$CELESTIAL_IFACE"
```

Checkpoint: the worker prints `Celestial started!` and listens on TCP port
1969. Leave this command running.

## 11. Start the Coordinator

Open remote terminal 2. Because the coordinator and worker run on the same VM,
the worker address is the loopback address `127.0.0.1`. It is not the remote
hostname and must not be replaced with another student's address.

**[REMOTE, terminal 2]**

```sh
cd QUEST
. .venv/bin/activate
python3 celestial.py quickstart/quickstart.zip 127.0.0.1
```

The coordinator registers the worker, initializes all machines, and applies a
new topology state every five seconds. The first microVM starts may take much
longer than later updates.

## 12. Observe the Experiment

Open remote terminal 3 if available. Ground-station and satellite console
streams are written below `/celestial/out`.

**[REMOTE, terminal 3]**

```sh
tail -f /celestial/out/gst-potsdam.out
```

The validator reports active satellites and latency comparisons. To inspect a
satellite, first list available output files:

**[REMOTE, terminal 3]**

```sh
find /celestial/out -type f -name '[0-9]*-*.out' -print
```

Then run `tail -f` on one path printed by `find`. Press `Ctrl+C` to stop
`tail`; this does not stop the experiment.

## 13. Stop the Experiment

The coordinator stops automatically after 120 seconds. Wait for terminal 2 to
print `finished`. To stop early, press `Ctrl+C` in terminal 2 and wait for the
same message. The coordinator asks the worker to stop all microVMs.

After the coordinator finishes, press `Ctrl+C` once in terminal 1 and wait for
the worker process to exit. Do not mount an overlay while its microVM or worker
is still using it.

## 14. Retrieve and Analyse the Results

The Potsdam validator writes `/root/validator.csv` inside its writable overlay.
Mount that overlay read-only after shutdown and copy the file out.

**[REMOTE]**

```sh
MOUNT_DIR="$(mktemp -d)"
sudo mount -o loop,ro /celestial/cegst-potsdam.ext4 "$MOUNT_DIR"
sudo install -m 0644 "$MOUNT_DIR/root/validator.csv" "$HOME/quest-validator.csv"
sudo umount "$MOUNT_DIR"
rmdir "$MOUNT_DIR"
sudo chown "$(id -u):$(id -g)" "$HOME/quest-validator.csv"
```

If a command fails, do not skip `umount`; confirm the mount state with
`mount | grep "$MOUNT_DIR"` before retrying or closing the terminal.

Copy the CSV back to the local checkout:

**[LOCAL]**

```sh
scp "$REMOTE_HOST:quest-validator.csv" quickstart/results-potsdam.csv
```

Analyse it from the quickstart directory so graphs are written to
`quickstart/graphs/`:

**[LOCAL]**

```sh
. .venv/bin/activate
cd quickstart
python3 -m pip install -r requirements.txt
python3 check_validator.py results-potsdam.csv
find graphs -type f -name '*.png' -print
cd ..
```

The scatter plot groups differences below 3 ms as `OK`, below 100 ms as
`MEH`, and larger or unreachable differences as `NOT OK`. These thresholds are
validator diagnostics, not a claim that the emulation is physically calibrated
for a particular satellite system.

## 15. Explore QUEST Features

Make a copy of `quickstart.toml` for each exercise; keep the original as a
known-good reference.

1. Change `antenna_number` for Potsdam from `2` to `1`. Regenerate the ZIP and
   compare how many simultaneous satellite contacts are selected.
2. Add a third `[[ground_station]]` with a unique name and valid latitude and
   longitude. It receives its own always-active microVM.
3. Remove both `ground_station_bandwidth_kbits` and
   `ground_station_path_stretch` to disable direct ground-station backhaul.
   The fields are a pair; supplying only one is invalid.
4. Change `satellite_activation` to `"bbox"`. Satellite activity is then
   controlled by the configured geographic box rather than selected direct
   ground contacts.

Run `python3 satgen.py INPUT.toml OUTPUT.zip` after each change. A validation
error means the configuration contract was violated; read
[`docs/reference/configuration.md`](../docs/reference/configuration.md) before
changing code.

## Troubleshooting

**A command is missing.** Check whether you are in `[LOCAL]` or `[REMOTE]`.
Install local project tools yourself. On the remote VM, install Go, Python, and
user-space project tools as described above; report missing KVM, sudo, or
host-network prerequisites to the Helpdesk.

**The current directory is wrong.** Run `pwd` and `test -f
quickstart/quickstart.toml`. Most commands expect the QUEST repository root;
the two image commands intentionally run from `quickstart/validator`.

**Docker is found on the remote VM.** Stop. Do not run or uninstall it. Ask the
administrator for a clean host because Docker-created bridges and firewall
rules can conflict with Celestial networking.

**`/dev/kvm` is missing or inaccessible.** This is an administrator-provided
virtualization prerequisite. Send the exact preflight error to the Helpdesk;
do not change device permissions or load kernel modules yourself.

**The worker rejects the network interface.** Re-run `ip route show default`
and use the interface from its first default route. Do not assume `ens4`,
`eth0`, or a name from another VM.

**A file is missing under `/celestial`.** Re-run the three `ls -lh` checks in
step 8 and compare each filename with `quickstart/quickstart.toml`.

**TCP port 1969 is already in use.** Confirm that an older `celestial.bin`
process is not still running. Do not kill another user's process on a shared
machine; coordinate with the administrator.

**A microVM fails to start.** Read terminal 1 around the first Firecracker
error, check `/dev/kvm`, and confirm the kernel and image files exist. Do not
reinterpret a build, permission, or artifact error as a topology problem.

## What to Read Next

- [`Project overview`](../docs/handbook/01-project-overview.md)
- [`Core concepts`](../docs/handbook/02-core-concepts.md)
- [`System architecture`](../docs/handbook/05-system-architecture.md)
- [`Startup call flow`](../docs/handbook/06-startup-call-flow.md)
- [`Source-code reading guide`](../docs/handbook/07-source-code-reading-guide.md)
- [`Complete configuration reference`](../docs/reference/configuration.md)

Return to the [repository starting page](../README.md) for the full handbook
order.
