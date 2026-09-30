# Experiment & Dataset Conventions

A simple, repeatable naming scheme so that any experiment, dataset, or
model referenced anywhere in this repo (code, reports, risk register) can
be traced unambiguously. This is deliberately lightweight — it is a
naming and record-keeping convention, not an experiment-tracking
platform. (A real tracking tool can be adopted in a later issue if the
lab outgrows this.)

## Naming scheme

```text
dataset:    ps-dataset-YYYYMMDD-v001
experiment: EXP-<topic>-YYYYMMDD-001
model:      MODEL-<task>-v001
```

- `YYYYMMDD` — date the snapshot was taken / the experiment was run.
- `v001` / `001` — zero-padded sequence number, incremented if you take
  more than one snapshot or run more than one experiment of that kind on
  the same day. Never reuse a number for a different snapshot/run.
- `<topic>` — short lowercase slug naming the research area, matching an
  `experiments/` subfolder where possible: `explainability`,
  `counterfactuals`, `fairness`, `neuro_symbolic`, `safety`, or
  `baseline`. Note: `experiments/baseline/` doesn't exist yet as of
  issue #1 — it's created when the first baseline model experiment is
  actually run (expected around issue #3), not before.
- `<task>` — short lowercase slug naming what the model predicts, e.g.
  `price`, `price-band`.

### Examples

```text
ps-dataset-20260930-v001          # first snapshot taken 2026-09-30
EXP-fairness-20261005-001         # first fairness experiment on 2026-10-05
EXP-fairness-20261005-002         # second one, same day
MODEL-price-v001                  # first baseline price model
```

## What every experiment must record

Every experiment, whatever its topic, should eventually record the
following (as a config file, a run log, or a short section at the top of
its report — format is up to the experiment, the fields are not
optional):

| Field | Meaning |
|---|---|
| Experiment ID | `EXP-<topic>-YYYYMMDD-NNN` |
| Dataset version | `ps-dataset-YYYYMMDD-vNNN` used as input |
| Code commit SHA | exact commit the experiment was run at |
| Configuration | hyperparameters / settings used |
| Random seed | for reproducibility |
| Model/library versions | e.g. Python version, key package versions |
| Metrics | the numeric results produced |
| Generated artefacts | what was produced (plots, model files, tables) and where they live (gitignored paths are fine, just say where) |
| Result | short summary of the outcome, including negative/failed results (see `governance/research-principles.md`, principle 7) |
| Limitations | what this experiment does *not* show, known caveats |

## Where this fits in the pipeline

```text
data snapshot (ps-dataset-...)
        → experiment (EXP-...)
                → model (MODEL-...), if applicable
                        → report (reports/), citing the EXP and dataset IDs
                                → governance/risk-register.md updated if a
                                  hypothesised risk becomes measured
```

This convention starts in issue #1 so that issue #2 (building the first
versioned dataset snapshot and Data Card) can use it immediately, rather
than inventing it under time pressure later.
