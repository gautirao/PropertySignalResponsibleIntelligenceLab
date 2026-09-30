# data/raw/

Untouched, as-received research snapshots, taken via an approved
read-only export — experiments never hold a live connection to the
production database (see `governance/research-principles.md`).

## Layout convention for a snapshot

Each snapshot gets its own version-tagged directory (see
`research/experiment-conventions.md`), e.g. `ps-dataset-20260930-v001/`,
containing:

```text
data/raw/ps-dataset-20260930-v001/
  README.md          what this snapshot is, how/when it was taken, known caveats
  manifest.yaml       source, extraction date, filters/queries applied, row/field counts
  schema.json          field names, types, and what each one means
  checksums.txt        hashes of the payload files, to detect drift/corruption
  payload/              the actual data files — gitignored, never committed
```

- **`payload/` is gitignored.** The data itself never goes into version
  control. Everything else above it — the README, manifest, schema, and
  checksums — is provenance/documentation and **is tracked**, so a
  snapshot's existence, shape, and history are reviewable without
  needing the data itself.
- Nothing in this folder is edited in place. If a snapshot turns out to
  be wrong, take a new versioned snapshot — don't patch the old one.
- A snapshot may still contain sensitive information even after
  minimisation/de-identification (see R11 in
  `governance/risk-register.md`). "De-identified" is not the same as
  "safe to publish" — access to `payload/` content is restricted to the
  lab, not assumed safe for wider sharing.
- Do not commit production credentials, production DB connection
  strings, or raw PII here — not even inside `payload/` (which is
  gitignored, but gitignoring is a safety net, not the control).

The exact process for producing a snapshot is defined in issue #2; this
file only fixes the layout convention so #2 has somewhere to write to.
