# Risk Register

This register lists harms that are **plausible** given the kind of
system this lab is exploring (property price estimation, explanation,
ranking, and related models). Almost none of these have been measured
yet — the lab has not produced a model or dataset yet (that's issue #2
onward). Listing a risk here is a hypothesis to test for, not a finding.

**Status legend** (see also `governance/research-principles.md`):
- `hypothesised` — plausible based on domain knowledge of similar systems;
  no evidence from this lab yet.
- `measured` — an experiment in this repo has produced evidence for or
  against it (the relevant experiment ID should be added when this
  happens).
- `mitigation proposal` — an idea for reducing the risk, not yet
  implemented or validated.

As of this issue, **every row below is `hypothesised`**. Updating a row
to `measured` requires linking a specific `EXP-...` ID from
`research/experiment-conventions.md`.

| ID | Risk / harm | Affected stakeholder | Cause | Likelihood | Severity | Detection / evidence | Mitigation | Residual risk | Owner / reviewer |
|----|---|---|---|---|---|---|---|---|---|
| R01 | Inaccurate price estimate presented as confident fact | Buyers, sellers | Model trained on incomplete/stale features; point estimate shown without uncertainty | Medium | High | Compare model estimate vs. verified transaction price on held-out snapshot | Always report a range/interval, not a point value; label estimates as model output, not fact | Medium — estimates remain inherently uncertain | Lab maintainer |
| R02 | Misleading or overconfident explanation ("why" text implies causation it doesn't have) | Buyers, sellers, agents | Explainability method (e.g. SHAP-style) summarised as plain-language causal story | Medium | Medium | Manual review of generated explanations against known ground truth in synthetic experiments | Explicitly label explanation output as "model's local approximation," never "the reason" | Medium — explanation quality is an open research problem | Lab maintainer |
| R03 | Location acting as a proxy for a protected characteristic | Neighbourhoods, buyers, sellers | Postcode/area features correlate with demographic composition | Medium-High | High | Controlled fairness experiments using **synthetic** protected attributes can demonstrate the *mechanism* and validate a fairness metric/method against it; they cannot, by themselves, establish that a *real* locality is acting as a proxy for a *real* protected characteristic in real data — that claim remains unmeasured unless supported by an authoritative, lawful data source | Prohibit direct protected-attribute use; monitor outcome disparities by area even without using demographic features directly; do not present synthetic-experiment results as evidence about real-world proxy behaviour | Medium-High — proxy bias is very hard to fully eliminate, and harder still to measure in real data without protected-attribute access | Lab maintainer |
| R04 | Unfair ranking/exposure of listings (some properties systematically under- or over-shown) | Sellers, buyers | Ranking model optimised for a metric (e.g. click-through) that correlates with existing bias in historical data | Medium | Medium | Fairness experiments comparing exposure distribution across segments | Audit exposure distribution, not just accuracy, before any ranking logic is proposed | Medium | Lab maintainer |
| R05 | Stale data used for current-market decisions | Buyers, sellers, agents | Research snapshot not refreshed; model trained on an old market state | Medium | Medium | Compare snapshot date vs. experiment run date; distribution-shift checks (safety experiments) | Every dataset snapshot is versioned and timestamped; experiments must record which version they used | Low-Medium — mitigated by versioning discipline | Lab maintainer |
| R06 | False certainty when required documents/features are missing (model fills gaps silently) | Buyers, sellers, lenders | Missing-value imputation masks genuine data gaps (e.g. no verified sale ever recorded) | Medium | Medium-High | Track proportion of imputed vs. observed features per prediction | Surface missingness to the user/reader; avoid silent imputation in any user-facing output | Medium | Lab maintainer |
| R07 | Distribution shift between training snapshot and real-world use | Buyers, sellers, developers | Market conditions change (rates, demand) faster than snapshots are refreshed | Medium | Medium | OOD / safety experiments comparing new data against training distribution | Explicit OOD detection; models should flag low-confidence regions rather than extrapolate silently | Medium | Lab maintainer |
| R08 | Explainability/confidence output mistaken for ground truth ("model confidence ≠ correctness") | Buyers, sellers, agents, lawyers | High displayed confidence score doesn't necessarily track real-world accuracy | Medium | High | Calibration experiments (confidence vs. observed accuracy) | Calibrate and report confidence honestly; never present raw model confidence as a probability of being "right" | Medium | Lab maintainer |
| R09 | Commercial influence on pricing narrative (seller/developer pressure to skew output) | Buyers, society | Party with commercial interest requests/uses model output selectively to support a preferred narrative | Low (within this lab; higher if ever productionised) | Medium | N/A in research phase — flagged as a design constraint | Keep all lab outputs clearly labelled "research, not advice"; no mechanism in this lab for external parties to request custom output | Low (research-only), would rise if reused externally without this label | Lab maintainer |
| R10 | Feedback loops (model output changes behaviour, which changes the data the next model learns from) | Society, neighbourhoods, developers | E.g. developers using research trend signal to decide where to build, which then shifts the market the next snapshot observes | Low (within this lab), Medium (if findings are acted on) | Medium | Compare successive dataset snapshots for signs the market moved in the direction of prior predictions | Document this risk explicitly in any report that shares findings externally | Medium — hard to detect from inside a single lab | Lab maintainer |
| R11 | Privacy leakage from research snapshots (re-identification of individuals from listing data) | Buyers, sellers | Combination of quasi-identifiers (address, price, date) makes individuals re-identifiable even without names | Medium | High | Manual review of snapshot fields for quasi-identifiers before any snapshot is taken (issue #2) | Snapshot process must minimise/mask direct identifiers; access to raw snapshots restricted to the lab | Medium — full anonymisation of address-linked data is genuinely hard | Lab maintainer |
| R12 | Model misuse outside its intended research domain (e.g. treated as a lending or legal decision tool) | Banks/lenders, buyers, sellers | No technical barrier stops a research artefact from being copied into a different, higher-stakes context | Low (within this lab) | Very High if it occurred | N/A — preventive control, not detectable after the fact | Explicit "research-only, not for lending/legal/production decisions" labelling in every report and model artefact | Low-Medium — labelling is necessary but not sufficient | Lab maintainer |
| R13 | Automation replacing professional/legal judgement (agents or buyers skip professional advice because "the model said so") | Buyers, agents, lawyers/conveyancers | Confident-sounding automated output is easier to act on than seeking paid professional advice | Medium | Medium-High | N/A in research phase — design/communication risk | Every output explicitly states it does not replace professional (legal, financial, valuation) advice | Medium | Lab maintainer |

## Notes

- This list is not exhaustive. New risks discovered during experiments
  (issues #2+) should be appended with a new ID (`R14`, `R15`, ...), not
  inserted mid-sequence, so existing IDs stay stable references.
- "Owner / reviewer" is `Lab maintainer` for all rows at this stage
  because the lab has one contributor; this column exists so the
  structure is ready once more people are involved.
