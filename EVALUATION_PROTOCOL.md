# Predeclared evaluation protocol: Does peer critique help?

BioReason must not assert that eight simulated roles improve scientific insight merely
because GitHub Actions completes or more model tokens are generated.

## Experimental unit

A *run* uses **one frozen response model** (Qwen/Qwen2.5-0.5B-Instruct),
**one Europe PMC bibliography** retrieved once, one focus query, and
deterministic generation. All candidate texts and source records are saved
in the downloadable workflow artifact. Each run compares:

- **Solo:** one Inventor inference, same model and original bibliography, with no
  dialogue, role outputs, remembered lessons, or peer critiques in its input.
- **Council first:** the Inventor's proposal in the first discussion round,
  after the initial eight-role baseline and the first two discussion messages.
- **Council last:** the Inventor's proposal during the second discussion round,
  after responses and recorded objections from the rest of the council.

Each candidate passes **the same independent deterministic gate**.
No arm receives different search results or different model weights.
However, the arms **do not have equal inference budgets or identical prompt
contexts**, so a higher score alone cannot prove that dialogue caused it.

## Predeclared machine-measurable proxies

The evaluator assigns **one point each** for these six Boolean checks:

1. Has an interrogative question mark.
2. Includes an exact ID from the retrieved set.
3. That cited record includes the relevant recognized biomedical topic(s).
4. Passes the limited independent evidence-coherence gate without a blocking
   reason.
5. Names a measurable clinical research endpoint, e.g. sensitivity/specificity.
6. Names a comparator or baseline.

Total: 0–6. The evaluator **must** report both positive and negative changes:

- `solo_to_last_proxy_delta = last - solo`
- `first_to_last_proxy_delta = last - first`
- Whether the first and last proposals have different actual text.
- Whether the final proposal is **held** for independent expert assessment.

**Automated success on proxy only:** final score exceeds both solo and first
scores, the final proposal is not held, and the first-to-last text changed.

**Automated negative result:** final score is lower or equal to either
comparator, or the final evidence gate holds it. All results are published;
a negative finding is not retried with a different sample and reported as
if it were the original. Machine success is still **not** scientific success.

## Scientific improvement is currently NOT demonstrated

The gate uses an intentionally incomplete lexicon. It cannot establish
causality, clinical truth, research novelty, study quality, or consistency with
full-text evidence. The model is small, and role prompts do not create
independent expert reasoning agents.

Before claiming better **science** instead of better formatting, freeze
a sufficiently diverse benchmark (at least 20 independently labelled cases);
compare solo, same-budget single-model revision and multiple-agent reasoning
with matching token budgets; blind domain experts to the system arm; and
publish false acceptance, false rejection, unsupported facts, abstentions,
citation fidelity and inter-reviewer agreement.

The system continues to default to **independent scientific review required**
for any research lead. No clinical recommendations or patent claims are produced.

## Reproducibility

The run uses `scripts/model_council.py`, comparison implementation
`src/bioreason/comparison.py`, and 51+ offline tests plus ten synthetic
regression examples. The actual model and comparison evidence are emitted to
`artifacts/model-council.json` under `solo_vs_council`. Preserve the
GitHub run ID and git revision when interpreting results.

This protocol was authored **before** interpreting the first live run that
includes the solo control.
