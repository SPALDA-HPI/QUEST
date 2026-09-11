# Compilation Reference

QUEST retains Celestial's Python topology/coordinator programs and Linux/amd64
Go worker. Generated protobuf bindings and the embedded Berkeley Packet Filter
(eBPF) object are also part of the source tree.

## Local container toolchain

Use the repository's pinned compile container on a local workstation with
Docker:

```sh
make celestial-make
./celestial-make proto
./celestial-make celestial.bin
```

`make celestial-make` builds `compile.Dockerfile`. The wrapper mounts the
checkout at `/celestial` and runs `make` inside a Linux/amd64 container. Use
`./celestial-make ebpf` only when the eBPF C source changes.

Generated protobuf files under `proto/celestial/` must come from
`proto/celestial/celestial.proto`; do not edit them by hand.

## Native remote worker build

Do not use Docker on the remote Celestial host. With Go available, build the
worker natively from the repository root:

```sh
go version
make celestial.bin
```

The Makefile sets `GOOS=linux` and `GOARCH=amd64`. The resulting
`celestial.bin` is the host worker, not a guest workload.

## Python environment

The topology generator and coordinator use the same declared Python packages:

```sh
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements.txt
```

See the [quickstart](../../quickstart/README.md) for the complete split between
local builds and remote execution.
