# 10. Running Experiments

A reproducible QUEST experiment connects one scientific question to one set of
controlled inputs, one execution record, and one interpretation. Start small;
scale is useful only after correctness is visible.

## 1. State the question and comparison

Write one sentence naming the independent change and outcome. For example:

> How does reducing a ground station from two antennas to one change the time
> between a selected contact and validator reachability in this topology?

Do not change constellation size, antenna count, activation, workload, and run
duration together unless the experiment explicitly studies their interaction.

## 2. Copy the known-good input

```sh
cp quickstart/quickstart.toml antenna-one.toml
```

Change only the factor under study. Keep experiment-specific configurations
near the study artifacts rather than accumulating them in the platform root.
There is no required generic experiment directory; choose a location that the
project supervisor approves.

## 3. Record provenance before building

On the local build workstation, capture at least:

```sh
git rev-parse HEAD
python3 --version
go version
docker version
```

On the remote VM, record `git rev-parse HEAD`, `python3 --version`,
`go version`, and `firecracker --version`. Do not install or invoke Docker
there.

Also record the full Tom's Obvious Minimal Language (TOML) input, workload
source, guest image build command, kernel config/filename, host class/resources,
and whether the worker used eBPF or netem. Do not publish the assigned HPI
hostname or credentials.

## 4. Validate and build inputs

Generate a fresh topology archive from the exact configuration:

```sh
. .venv/bin/activate
python3 satgen.py antenna-one.toml antenna-one.zip
```

Build only artifacts affected by the study. Generated ZIPs, binaries, kernels,
images, overlays, logs, CSVs, and graphs remain untracked.

## 5. Run from a clean runtime boundary

Before starting:

- confirm no earlier worker/coordinator is running;
- confirm required `/celestial` artifacts have the intended checksums;
- confirm enough disk, memory, process, and file-descriptor capacity;
- record the default interface and backend;
- run the read-only preflight;
- keep the same code commit and configuration on coordinator and worker.

Start worker first, then coordinator. Save both logs. Record whether the run
ended normally, was interrupted, or failed; a failed run is not a completed
sample.

## 6. Collect raw evidence before analysis

Preserve raw coordinator/worker/guest logs and workload output before creating
plots or summaries. Read overlays only after complete shutdown and mount them
read-only. Associate each result with:

- run identifier and timestamp;
- Git commit;
- configuration file or hash;
- guest image/kernel identifier or hash;
- host/backend information;
- completion/failure status.

Do not silently replace a missing observation with a successful zero, and do
not pool failures with completed latency samples without an explicit rule.

## 7. Analyse the named outcome

Run the analysis version stored with the study. Keep units on every metric.
Report sample count, missing/failed count, and the aggregation used. Separate
modeled values from measured guest values and separate code facts from
interpretation.

For the validator, configured path delay is a one-way model in microseconds;
ping is a guest-observed round trip in milliseconds. The quickstart analysis
converts and compares them, but its thresholds are diagnostics rather than a
scientific accuracy guarantee.

## 8. Repeat and compare fairly

Recreate the runtime boundary for each sample. Randomize or alternate method
order when host drift could bias one method. Hold topology, input observations,
workload semantics, result completeness, and user-visible endpoint constant
when the causal question is placement or processing strategy.

## 9. Package the study, not the platform

Commit small source/configuration/analysis inputs in the location agreed for
the student project. Store large or sensitive raw artifacts in approved
storage with stable references. Do not add generated evidence, private host
details, or one cohort's ad hoc launcher to the reusable QUEST root by default.

Checkpoint: another student should be able to identify the exact code,
configuration, guest artifacts, environment assumptions, raw outputs, and
analysis that produced every reported figure.
