# Output and Result Retrieval

## Console streams

The worker forwards each guest's standard output and standard error to
`/celestial/out` on the worker host. Satellites use names such as
`1-12.out`/`1-12.err`; a named ground station uses
`gst-potsdam.out`/`gst-potsdam.err`.

Heavy console output writes to host storage and can perturb a performance
experiment. Prefer concise structured records for application measurements.

## Writable overlays

The configured root filesystem is read-only. Each machine receives a sparse
writable ext4 overlay:

- satellite: `/celestial/ce<SHELL>-<ID>.ext4`;
- ground station: `/celestial/cegst-<NAME>.ext4`.

Stop the coordinator and worker before reading an overlay. Mount it read-only,
copy only the result you need, and unmount it before another run:

```sh
MOUNT_DIR="$(mktemp -d)"
sudo mount -o loop,ro /celestial/ce1-12.ext4 "$MOUNT_DIR"
sudo install -m 0644 "$MOUNT_DIR/root/output.csv" "$HOME/sat-1-12-output.csv"
sudo umount "$MOUNT_DIR"
rmdir "$MOUNT_DIR"
sudo chown "$(id -u):$(id -g)" "$HOME/sat-1-12-output.csv"
```

If the run used multiple worker hosts, an overlay exists only on the host that
was assigned that machine. QUEST's beginner quickstart uses one worker.

Generated ZIPs, kernels, images, overlays, CSV files, graphs, and caches are
ignored. Store experiment artifacts separately with their commit ID and input
configuration; do not add them to the platform root by default.
