# governance/

The non-code artefacts that make this lab's work responsible-AI-aware
rather than just ML-accuracy-aware.

- `stakeholder-map.md` — who is affected by property-intelligence AI,
  directly or not, and how.
- `risk-register.md` — concrete, hypothesised harms, who they affect,
  and how they'd be detected and mitigated.
- `research-principles.md` — the binding rules every experiment must
  follow (no production DB access, no protected-attribute inference,
  versioned snapshots, reproducibility, etc.).

These three documents should be readable and understandable by someone
who has never opened the code — that's the point. If an experiment's
design can't be explained by referring back to these documents, the
experiment needs more thought before it's run, not after.
