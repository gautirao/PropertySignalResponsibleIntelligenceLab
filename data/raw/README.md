# data/raw/

Untouched, as-received research snapshots — never the live production database.

- Files here are exports/extracts taken at a point in time and given a
  version tag (see `research/experiment-conventions.md`), e.g.
  `ps-dataset-20260930-v001/`.
- Nothing in this folder is edited in place. If a snapshot turns out to be
  wrong, take a new versioned snapshot — don't patch the old one.
- Actual data files are gitignored (see `.gitignore`). This folder tracks
  only documentation about how a snapshot was produced (source, extraction
  date, filters applied, known caveats) — not the data itself.
- Do not commit production credentials, production DB connection strings,
  or raw PII here.
