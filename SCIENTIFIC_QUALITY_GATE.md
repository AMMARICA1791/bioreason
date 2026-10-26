# Scientific Quality Gate — Scope, Evidence, and Failure Policy

BioReason's eight model-backed agent roles remain experimental. An intact message
chain and 39 successful software tests do **not** establish scientific accuracy.

## Failure that motivated the correction

In [the archived two-round discussion](https://github.com/AMMARICA1791/bioreason/actions/runs/40259589474),
the Inventor proposed improving **cervical cancer diagnosis** by improving
classification of **glaucoma retinal images**. The two topics appeared in
different retrieved records (PMC13650561 and PMC13639773). None of the
retrieved records was offered as evidence that retinal glaucoma images diagnose
cervical cancer. The proposal recurred during the next round.

This is an **unsupported cross-topic leap** on the available evidence, not
proof that an interdisciplinary research question can never be productive.

## Engineering corrections

1. **Evidence enrichment.** The Europe PMC client requests `resultType=core`
   metadata and includes sanitized, bounded abstract text when available.
   Abstracts are not equivalent to full-text study review.
2. **Conservative independent gate.** `src/bioreason/scientific_gate.py`
   cross-checks a deliberately small set of biomedical topic expressions,
   source identifiers and DOI references against the records retrieved.
   Claims containing multiple tracked topics without a single relevant
   joint record are marked `hold_for_independent_review`.
3. **Discussion-stage screening.** Every Inventor proposal is assessed; its
   screening result is explicitly passed to the Critic, Validator, Auditor and
   other downstream agents. Model agreement cannot override the deterministic
   hold.
4. **Learning from the identified mistake.** Unsupported topic bridges and
   topics absent from the evidence are saved as **allowlisted corrective codes**
   that guide future prompts, not as model-authored instructions.
5. **Publication decision.** If the latest proposal fails the gate, the
   deliberation record sets `publication_gate=hold_for_independent_review`
   and `final_tentative_candidate=null`. A tentative result is **not**
   scientific verification or authorization for clinical decisions.

## What is tested

- Regression: `glaucoma retinal imaging -> cervical cancer diagnosis` is held
  even when two genuine but separate paper IDs are cited.
- A single-topic proposal with a matching study ID remains *tentative*.
- Fabricated DOIs and citations to unrelated records are rejected.
- A joint-topic evidence record permits an appropriately *tentative* bridge.
- A role must receive the scientific screen in the following dialogue turn.
- A second-round revision can clear a previous hold without being called
  medically validated.
- Unknown topics receive a hold rather than invented certainty.
- An offline test verifies that Europe PMC core abstracts are sanitized.

These tests are intentionally narrow **regressions**, not accuracy or safety
benchmarks on representative biomedical claims. The topical expression set is
incomplete; the gate may be overly strict or miss scientifically invalid links
outside its vocabulary.

## Acceptance standard for a research-grade system

The next benchmark must use blinded independently expert-labelled hypotheses,
include both plausible interdisciplinary ideas and demonstrably unsupported
claims, and report false acceptance, false rejection, citation precision,
scientific error recurrence and abstention frequency before and after critique.

Until those data exist, outputs remain *research leads requiring independent
expert assessment*. The council does not diagnose conditions, advise treatment,
verify scientific originality, or establish causal findings.
