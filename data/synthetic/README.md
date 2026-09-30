# data/synthetic/

Artificially generated data — including any synthetic protected/group
attributes used for fairness experiments.

- Everything in this folder is synthetic by construction. It must be
  clearly labelled `research-only` / `synthetic` in filenames and in any
  accompanying documentation, and must never be presented as, or merged
  with, real PropertySignal user or transaction data.
- Synthetic protected characteristics (e.g. a simulated demographic
  attribute used to test a fairness metric) belong here, never inferred
  from real names, locations, or other proxies in `data/raw/` or
  `data/processed/` — see `governance/research-principles.md`.
- Actual data files are gitignored. Document generation method, seed, and
  intended use here.
