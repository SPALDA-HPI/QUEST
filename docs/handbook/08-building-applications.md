# 8. Building Applications

A QUEST application is ordinary Linux software packaged into a guest root
filesystem. Begin with the two quickstart examples before adding a language,
database, or data dependency.

## The builder contract

Build the local image-builder container:

```sh
make rootfsbuilder
```

The builder starts from an Alpine Linux 3.18 minirootfs and adds the init,
network, overlay, time, and shutdown scripts expected by Celestial. A build
invocation can mount three inputs:

- `/app.sh` is required and becomes the guest application entry point;
- `/base.sh` is optional and runs inside the root filesystem at build time;
- `/files/` is optional and its contents are copied into the image root.

The builder writes the named SquashFS image through `/opt/code`, which should
be a mounted host directory.

## Satellite server example

`quickstart/validator/server.sh` is deliberately minimal. It prints a status
line and sleeps forever so the satellite responds to Internet Control Message
Protocol (ICMP) pings while active.

From `quickstart/validator` on the local workstation:

```sh
docker run --rm \
    --platform linux/amd64 \
    --privileged \
    -v "$(pwd)/server.sh":/app.sh \
    -v "$(pwd)":/opt/code \
    rootfsbuilder server.img
```

No `/base.sh` is needed because the base image already contains the shell and
network tools used by `server.sh`.

## Validator example

The validator needs Python, `requests`, `ping3`, and its Python source:

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

`validator-base.sh` uses Alpine's package manager and Python package installer
while the image is being built. `validator.sh` later runs
`python3 validator.py info.celestial` inside the microVM.

## Boot and storage sequence

At runtime:

1. Firecracker boots the configured guest kernel.
2. The read-only root image is the lower filesystem.
3. `builder/ceinit` mounts the per-machine ext4 disk as a writable overlay and
   pivots into the merged root.
4. `builder/fcinit.c` and the Alpine init system bring up the guest.
5. `builder/run-user-script` configures time when available, adds
   `info.celestial`, and runs `/app.sh`.
6. When `/app.sh` exits, the guest shuts down.

Write results under the guest's normal filesystem, such as
`/root/result.csv`; they land in the writable overlay. The validator uses a
comma-separated values (CSV) file. Do not try to modify the read-only image
during a run.

## Add a minimal application

1. Copy one quickstart `app.sh` and give it a descriptive name.
2. Put only runtime files beneath a dedicated application directory.
3. Add a `base.sh` only if packages must be installed at image-build time.
4. Build one ignored `.img` locally.
5. Set `rootfs` in a copied Tom's Obvious Minimal Language (TOML)
   configuration.
6. Install that image under `/celestial` with the exact same basename.
7. First test startup and one result; scale only after the small case works.

Use shell `exec` for a long-running process when signal delivery matters. Keep
console output bounded and flush result files before shutdown.

## Data and dependency boundary

QUEST intentionally does not provide an attached read-only satellite data
drive. Put small, immutable inputs into the root image through `/files`, or
design an explicit application-specific data transfer or storage mechanism.
Large scientific datasets should remain outside the platform repository and
be documented with a stable identifier or preparation procedure.

## Checkpoint

Describe which of `app.sh`, `base.sh`, and `/files` is needed for a
single statically linked executable, and where its output persists after the
root image remains read-only.
