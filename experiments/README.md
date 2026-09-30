# experiments/

Each subfolder is one stage of the Responsible AI pipeline described in
the top-level `README.md`. Every experiment inside them follows the
naming and record-keeping convention in
`research/experiment-conventions.md`.

- `explainability/` — model explanation methods (e.g. feature
  attribution, SHAP-style, rule extraction) applied to baseline models.
  Explanations are hypotheses about model behaviour, not ground truth.
- `counterfactuals/` — "what would need to change for a different
  outcome" style analysis, used to probe model behaviour and surface
  potential fairness/robustness issues.
- `fairness/` — group-level and individual fairness metrics, bias
  audits, and mitigation experiments. Uses synthetic protected
  attributes from `data/synthetic/` unless an authoritative real
  attribute source is documented.
- `neuro_symbolic/` — combining learned models with explicit rules or
  symbolic constraints (e.g. legal/regulatory logic), and comparing
  behaviour against the pure ML baseline.
- `safety/` — out-of-distribution detection, confidence calibration,
  and failure-mode analysis — where the model should say "I don't know"
  rather than produce a confident wrong answer.

Experiment outputs (model artefacts, run logs, generated plots) are
gitignored; only the experiment code, config, and written results are
tracked.
