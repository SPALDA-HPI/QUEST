# 9. Testing and Debugging

Test the narrowest boundary that can disprove your change, then widen the
check. A unit test, build, generated topology, and remote KVM run answer
different questions.

## Python checks

Activate the repository environment:

```sh
. .venv/bin/activate
```

Run one test file during development:

```sh
python3 -m unittest discover -s test -p 'test_antenna_scheduler.py' -v
```

Run the retained Python suite and syntax compilation:

```sh
python3 -m compileall -q celestial proto quickstart test *.py
python3 -m unittest discover -s test -p 'test_*.py' -v
python3 -m mypy --config-file setup.cfg *.py
```

VS Code's Pylance and mypy are separate checkers. A passing mypy run does not
guarantee an empty Problems panel. Install `requirements-dev.txt` and select
the Python 3.11 environment as described in the
[environment guide](03-development-environments.md#python-virtual-environments).
With Node.js/npm installed, the equivalent standalone Pyright check is:

```sh
npm exec --yes --package=pyright@1.1.411 -- pyright
```

This version matches Pylance 2026.3.1. The repository configuration documents
the generated-binding exception; it does not disable checking handwritten
code. CI continues to use the original `mypy==1.9.0` pin.

Write a failing test before changing behavior. Confirm that it fails for the
missing behavior, implement the smallest change, then run the focused and full
suites.

## Go checks

Format only edited Go files while working:

```sh
gofmt -w PATH1.go PATH2.go
```

Use the local Linux/amd64 compile container for the complete build and safe
unit packages:

```sh
make celestial-make
docker run --platform linux/amd64 --rm \
    -v "$(pwd)":/celestial \
    --entrypoint sh celestial-make \
    -c 'gofmt -l . && go build ./... && \
go test ./pkg/orchestrator ./pkg/peer ./pkg/server && \
go test -c -o /tmp/virt.test ./pkg/virt'
```

No output from `gofmt -l` means formatting is clean.
## Shell checks

Use the interpreter declared by the first line:

```sh
sh -n quickstart/preflight.sh quickstart/validator/server.sh
bash -n builder/build-script.sh kernel/config.sh kernel/compile.sh
```

A syntax check does not execute the script. The preflight is safe to execute
remotely because it is intentionally read-only; build and runtime scripts have
real side effects.

## Configuration and topology checks

Run topology generation on the local workstation:

```sh
python3 satgen.py quickstart/quickstart.toml quickstart/quickstart.zip
unzip -l quickstart/quickstart.zip
```

This proves that configuration, orbit/contact calculation, and serialization
complete for the example. It does not start Firecracker or validate an
application inside a guest.

## Read logs from the right layer

**Topology generator:** progress and Python exceptions in the `satgen.py`
terminal.

**Coordinator:** registration, initialization, timestep, gRPC, and shutdown
messages in the `celestial.py` terminal.

**Worker:** backend choice, host networking, Firecracker, and orchestration
messages in the `celestial.bin` terminal.

**Guest:** `/celestial/out/<machine>.out` and `.err` on the worker.

**Guest files:** `/celestial/ce<machine>.ext4` after complete shutdown.

## Common failure evidence

**Missing command.** Run `command -v NAME` in the same local/remote shell.
Do not assume the tool installed in one environment exists in another.

**Permission or sudo failure.** Preserve the exact command and error. Project
file permissions may be yours to fix; `/dev/kvm`, sudo policy, or host network
permissions belong to the administrator.

**KVM failure.** Run `./quickstart/preflight.sh`; report its device checks.
Do not change KVM ownership or modules yourself.

**Wrong interface.** Inspect `ip route show default` on the actual worker and
pass that interface with `-network-interface`.

**gRPC port failure.** Port 1969 is the default coordinator/worker port. Check
whether an earlier worker is still listening and coordinate before stopping a
process you do not own.

**Missing kernel or image.** Compare TOML basenames with `ls -lh /celestial`.
The files must be installed on every worker that can host the machine.

**Firecracker startup failure.** Read the first worker error, not only later
coordinator timeouts. Check architecture, KVM, artifact format, and available
host resources in that order.

## Verification ladder

```text
focused unit test
→ full local unit suite
→ formatting/type/build checks
→ quickstart topology generation
→ local guest artifact build
→ authorized remote KVM run
```

Stop at the first failed rung and diagnose that boundary.
