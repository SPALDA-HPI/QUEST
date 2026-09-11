# Guest Kernel Reference

Every Firecracker microVM needs an uncompressed Linux `vmlinux` kernel built
for Linux/amd64. QUEST includes the original Celestial configuration in
`kernel/config-5.12`.

## Container build

Build the quickstart kernel on the local Docker workstation:

```sh
make -C kernel vmlinux-5.12.bin
```

The Makefile builds `kernel/Dockerfile`, mounts `kernel/` at `/input`, checks
out Linux `v5.12`, applies `config-5.12`, and writes
`kernel/vmlinux-5.12.bin`. This generated binary is ignored by Git.

## Important options

The supplied configuration supports Firecracker devices, ext4, the overlay
root setup used by the builder, and Kernel-based Virtual Machine (KVM) clock
support. `CONFIG_RANDOM_TRUST_CPU=y` helps many concurrently booting guests
avoid blocking on a depleted entropy pool when the host CPU source is
acceptable for the experiment.

If a workload needs an unavailable kernel feature, copy a supplied config,
change only the required options, build a matching filename, and update the
TOML `kernel` field. Record that configuration with the experiment.

## Manual build boundary

The container path is the supported beginner workflow. A manual kernel build
requires Linux source, a compiler toolchain, and an appropriate `.config`;
consult the [Firecracker kernel setup guide](https://github.com/firecracker-microvm/firecracker/blob/main/docs/rootfs-and-kernel-setup.md).
Do not replace or reconfigure the remote host kernel as part of a QUEST guest
kernel build.
