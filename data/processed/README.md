# data/processed/

Cleaned, feature-engineered, or otherwise transformed versions of a
`data/raw/` snapshot, produced by documented, re-runnable code.

- Every processed dataset should be traceable back to the exact
  `data/raw/` snapshot version and the code commit that produced it.
- Processed data is still a research artefact, not production data — it
  inherits every restriction in `governance/research-principles.md`
  (no protected-characteristic inference, listing price ≠ verified
  transaction price, etc.).
- Actual data files are gitignored. Keep notes here on what
  transformation each processed dataset represents.
