# Compilation Reference

QUEST retains Celestial's Python topology/coordinator programs and Linux/amd64
Go worker. Generated protobuf bindings and the embedded Berkeley Packet Filter
(eBPF) object are also part of the source tree.

## Local container toolchain

Use the repository's pinned compile container on a local workstation with
Docker:

```sh
./celestial-make celestial.bin
```

The wrapper runs `make celestial-make`, which builds `compile.Dockerfile`, then
mounts the checkout at `/celestial` and runs the requested Make target inside
a Linux/amd64 container. The resulting `celestial.bin` is therefore suitable
for the remote Linux/amd64 worker even when the local workstation is macOS or
Windows Subsystem for Linux 2. Use `./celestial-make proto` only when the
protocol definition changes, and use
`./celestial-make ebpf` only when the eBPF C source changes.

Generated protobuf files under `proto/celestial/` must come from
`proto/celestial/celestial.proto`; do not edit them by hand.

This is the build path used by the original Celestial Quick Start. It keeps
Docker on the local build workstation and transfers only the resulting binary
to the clean runtime host.

## Native build for advanced development

With a compatible Linux/amd64 Go toolchain, developers can build natively:

```sh
go version
make celestial.bin
```

The Makefile sets `GOOS=linux` and `GOARCH=amd64`. This is not the beginner
quickstart path and is not a reason to install Docker on the remote Celestial
host. The resulting `celestial.bin` is the host worker, not a guest application.

## Python environment

The topology generator and coordinator use the same declared Python packages:

```sh
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements.txt
```

See the [quickstart](../../quickstart/README.md) for the complete split between
local builds and remote execution.
