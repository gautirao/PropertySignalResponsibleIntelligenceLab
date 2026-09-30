# data/

Versioned research snapshots. Every dataset used anywhere in this repo
has an explicit version identifier (`ps-dataset-YYYYMMDD-vNNN`, see
`research/experiment-conventions.md`) and lives here, not in an
experiment folder or a notebook's working directory.

```text
data/
├── raw/        first fixed extraction from a source (for the first
│               dataset: the dedicated, read-only PropertySignal
│               production export — see tools/dataset/export_snapshot.py)
├── processed/  cleaned/minimised/feature-prepared derivatives of a raw
│               snapshot, produced by documented, re-runnable code
│               (see tools/dataset/prepare_dataset.py)
└── synthetic/  artificially generated data, including synthetic
                protected/group attributes for fairness experiments
```

Each subfolder's own `README.md` documents its layout convention in
detail. In all three, a dataset version is a directory containing a
`README.md`, `manifest.yaml`, `schema.json`, and a **gitignored**
`payload/` — the payload never reaches Git; the provenance metadata
describing it always does.

## Before using any dataset here

Read the relevant snapshot's `README.md` and `manifest.yaml` first, then
`governance/data-card-v1.md` for the first dataset
(`ps-dataset-20260930-v001`). A snapshot being de-identified does not
make it anonymous or safe to publish — see
`governance/research-principles.md` and R11 in
`governance/risk-register.md`.

No experiment, notebook, or analysis code anywhere in this repository
opens a production database connection. The one exception is the
dedicated export tooling in `tools/dataset/`, which writes a versioned
snapshot here and has no other responsibility.
