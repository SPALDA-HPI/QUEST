# Nested Virtualization and KVM

Firecracker requires hardware virtualization through `/dev/kvm`. When QUEST
runs inside an HPI virtual machine, the underlying infrastructure must expose
nested virtualization to that VM.

The HPI Scientific Compute Helpdesk provides the VM, sudo policy, and working
KVM configuration. Students should not change hypervisor settings, load host
kernel modules, or rewrite `/dev/kvm` permissions.

Use the read-only project check:

```sh
./quickstart/preflight.sh
```

Its KVM portion is equivalent to checking that `/dev/kvm` is a character
device and is readable and writable by the process that will start
Firecracker. It also checks Linux/amd64 and required commands without changing
the host.

If the check fails, send the administrator:

- the output of `uname -s` and `uname -m`;
- the exact `/dev/kvm` error from the preflight;
- whether `test -c /dev/kvm` succeeds;
- the assigned VM identity through the approved support channel.

Do not put the actual VM hostname into repository files or public issue logs.
Cloud-provider provisioning examples are intentionally outside QUEST because
students use an administrator-provided HPI environment.
