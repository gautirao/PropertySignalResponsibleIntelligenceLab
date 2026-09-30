# data/processed/

Cleaned, feature-engineered, or otherwise transformed versions of a
`data/raw/` snapshot, produced by documented, re-runnable code.

## Layout convention

Follows the same convention as `data/raw/`: a version-tagged directory
per output (e.g. `ps-dataset-20260930-v001-processed/`) containing a
`README.md`, `manifest.yaml` (recording the exact `data/raw/` snapshot
version and code commit SHA it was derived from), `schema.json`, and a
gitignored `payload/` holding the actual transformed data.

- Every processed dataset is traceable back to the exact `data/raw/`
  snapshot version and the code commit that produced it — record both
  in the manifest, not just in a commit message.
- Processed data is still a research artefact, not production data — it
  inherits every restriction in `governance/research-principles.md`
  (no protected-characteristic inference, listing price ≠ verified
  transaction price, etc.) and the sensitivity caveat in
  `data/raw/README.md` (de-identified is not the same as safe to
  publish).
- `payload/` is gitignored; the manifest, schema, and README describing
  the transformation are tracked.
