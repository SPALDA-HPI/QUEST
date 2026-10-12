# QUEST Quickstart

This tutorial takes you from a clean checkout to one short QUEST emulation.
Read each checkpoint before continuing.

QUEST builds on [Celestial](https://github.com/OpenFogStack/celestial), an
open-source LEO edge emulator that runs every satellite and ground station as a
Firecracker microVM. In this guide, "Celestial" means the emulator components
inside QUEST: the worker `celestial.bin` and the coordinator `celestial.py`.
"Upstream Celestial" means the original project.

## What You Will Do

You will use two machines:

- your **local workstation** uses Docker to build the Linux/amd64 Celestial
  worker and the guest root filesystem images, downloads the supplied guest
  kernel, generates the topology, and analyses the results;
- one **remote VM** at HPI runs the Celestial worker and the Python
  coordinator in separate terminals, plus the Firecracker microVMs. Docker is
  never used there.

```text
LOCAL workstation (Docker)                   REMOTE VM (no Docker)
---------------------------------            ------------------------------------
celestial.bin             step 7   --scp-->  ~/QUEST/celestial.bin        (worker)
server.img, validator.img step 5   --scp-->  /celestial/
vmlinux-5.12.bin          step 6   --scp-->  /celestial/
quickstart.zip            step 8   --scp-->  ~/QUEST/quickstart/     (coordinator)
results-potsdam.csv       step 14  <--scp--  ~/quest-validator.csv
```

The example contains 32 satellites and two ground stations. It demonstrates
contact-based activation, finite antenna counts, multiple ground stations, and
direct ground-station backhaul. The run lasts 120 seconds and records the
difference between emulated ping latency and the latency reported by
Celestial's information service.

## Before You Begin

You need:

- **local:** Git, a POSIX shell, Python 3.11, `make`, `curl`, `file`, `ssh`,
  `scp`, and Docker that can run `linux/amd64` containers. Your GitHub account
  needs SSH access to `SPALDA-HPI/QUEST`.
- **remote:** the HPI VM assigned to you, running Linux on x86-64 with `sudo`
  rights and KVM access. Step 3 installs the rest: Git, `make`, Python 3.11,
  Firecracker 1.6.0, WireGuard tools, `ipset`, `ip`, `tc`, and `iptables`.

You install and manage the project tools yourself. Host-level problems, such as
missing KVM access, `sudo` rights, kernel modules, or network configuration, go
to the Helpdesk; do not change those yourself.

You do not need Go on either machine: step 7 compiles the worker inside a
pinned Docker container.

The worker is built for Linux on x86-64/amd64. A macOS or Windows computer can
still be the local build machine, because Docker builds Linux/amd64 artifacts.
On Windows, use Windows Subsystem for Linux 2 (WSL2) and run the same POSIX
commands shown here. Native PowerShell commands are outside this guide.

> [!WARNING]
> Do not install or run Docker on the remote VM. Docker's bridges and firewall
> rules interfere with Celestial's Firecracker networking. Docker belongs on
> your local workstation only.

**One experiment per VM.** The worker uses the VM's host networking, TCP port
1969, and the directory `/celestial`, so only one Celestial experiment can run
on a VM at a time. A new run also deletes the previous run's console logs and
recreates the microVM disks, so retrieve your results (step 14) before starting
another run. If you share a VM with other students, agree on who runs when.

<!-- TODO: state whether each student gets their own VM. If so, shorten the paragraph above. -->

## Local and Remote Commands

Every command block is labelled `[LOCAL]` or `[REMOTE]`.

- `[LOCAL]` means your workstation or WSL2 shell. Unless a block says
  otherwise, it runs in the repository root: the `QUEST` folder that contains
  `satgen.py`.
- `[REMOTE]` means a shell on the HPI VM, opened with `ssh` from a local
  terminal. A new SSH session starts in your home directory, so remote blocks
  begin with `cd ~/QUEST` where needed.

You need one local terminal throughout, and up to three remote terminals from
step 10 on. If you know `tmux`, you can run the remote terminals inside one SSH
session instead.

In each local terminal you open, define the remote name:

**[LOCAL]**

```sh
REMOTE_HOST="<your assigned host>"
```

Replace the angle-bracket text with the hostname supplied to you. The variable
exists only in that terminal; define it again after opening a new terminal.

Common shell reminders:

- `cd PATH` changes the current directory.
- `pwd` prints the current directory.
- `.` followed by a filename loads environment settings into the current
  shell; `. .venv/bin/activate` activates the Python environment.
- `test -s FILE && echo OK` prints `OK` only if `FILE` exists and is not empty.
  Several checkpoints use this pattern.
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
    ├── server.sh             long-running satellite application
    ├── validator-base.sh     installs validator dependencies in its image
    ├── validator.py          compares reported and measured latency
    └── validator.sh          starts validator.py inside the ground station
```

The following files are created while you follow this guide and are
intentionally ignored by Git:

- `celestial.bin` (repository root): the worker binary;
- `quickstart/vmlinux-5.12.bin`: downloaded guest Linux kernel;
- `quickstart/validator/server.img`: satellite root filesystem;
- `quickstart/validator/validator.img`: validator root filesystem;
- `quickstart/quickstart.zip`: serialized topology and timed state changes;
- `quickstart/results-potsdam.csv` and `quickstart/graphs/`: results.

## 1. Clone QUEST

Clone the repository on the local workstation. SSH cloning is shown; use the
GitHub method configured for your account.

**[LOCAL]**

```sh
git clone git@github.com:SPALDA-HPI/QUEST.git
cd QUEST
test -f quickstart/quickstart.toml && echo OK
git rev-parse HEAD
```

Checkpoint: `OK` is printed. Note the commit ID printed by `git rev-parse HEAD`.

Now clone the same repository on the remote VM. The repository is private, so
the VM needs your GitHub credentials. The simplest way is SSH agent forwarding
(`ssh -A`), which lets the VM use your local key without copying it there. Use
`-A` only for this step and connect without it afterwards.

**[LOCAL]**

```sh
ssh -A "$REMOTE_HOST"
```

**[REMOTE]**

```sh
git clone git@github.com:SPALDA-HPI/QUEST.git ~/QUEST
cd ~/QUEST
git rev-parse HEAD
```

Checkpoint: the commit ID matches the local one. If it does not, run
`git pull` in both checkouts and compare again. Matching commits make the run
reproducible.

If the clone fails with `Permission denied (publickey)`, type `exit`, run
`ssh-add` locally to load your key, and reconnect with `ssh -A`. Alternatively,
clone over HTTPS with a GitHub personal access token.

Type `exit` to close the connection; the next step is local.

## 2. Prepare the Local Workstation

Check the local tools from the repository root.

**[LOCAL]**

```sh
git --version
python3.11 --version
make --version
curl --version
command -v file ssh scp
docker version
```

Create a Python virtual environment. A virtual environment keeps this
project's Python packages separate from system Python. Use Python 3.11,
matching CI; see the [environment guide](../docs/handbook/03-development-environments.md#python-virtual-environments)
for installation and VS Code interpreter selection.

The first requirements file is for topology generation (step 8), the second
for result analysis (step 14).

**[LOCAL]**

```sh
python3.11 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements.txt -r quickstart/requirements.txt
```

The shell prompt often gains a `(.venv)` prefix. Confirm that Python now comes
from the repository:

**[LOCAL]**

```sh
python3 -c 'import sys; print(sys.executable)'
```

Checkpoint: the path contains `QUEST/.venv/`.

## 3. Prepare the Remote VM

Connect to the VM (without `-A` from now on):

**[LOCAL]**

```sh
ssh "$REMOTE_HOST"
```

First inspect the operating system and virtualization support.

**[REMOTE]**

```sh
cat /etc/os-release
uname -m
ls -l /dev/kvm
```

Checkpoint: the architecture is `x86_64` or `amd64`, and `/dev/kvm` exists. If
`/dev/kvm` is missing, stop and report it to the Helpdesk.

On Debian or Ubuntu, install the basic project and networking commands.
`iproute2` provides `ip` and `tc`; `e2fsprogs` provides `mkfs.ext4`, which the
worker uses to create microVM disks.

**[REMOTE]**

```sh
sudo apt-get update
sudo apt-get install -y git make curl tar python3 python3-venv \
    wireguard-tools iproute2 iptables ipset e2fsprogs
```

The unversioned `python3` package is not necessarily Python 3.11. Check:

**[REMOTE]**

```sh
command -v python3.11
```

If this prints nothing, install Python 3.11 and its venv package. On Debian 12
and Ubuntu 22.04, run
`sudo apt-get install -y python3.11 python3.11-venv`. Ubuntu 24.04 does not
ship Python 3.11; ask the Helpdesk or your supervisor how to install it.

<!-- TODO: name the OS image of the HPI VMs and keep only the matching command. -->

Install Firecracker 1.6.0, the version upstream Celestial uses. The worker runs
with `sudo` and looks Firecracker up on `PATH`. `sudo` uses a fixed system
`PATH` that includes `/usr/local/bin` but not your home directory, so install it
there.

**[REMOTE]**

```sh
cd ~
FIRECRACKER_VERSION="1.6.0"
curl -fLO "https://github.com/firecracker-microvm/firecracker/releases/download/v${FIRECRACKER_VERSION}/firecracker-v${FIRECRACKER_VERSION}-x86_64.tgz"
tar -xzf "firecracker-v${FIRECRACKER_VERSION}-x86_64.tgz"
sudo install -m 0755 \
    "release-v${FIRECRACKER_VERSION}-x86_64/firecracker-v${FIRECRACKER_VERSION}-x86_64" \
    /usr/local/bin/firecracker
sudo sh -c 'command -v firecracker && firecracker --version'
```

Checkpoint: the last command prints `/usr/local/bin/firecracker` and reports
version 1.6.0.

Create the remote Python environment used by the coordinator:

**[REMOTE]**

```sh
cd ~/QUEST
python3.11 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 -c 'import sys; print(sys.version); print(sys.executable)'
```

Checkpoint: Python reports version 3.11, and its executable is inside
`~/QUEST/.venv`.

Upstream Celestial raises the open-file and process limits to 64,000 before
running many microVMs. The worker runs as root, so check root's limits without
changing them:

**[REMOTE]**

```sh
sudo bash -c 'ulimit -n; ulimit -u'
```

Checkpoint: both numbers are at least `64000` (or `unlimited`). If either is
lower, report it to the Helpdesk; do not edit `/etc/security/limits.conf`
yourself.

## 4. Check the Remote VM

The preflight script only reads host state. It does not install packages or
change networking.

**[REMOTE]**

```sh
cd ~/QUEST
./quickstart/preflight.sh
```

Every line should begin with `OK:` or `INFO:`. An `ERROR:` line is a stop
condition: fix it (see [Troubleshooting](#troubleshooting)) and run the script
again before continuing.

## 5. Build Guest Images Locally

The images are small Linux filesystems used *inside* Firecracker microVMs.
Docker only constructs them; Docker is not the experiment runtime.

This is the slowest step. On Apple Silicon Macs, Docker emulates amd64, so the
builds take considerably longer than on an x86 machine.

Check that Docker can run amd64 containers:

**[LOCAL]**

```sh
docker version
docker buildx ls
docker run --rm --platform linux/amd64 debian:bookworm uname -m
```

Checkpoint: the last command prints `x86_64`. If it fails, your Docker
installation cannot run amd64 containers; fix that before continuing.

Build the existing image-builder container, then change into the validator
folder:

**[LOCAL]**

```sh
make rootfsbuilder
cd quickstart/validator
```

Build the validator ground-station image:

**[LOCAL, in `quickstart/validator`]**

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

Build the satellite server image and return to the repository root:

**[LOCAL, in `quickstart/validator`]**

```sh
docker run --rm \
    --platform linux/amd64 \
    --privileged \
    -v "$(pwd)/server.sh":/app.sh \
    -v "$(pwd)":/opt/code \
    rootfsbuilder server.img
cd ../..
```

Checkpoint: both images exist and are not empty.

**[LOCAL]**

```sh
ls -lh quickstart/validator/validator.img quickstart/validator/server.img
```

## 6. Download the Guest Kernel Locally

Celestial supplies a Linux 5.12 kernel matching `kernel/config-5.12`. Download
it instead of compiling one yourself:

**[LOCAL]**

```sh
curl -fL --retry 3 \
    -o quickstart/vmlinux-5.12.bin \
    "https://tubcloud.tu-berlin.de/s/fcLHfyeQSZwWi5k/download/vmlinux-5.12.bin"
test -s quickstart/vmlinux-5.12.bin && echo OK
```

`-f` turns an HTTP error into a failed command, `-L` follows the download
redirect, and `--retry 3` retries transient failures.

Checkpoint: `OK` is printed. Do not substitute a different kernel. This kernel
runs inside the microVMs, not on your workstation or the remote VM.

## 7. Build the Worker Locally

Celestial uses the `celestial-make` Docker wrapper. It builds the pinned
compile image and runs the requested Make target inside a Linux/amd64
container.

**[LOCAL]**

```sh
./celestial-make celestial.bin
file celestial.bin
```

Checkpoint: `file` reports an `ELF 64-bit` `x86-64` executable.

`celestial.bin` is the privileged worker. `satgen.py` generates the topology
locally (step 8). `celestial.py` is already part of the remote checkout and
runs there as the coordinator (step 11).

## 8. Generate the Topology Locally

The TOML file is human-readable input. `satgen.py` calculates positions,
contacts, routes, VM states, and link properties, then stores timed differences
in a ZIP archive. Use the virtual environment from step 2.

**[LOCAL]**

```sh
. .venv/bin/activate
python3 satgen.py quickstart/quickstart.toml quickstart/quickstart.zip
test -s quickstart/quickstart.zip && echo OK
```

Checkpoint: the progress bar reaches `100%`, `satgen.py` prints
`Output written to quickstart/quickstart` (the name without `.zip`), and `OK`
is printed.

To run generation in Docker instead, see the
[appendix](#appendix-generating-the-topology-in-docker).

## 9. Transfer Files to the Remote VM

Copy the worker, the topology, and the three guest artifacts:

**[LOCAL]**

```sh
scp celestial.bin "$REMOTE_HOST:QUEST/celestial.bin"
scp quickstart/quickstart.zip "$REMOTE_HOST:QUEST/quickstart/quickstart.zip"
scp quickstart/vmlinux-5.12.bin \
    quickstart/validator/server.img \
    quickstart/validator/validator.img \
    "$REMOTE_HOST:"
```

Install the guest artifacts in the worker's fixed artifact directory.
`sudo install -d` creates the directory; the next command copies the three
read-only inputs into it.

**[REMOTE]**

```sh
sudo install -d -m 0755 /celestial
sudo install -m 0644 \
    "$HOME/vmlinux-5.12.bin" "$HOME/server.img" "$HOME/validator.img" \
    /celestial/
chmod 0755 "$HOME/QUEST/celestial.bin"
ls -lh /celestial/vmlinux-5.12.bin /celestial/server.img /celestial/validator.img
```

Checkpoint: all three files are listed with a non-zero size.

The topology ZIP stays in `~/QUEST/quickstart/`, where the coordinator reads
it. Do not copy it into `/celestial`.

## 10. Start the Worker

Open a new local terminal, define `REMOTE_HOST`, connect with
`ssh "$REMOTE_HOST"`, and keep that session open. This is remote terminal 1.

Starting the worker deletes the console logs of the previous run, so retrieve
any earlier results first (step 14).

Determine the actual default network interface instead of assuming a name.

**[REMOTE, terminal 1]**

```sh
cd ~/QUEST
CELESTIAL_IFACE="$(ip route show default | awk 'NR == 1 { print $5 }')"
printf 'Using interface: %s\n' "$CELESTIAL_IFACE"
sudo ./celestial.bin -debug -network-interface "$CELESTIAL_IFACE"
```

Checkpoint: the worker prints `Celestial started!` and listens on TCP port

1969. Leave this command running.

## 11. Start the Coordinator

Open remote terminal 2. The coordinator and worker run on the same VM, so the
coordinator connects to the worker through the loopback address `127.0.0.1`.

**[REMOTE, terminal 2]**

```sh
cd ~/QUEST
. .venv/bin/activate
python3 celestial.py quickstart/quickstart.zip 127.0.0.1:1969
```

The coordinator registers the worker, initializes all machines, and applies a
new topology state every five seconds. The first microVM boots take noticeably
longer than later updates.

## 12. Observe the Experiment

Open remote terminal 3. Ground-station and satellite console streams are
written below `/celestial/out`.

**[REMOTE, terminal 3]**

```sh
tail -F /celestial/out/gst-potsdam.out
```

`-F` keeps retrying until the file exists, so you can start it before the
ground station has booted. The validator reports active satellites and latency
comparisons.

To inspect a satellite, first list the available output files:

**[REMOTE, terminal 3]**

```sh
find /celestial/out -type f -name '[0-9]*-*.out' -print
```

Then run `tail -F` on one path printed by `find`. Press `Ctrl+C` to stop
`tail`; this does not stop the experiment.

## 13. Stop the Experiment

The coordinator stops automatically after 120 seconds. Wait for terminal 2 to
print `finished`. To stop early, press `Ctrl+C` in terminal 2 and wait for the
same message. The coordinator asks the worker to stop all microVMs.

After the coordinator finishes, return to remote terminal 1, press `Ctrl+C`
once, and wait for the worker process to exit. Do not mount an overlay while
its microVM or the worker is still using it.

## 14. Retrieve and Analyse the Results

The Potsdam validator writes `/root/validator.csv` inside its writable overlay.
Mount that overlay read-only after shutdown and copy the file out. Do this
before starting another run: the next run overwrites the overlay.

**[REMOTE]**

```sh
MOUNT_DIR="$(mktemp -d)"
sudo mount -o loop,ro /celestial/cegst-potsdam.ext4 "$MOUNT_DIR"
sudo install -m 0644 -o "$(id -u)" -g "$(id -g)" \
    "$MOUNT_DIR/root/validator.csv" "$HOME/quest-validator.csv"
sudo umount "$MOUNT_DIR"
rmdir "$MOUNT_DIR"
```

If a command fails, do not skip `umount`; confirm the mount state with
`mount | grep "$MOUNT_DIR"` before retrying or closing the terminal.

Copy the CSV back to the local checkout and analyse it from the quickstart
directory, so graphs are written to `quickstart/graphs/`:

**[LOCAL]**

```sh
scp "$REMOTE_HOST:quest-validator.csv" quickstart/results-potsdam.csv
. .venv/bin/activate
cd quickstart
python3 check_validator.py results-potsdam.csv
find graphs -type f -name '*.png' -print
cd ..
```

Checkpoint: `find` lists at least one PNG file.

The scatter plot groups differences below 3 ms as `OK`, below 100 ms as `MEH`,
and larger or unreachable differences as `NOT OK`. These thresholds are
validator diagnostics, not a claim that the emulation is physically calibrated
for a particular satellite system.

## 15. Explore QUEST Features

Keep the original `quickstart.toml` as a known-good reference. For each
exercise:

1. copy the configuration, for example
   `cp quickstart/quickstart.toml quickstart/ex1.toml`, and edit the copy;
2. generate a new archive locally with
   `python3 satgen.py quickstart/ex1.toml quickstart/ex1.zip` (step 8);
3. copy it to the VM with
   `scp quickstart/ex1.zip "$REMOTE_HOST:QUEST/quickstart/"`;
4. repeat steps 10–14, passing `quickstart/ex1.zip` to `celestial.py`.

A validation error from `satgen.py` means the configuration contract was
violated; read [`docs/reference/configuration.md`](../docs/reference/configuration.md)
before changing code.

The exercises:

1. Change `antenna_number` for Potsdam from `2` to `1`. Compare how many
   satellites the Potsdam validator reports as active (step 12) with your
   first run.
2. Add a third `[[ground_station]]` with a unique name and a valid latitude and
   longitude. It receives its own always-active microVM, and its console output
   appears as `/celestial/out/gst-<name>.out`. Check how the Potsdam entry
   selects its root filesystem and decide which image the new station should
   boot.
3. Remove both `ground_station_bandwidth_kbits` and
   `ground_station_path_stretch` to disable direct ground-station backhaul.
   The fields are a pair; supplying only one is invalid.
4. Change `satellite_activation` to `"bbox"`. Satellite activity is then
   controlled by the configured geographic box rather than selected direct
   ground contacts.

## Troubleshooting

**A command is missing.** Check whether you are in a `[LOCAL]` or `[REMOTE]`
shell. Install project tools yourself (steps 2 and 3). Report missing KVM,
`sudo`, or host-network prerequisites to the Helpdesk.

**`cd` fails or a file is not found.** Run `pwd`. Local commands expect the
repository root (the folder with `satgen.py`); only the two image commands in
step 5 run from `quickstart/validator`. Remote commands start with
`cd ~/QUEST`.

**Cloning on the VM fails with `Permission denied (publickey)`.** Your GitHub
key did not reach the VM. Run `ssh-add` locally and reconnect with `ssh -A`
(step 1).

**Docker is found on the remote VM.** Stop. Do not run or uninstall it. Ask the
Helpdesk for a clean host, because Docker-created bridges and firewall rules
conflict with Celestial networking.

**`/dev/kvm` is missing or inaccessible.** This is a virtualization
prerequisite the Helpdesk provides. Do not change device permissions or load
kernel modules yourself.

**The worker cannot find `firecracker`.** Firecracker must be in
`/usr/local/bin` (step 3), because `sudo` ignores your personal `PATH`. Check
with `sudo sh -c 'command -v firecracker'`.

**The worker rejects the network interface.** Re-run `ip route show default`
and use the interface from its first default route. Do not assume `ens4`,
`eth0`, or a name from another VM.

**A file is missing under `/celestial`.** Re-run the `ls -lh` check in step 9
and compare each filename with `quickstart/quickstart.toml`.

**TCP port 1969 is already in use.** Check for an older worker with
`pgrep -a celestial`. If it belongs to another user, coordinate with them or
the Helpdesk instead of stopping it.

**The coordinator cannot connect to `127.0.0.1:1969`.** Confirm that the worker
is running in remote terminal 1 and printed `Celestial started!`. Keep the
address `127.0.0.1`; the worker runs on the same VM.

**A microVM fails to start.** Read terminal 1 around the first Firecracker
error, check `/dev/kvm`, and confirm the kernel and image files exist (step 9).
Build, permission, and artifact errors are not topology problems.

**`validator.csv` is missing or contains an unexpected run.** A newer run has
overwritten the overlay. Repeat the run and retrieve the results (step 14)
before starting another one.

## What to Read Next

- [`Project overview`](../docs/handbook/01-project-overview.md)
- [`Core concepts`](../docs/handbook/02-core-concepts.md)
- [`System architecture`](../docs/handbook/05-system-architecture.md)
- [`Startup call flow`](../docs/handbook/06-startup-call-flow.md)
- [`Source-code reading guide`](../docs/handbook/07-source-code-reading-guide.md)
- [`Complete configuration reference`](../docs/reference/configuration.md)

Return to the [repository starting page](../README.md) for the full handbook
order.

## Appendix: Generating the Topology in Docker

`satgen-docker` is an alternative to the `satgen.py` command in step 8 when you
want generation isolated from your local Python environment. Use one or the
other, not both; they write the same kind of archive.

**[LOCAL]**

```sh
make satgen-docker
docker run --rm \
    -v "$(pwd)":/app \
    satgen-docker \
    /app/quickstart/quickstart.toml \
    /app/quickstart/quickstart.zip
```