# Stakeholder Map

This map identifies who is affected by property-related AI experiments in
this lab — even though the lab itself does not (yet) ship anything to any
of these people. It exists so that every later experiment is designed
with these groups' interests in mind from the start, rather than as an
afterthought.

Stakeholders are grouped by how directly the system's outputs reach them.

- **Direct stakeholders** — interact with, or receive output from, a
  property-intelligence system directly.
- **Indirect stakeholders** — don't use the system themselves, but their
  professional decisions are shaped by people who do.
- **Societal stakeholders** — affected by the aggregate pattern of many
  decisions, even with no individual interaction with the system.

For each stakeholder: **interest**, **benefit**, **possible harm**,
**power/influence**, and **how the system could affect them**.

---

## Direct stakeholders

### Buyers
- **Interest:** find a fairly priced property that matches their needs;
  understand whether an asking price is reasonable.
- **Benefit:** faster, better-informed decisions; access to explanation
  of *why* a price or recommendation looks the way it does.
- **Possible harm:** over-trusting a confident-looking price estimate or
  explanation that is wrong; being steered toward or away from areas by
  a biased ranking; anchoring on a number that turns out to be based on
  stale or unverified data.
- **Power/influence:** low individually; collectively they are the
  demand side of the market and shape which listings get attention.
- **System effect:** decision support (estimates, explanations,
  comparisons) directly shapes what they search for, offer, and pay.

### Sellers
- **Interest:** get an accurate valuation and sell at a fair (or
  favourable) price without unnecessary delay.
- **Benefit:** pricing guidance grounded in data rather than guesswork.
- **Possible harm:** under- or over-valuation from a biased or stale
  model; unequal visibility of similar listings due to ranking bias.
- **Power/influence:** low individually, but they supply the listing
  data the system is trained and evaluated on.
- **System effect:** valuation and exposure/ranking outputs affect
  pricing strategy and how quickly/well a property sells.

### Estate agents / brokers
- **Interest:** tools that help them advise clients and close deals
  faster, without undermining their professional judgement or liability.
- **Benefit:** decision support, faster comparables, defensible
  explanations to share with clients.
- **Possible harm:** clients over-relying on model output and
  disregarding professional advice; the model being wrong in a way the
  agent is blamed for; deskilling over time.
- **Power/influence:** medium — they are professional intermediaries who
  can amplify or push back on system outputs.
- **System effect:** any explanation or valuation the system produces is
  likely to be relayed to buyers/sellers through the agent, so agent-facing
  outputs need to be interpretable and appropriately hedged.

### Property developers
- **Interest:** market intelligence for site selection, pricing, and
  phasing of new developments.
- **Benefit:** access to research-grade demand/price signal without
  needing in-house data science.
- **Possible harm:** using research outputs to justify commercially
  motivated pricing or site decisions beyond what the evidence supports;
  feedback loops where developer decisions (informed by the model) skew
  the very data future models are trained on.
- **Power/influence:** high — commercial actors with resources to act at
  scale on model output, and an incentive to see results skew favourably.
- **System effect:** aggregate-level outputs (trend/demand signal) could
  influence where and what gets built, which then reshapes the local
  market the model was trained on.

### Banks / lenders
- **Interest:** collateral valuation and risk assessment for mortgage
  lending.
- **Benefit:** an independent, data-driven cross-check on valuations.
- **Possible harm:** treating a research-grade estimate as a verified
  valuation; inheriting model bias into a decision (e.g. lending) that
  has legal/regulatory consequences (this system is explicitly not
  intended for that use — see `research-principles.md`).
- **Power/influence:** high — regulated institutions whose use of a
  model would carry real financial/legal weight.
- **System effect:** none intended in this lab; flagged here because
  misuse of research output for lending decisions is a realistic
  out-of-scope risk (see risk register).

### Lawyers / conveyancers
- **Interest:** accurate, verifiable facts about a property (title,
  price paid, planning status) — not predictions.
- **Benefit:** potentially faster triage of which transactions look
  unusual and warrant closer checking.
- **Possible harm:** a model's "explanation" being mistaken for a legal
  or factual determination it cannot provide.
- **Power/influence:** medium — gatekeepers of transactions, but not
  system users in the modelling sense.
- **System effect:** minimal direct effect; risk is indirect, via
  clients citing model output during a transaction.

---

## Indirect stakeholders

### Regulators / government
- **Interest:** market fairness, financial stability, data protection,
  anti-discrimination compliance.
- **Benefit:** none directly from this research lab; broader interest in
  well-governed property-AI practice in the sector.
- **Possible harm:** reputational/regulatory exposure for PropertySignal
  if research-stage findings or techniques were deployed without proper
  governance, or if protected-characteristic inference occurred.
- **Power/influence:** very high — can compel changes via law/regulation.
- **System effect:** none directly; this lab exists partly *because* of
  this stakeholder — to build the habits and evidence needed to satisfy
  future regulatory scrutiny.

### Neighbourhoods / local communities
- **Interest:** not having their area systematically mis-priced,
  stigmatised, or made a target of predatory investment activity because
  of a model's output.
- **Benefit:** better market transparency can, in principle, help a
  community understand its own property market.
- **Possible harm:** location-based bias in pricing/ranking becoming a
  self-fulfilling proxy for socioeconomic or demographic bias, even
  without any explicit protected attribute being used (see
  `research-principles.md` on proxy variables).
- **Power/influence:** low individually, no direct relationship with the
  system at all — this is exactly why proxy bias is dangerous: the
  people most affected have the least visibility into how they're
  affected.
- **System effect:** never interacts with the system directly; affected
  only through aggregate downstream decisions (pricing, lending,
  investment) that might reference model output.

---

## Societal stakeholders

### PropertySignal (the organisation)
- **Interest:** build defensible, trustworthy AI capability; avoid harm
  to users, regulatory exposure, and reputational damage; generate real
  learning that could inform future product decisions.
- **Benefit:** a safe space to learn what responsible-AI practice looks
  like before any of this touches production.
- **Possible harm:** reputational or legal harm if research practices
  leak into production without proper review, or if research findings
  are over-claimed as production-ready.
- **Power/influence:** very high — owns the data source, the roadmap,
  and the decision on whether/how research ever reaches production.
- **System effect:** this lab exists to reduce PropertySignal's own risk
  by surfacing problems in a research setting, before they could occur
  in a live product.

### Society / the housing market generally
- **Interest:** a property market that isn't distorted or made less fair
  by opaque automated decision-making.
- **Benefit:** better public understanding of how AI could responsibly
  be used (or should not be used) in property markets.
- **Possible harm:** normalising the idea that algorithmic price
  estimates are authoritative, contributing to market dynamics (e.g.
  herd pricing, feedback loops) that reduce overall market efficiency or
  fairness.
- **Power/influence:** diffuse, but collectively decisive over the long
  run (public trust, adoption, regulation).
- **System effect:** only ever indirect and long-term; named here as a
  reminder that "no direct user harm today" is not the same as "no
  societal effect ever."

---

## Why this matters for Milestone 1

Every experiment in `experiments/` should be checked against this map
before it's run: *who could be affected if this technique were ever
deployed, even if that's not the plan?* The risk register
(`governance/risk-register.md`) traces specific harms back to specific
stakeholders from this list.
