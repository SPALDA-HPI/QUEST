# Guest Kernel Reference

Every Firecracker microVM needs an uncompressed Linux `vmlinux` kernel built
for Linux/amd64. QUEST includes the original Celestial configuration in
`kernel/config-5.12`.

## Supplied quickstart kernel

Download the Linux 5.12 guest kernel published in the original Celestial Quick
Start. Run this locally from `quickstart/`:

```sh
cd quickstart
curl -fL --retry 3 \
    -o vmlinux-5.12.bin \
    "https://tubcloud.tu-berlin.de/s/fcLHfyeQSZwWi5k/download/vmlinux-5.12.bin"
test -s vmlinux-5.12.bin
cd ..
```

`curl -f` fails on HTTP errors, `-L` follows the download redirect, and
`--retry 3` retries transient failures. If the server continues to return an
HTTP error such as 503, stop and ask the project supervisor for the verified
5.12 file. Do not substitute an arbitrary Firecracker kernel. The downloaded
binary is ignored by Git.

The supplied kernel follows `kernel/config-5.12`.

## Important options

The supplied configuration supports Firecracker devices, ext4, the overlay
root setup used by the builder, and Kernel-based Virtual Machine (KVM) clock
support. `CONFIG_RANDOM_TRUST_CPU=y` helps many concurrently booting guests
avoid blocking on a depleted entropy pool when the host CPU source is
acceptable for the experiment.

If an application needs an unavailable kernel feature, discuss the change with the
project supervisor, copy the supplied config, change only the required
options, build a matching filename, and update the TOML `kernel` field. Record
that configuration with the experiment.

## Manual build boundary

Kernel compilation is outside the beginner workflow. It requires Linux source,
a compiler toolchain, and an appropriate `.config`;
consult the [Firecracker kernel setup guide](https://github.com/firecracker-microvm/firecracker/blob/main/docs/rootfs-and-kernel-setup.md).
Do not replace or reconfigure the remote host kernel as part of a QUEST guest
kernel build.
