# data/synthetic/

Artificially generated data — including any synthetic protected/group
attributes used for fairness experiments.

## Layout convention

Same convention as `data/raw/` and `data/processed/`: a version-tagged
directory per generated dataset, containing a `README.md` (generation
method, seed, and intended use), `manifest.yaml`, `schema.json`, and a
gitignored `payload/` holding the generated data itself.

- Everything in this folder is synthetic by construction. It must be
  clearly labelled `research-only` / `synthetic` in filenames and in any
  accompanying documentation, and must never be presented as, or merged
  with, real PropertySignal user or transaction data.
- Synthetic protected characteristics (e.g. a simulated demographic
  attribute used to test a fairness metric) belong here, never inferred
  from real names, locations, or other proxies in `data/raw/` or
  `data/processed/` — see `governance/research-principles.md`. A
  synthetic attribute is a tool for testing a fairness *metric/method*
  in a controlled setting — it does not, by itself, prove anything about
  whether a real-world attribute (e.g. location) behaves as a proxy in
  real data. See R03 in `governance/risk-register.md`.
- `payload/` is gitignored; the README, manifest, and schema describing
  generation method/seed/intended use are tracked.
