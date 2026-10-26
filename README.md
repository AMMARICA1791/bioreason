# BioReason

**Open science research council — evidence-first, multi-disciplinary, experimental**

BioReason's mission is to **explore scientific research across fields, identify potentially useful connections, propose falsifiable hypotheses, challenge them through an eight-role council, and turn promising questions into testable next steps.** Outputs remain unvalidated research leads. Eight prompts on pretrained local models are not eight independently trained scientific experts.

## Problem and scope

The goal is not to optimize biomedical citation-formatting tests. Biomedical experiments exposed important defects and are now retained as an **evaluation laboratory**, while the science-wide track scouts additional fields using public Crossref journal metadata. New connections must cite actual studies, describe uncertainty, and explicitly separate a hypothetical mechanism from demonstrated evidence. Prior-art originality and scientific effectiveness are **not yet established**.

## Active research tracks

| Track | Source and role | Actual evidence |
| --- | --- | --- |
| **Science-wide scouting** (new main research direction) | [Four science fields, live Crossref DOIs, eight audited software roles](.github/workflows/science-scout.yml) | [Verified live run](https://github.com/AMMARICA1791/bioreason/actions/runs/40340168406) |
| **Science-wide model council** (experimental) | [Real local-model role dialogue, one revision and source gate](.github/workflows/open-science-council.yml) | Model-run artifacts must be inspected before claiming an improved hypothesis |
| **Biomedical regression laboratory** (retained) | [Europe PMC trials](.github/workflows/model-council.yml), [scientific quality regression cases](evaluation/scientific_regression_cases.json) | Historical positive and negative software tests; **not** the mission's domain limit |

**The current four-field selection is a pilot, not a permanent science whitelist.**
Reports clearly differentiate retrieving a paper, stating a testable hypothesis, verifying an experiment, and proving originality; none can substitute for another.

## Implemented pipeline

| Role | Current behavior |
| --- | --- |
| Scout | Fetches up to 25 Europe PMC metadata records, or reads local JSON |
| Analyst | Counts repeated words in **titles**, not full-text findings |
| Inventor | Poses a tentative question from repeated title terms |
| Critic | Flags title-only inference, causal uncertainty, and missing DOIs |
| Validator | Counts records with source and ID; **does not verify findings** |
| Builder | Records pipeline execution |
| Auditor | Records that limitations were reported |
| Coordinator | Combines results into JSON |

**Architecture disclosure:** The default CLI executes eight bounded deterministic agent roles with hash-linked handoffs and an explicit audit. An opt-in GitHub Actions workflow can give **each of the eight roles its own inference turn on the same locally loaded Qwen model**, chaining proposals through the council. The roles are not eight separately hosted or trained models. Deterministic validation gates remain in force; model suggestions never establish scientific facts. Scheduled runs now include two additional full-eight-role deliberation rounds and a bounded record of correctable errors carried between successful runs via GitHub Actions cache. This is **prompt-level procedural adaptation**, not model training or proven accuracy improvement. Scientific validation and continuous real-time monitoring remain unimplemented.

## Run

Python 3.10+; deterministic mode has no runtime third-party dependencies. The separate optional local-model workflow installs PyTorch and Transformers on GitHub Actions.

```bash
PYTHONPATH=src python -m bioreason 'CRISPR AND cancer' --limit 10
PYTHONPATH=src python -m bioreason 'example query' --input examples/papers.json
PYTHONPATH=src python -m unittest discover -s tests -v
```

The online command requires Europe PMC access. Offline fixtures and unit tests require no network. The repository currently has **100 offline tests**, including biomedical cross-topic regression tests, source/DOI checks, eight-role inference-adapter coverage, discussion chaining, and safe memory replay; GitHub Actions has executed the Python 3.10–3.13 test matrix successfully. Passing software tests does **not** establish scientific accuracy.

Input: JSON array of objects with `title`, `id`, `source`, `doi`, optionally `year`. Output: JSON printed to stdout. Example records are synthetic.

## Council dialogue and corrective memory

The [model-backed council workflow](.github/workflows/model-council.yml) first executes all eight roles on ten live Europe PMC bibliographic records, then conducts **two further conversation rounds** in which all eight roles respond to recent colleagues' replies. The complete dialogue uses hash-linked messages and is exported as a GitHub Actions artifact.

After each reply, deterministic checks flag three narrowly defined **process issues**: missing source identifiers in roles expected to cite records, DOI values absent from the retrieved records, and verbatim unchanged revisions. Only those issue **codes** are carried into later prompts as corrective lessons; model-generated prose is never stored as trusted future instructions. A JSON lessons file is restored and saved using GitHub Actions cache after successful cycles. Cache data may be evicted; every run additionally publishes the state in its artifact. Improvement in scientific quality is **not** assumed or claimed, and this procedure does **not** update Qwen weights.

## Scientific quality correction

A model-generated cross-topic proposal previously linked cervical cancer
diagnosis to glaucoma retinal photographs without joint source evidence.
BioReason now applies an independent **evidence-coherence screening gate**
to every Inventor reply, passes blocking reasons to reviewers, and holds
unsupported links for human scientific assessment. Europe PMC core records
provide bounded abstract excerpts where available. A set of ten synthetic
positive/negative regression cases exercises both the false-release and
over-hold paths (10/10 cases passed in [GitHub Actions](https://github.com/AMMARICA1791/bioreason/actions/runs/40263193884)); this is **not** a measure of clinical accuracy.

See [Scientific Quality Gate](SCIENTIFIC_QUALITY_GATE.md) for scope,
limitations, counterexamples, and the future blinded benchmark.

## Focused literature and falsifiable proposals

The current quality pilot draws a **single coherent biomedical topic** (cervical
cancer plus AI research) from Europe PMC. If the 2026 date window has too few
traceable records, the collector extends the date window to 2025–2026 rather
than combining unrelated medical specialties or inventing evidence.

[Focused-source proof](https://github.com/AMMARICA1791/bioreason/actions/runs/40314598414)
retrieved **nine relevant live records**. This validates retrieval coherence,
not scientific causality. The Inventor must pose a narrow research question
supported by at most three actually supplied source identifiers, or abstain.
Catalogue-style questions about general AI applications are held by the
independent quality gate.

## Direct test of whether peer critique adds value

[The predeclared experiment](EVALUATION_PROTOCOL.md) compares one Qwen
Inventor reply without peers to the first and last council Inventor replies
on the **same live bibliography and model**. [A separate verification
script](scripts/evaluate_run.py) independently recomputes all proxy scores
from the archived, hash-linked trace and **reports regressions as well as
improvements**. It never labels machine-readable formatting as scientific
truth; the multi-agent arm uses more inference than the solo arm.

An actual prior-council trace revealed that the rolling four-message window
dropped the Critic's earlier objection before Inventor's revision. The
[deliberation logic](src/bioreason/deliberation.py) now delivers the actual
earlier objection, validation feedback and exact blocking reasons **directly**
to Inventor for a new attempt. Sources are suggested for review rather than
silently inserted into the model's answer. The regression is tested.

## First experimental result (negative, not hidden)

The first [actual Qwen solo-versus-council comparison](https://github.com/AMMARICA1791/bioreason/actions/runs/40316126789) found **no improvement**: a solo model response scored **one proxy point higher** than the final council proposal on the same literature; none of the three proposals cited a usable record ID, so all were held. The original metric mistakenly credited an uncited paper's mere presence in the bibliography. After fixing the metric to require an **actually cited supporting paper**, the comparison was **3/6 solo, 2/6 first council, 2/6 last council**. Both original and corrected interpretations are preserved in [RUN_EVIDENCE.md](RUN_EVIDENCE.md).

The prior Critic objection was also dropped from the next Inventor's rolling context. The [handoff fix](src/bioreason/deliberation.py) explicitly delivers reviewer objections and gate reasons to the next Inventor turn, but a new real-model evaluation is required before claiming it improves answers.

## Critic accountability and revision continuity

A later actual [council trace](https://github.com/AMMARICA1791/bioreason/actions/runs/40316791405)
found **no solo-to-council proxy advantage** (4/6 in each arm under the
then-current score) and showed that Critic frequently rephrased Inventor's
question without exposing the missing source citation. This does not qualify
as a substantive peer challenge.

[The correction](src/bioreason/peer_review.py) now generates an auditable,
deterministic list of *specific* obligations from the independent proposal
screen (e.g. absent source ID, unsupported disease bridge). Critic receives
those challenges directly. Its answer is separately audited as either
an explicit objection, a superficial review, or a case with no mandatory
blocking criticism. Independently generated objections continue to reach
Inventor even when Critic falls short. [The independent run evaluator](scripts/evaluate_run.py)
reports Critic failures alongside the solo/council result.

A compact focused paper excerpt and its **exact ID** are shown in both solo
and council Inventor prompts, while revision additionally receives prior
Critic objections and source failures. **The code never attaches citations
automatically to a model's prose**, and scientific validation is not claimed.
Software tests verify the handoffs; live-model improvement remains an
experimental question.

## Valid abstention when source support is insufficient

Professional research behavior sometimes means **not proposing a hypothesis**.
The source gate now treats the exact response `ABSTAIN: insufficient evidence`
(or a small set of equivalent unambiguous phrases) as an explicit abstention.
Inventor is not penalized for lacking a citation when it makes no research
claim. Abstentions are separately reported and are never considered
scientifically validated or publishable research conclusions. Any response
that mixes an abstention with an unsupported DOI or a new factual claim
still goes through the normal gate.

[69 offline tests and ten synthetic regression cases](https://github.com/AMMARICA1791/bioreason/actions/runs/40319788740)
verify this behavior and the revised critique handoff on four Python
versions. The updated real-model performance is evaluated separately.

## Model copying an instruction template: detected and blocked

[Real Qwen run 40319089691](https://github.com/AMMARICA1791/bioreason/actions/runs/40319089691)
exposed a negative failure mode: both the solo model and the council reproduced
unfilled examples such as `[specific method]` and `[measurable endpoint]`,
with **2/6** proxy points each and no scientific approval. We removed literal
question templates from generation prompts and added a gate rule rejecting
unresolved placeholders in outputs. This is backed by focused unit tests, not
by a demonstrated live model improvement.

## No-regression safeguard for human review leads

An actual [Qwen experiment](https://github.com/AMMARICA1791/bioreason/actions/runs/40320610137)
found the solo answer included a retrieved study identifier (`42380812`)
but both council Inventor replies omitted it. The result was a **negative
solo-versus-council comparison** (recorded 5/6 solo versus 2/6 council).
After correcting endpoint detection to recognize plural `detection rates`,
replaying the *same verbatim transcripts* gives **6/6 solo versus 3/6
council**, preserving the negative **three-point difference**. Neither
result establishes clinical accuracy; [full provenance and
correction](RUN_EVIDENCE.md) are retained.

A new conservative `solo_vs_council.selection` chooses the best
*evidence-screened tentative research lead for human review only*: it
retains the **highest-scoring screened** tentative lead across solo,
first-round council and final council replies, breaking ties in favor
of the earlier screened reply. It returns no lead if all three fail. The independent evidence
verification script prevents changing the selected source without
detecting tampering. This safeguard **does not** make council reasoning
more accurate and **does not publish** any biomedical conclusion.

[100 passing offline tests](https://github.com/AMMARICA1791/bioreason/actions/runs/40331546234)
on Python 3.10–3.13 include replay of the original Qwen failure
and checks for non-regression and tampering.

## Measured model capability and corrected source checking

In a [controlled eight-inference probe](https://github.com/AMMARICA1791/bioreason/actions/runs/40326374533),
Qwen2.5-1.5B produced stronger **initial** sourced questions than Qwen2.5-0.5B
on two fixed records, but **both models degraded during revision**.
An [isolated eight-role pilot](https://github.com/AMMARICA1791/bioreason/actions/runs/40327497545)
used 1.5B for Inventor with seven default 0.5B peers. The final council
revision still lost a legitimate paper identifier and underperformed the
solo reply; default production and persistent memory settings were unchanged.

The pilot also revealed a **real deterministic verification bug**:
a genuine DOI wrapped as `[DOI: 10.1186/s12885-026-16427-y]` was
misread as fabricated. Fixed DOI normalization and exact-transcript
regressions establish corrected *posthoc* proxy scores of **5/6 solo,
5/6 first council, 3/6 final council**; this does not validate scientific
accuracy or turn the final revision into a success.

[Run evidence](RUN_EVIDENCE.md) reports historical original scores,
correction details and artifact links without deleting negative results.
[The model-capability protocol](MODEL_CAPABILITY_PROTOCOL.md) preserves
its outcome criteria and full initial/revised responses.

## More precise citation integrity and reviewer accountability

A concrete provenance hole has been closed: the evidence gate now rejects
proposals that combine a legitimate DOI from **one** paper with a legitimate
record ID from a **different** paper. It requires each supplied DOI to belong
to a cited source identifier and still accepts correctly paired genuine
citations. The correction is covered by regression tests using real Europe
PMC identifiers `42380812` and `42802541`.

Critic replies are also no longer considered a substantive source objection
merely because they include generic negative wording about a paper. A
missing-citation failure requires a source-related objection, and a
DOI/record mismatch requires an identity-specific objection. This remains a
**lexical review audit, not expert scientific validation**.

[100 tests and ten synthetic scientific regressions passed](https://github.com/AMMARICA1791/bioreason/actions/runs/40331546234)
on the four supported Python versions. Actual model dialogue still has
not demonstrated that the council improves its Inventor questions after peer
criticism; the best screened proposal is preserved for human review only.

## Evidence and provenance

| Claim | Supporting reference | Not established |
| --- | --- | --- |
| Europe PMC provides a literature search API | [1] | BioReason scientific accuracy |
| OpenAlex provides scholarly metadata APIs | [2] | An implemented OpenAlex integration |
| Agent-based workflows are used in biological research | [3] | BioReason originality or effectiveness |
| Multi-agent bioinformatics is an active research field | [4] | Commercial demand |

### References

1. Europe PMC, *RESTful Web Service*: https://europepmc.org/RestfulWebService
2. OpenAlex, *API documentation*: https://docs.openalex.org/
3. *A multi-agent system for automating scientific discovery*, Nature (2026): https://doi.org/10.1038/s41586-026-10652-y
4. *The next paradigm in bioinformatics: a review of multi-agent systems and foundational models for end-to-end scientific discovery*, Briefings in Bioinformatics (2026): https://doi.org/10.1093/bib/bbag245

These are background references, **not BioReason experimental results**. Bibliographic links and publication details should be independently checked before relying on them in a scientific publication.

## Known limitations

- Title co-occurrence is a weak signal, not a mechanism, causal relationship, or discovery.
- No full-text review, study-quality assessment, retraction checks, or patent/novelty search.
- A DOI can be absent from a valid record. Source plus ID indicates traceability, not scientific correctness.
- No measured performance, accuracy, customer demand, time savings, or financial return.
- Online retrieval depends on the Europe PMC API and network availability.
- Current implementation is a baseline, not a production research assistant.

## Evaluation roadmap — proposed, not completed

1. Freeze a dated, DOI-linked bibliography and predefined research questions.
2. Obtain blinded independent assessments of relevance, traceability, and unsupported claims.
3. Compare manual review, this deterministic baseline, a single-model approach, and a genuine multi-agent implementation using the same source set.
4. Publish prompts, datasets, code revisions, costs, timing, failures, and negative results.
5. Consider commercial pilots only after researchers demonstrate utility or willingness to pay.

## Status and governance

**Implemented:** Europe PMC metadata retrieval, offline JSON input, executable eight-role deterministic council, two rounds of multi-agent discussion, allowlisted corrective memory, hash-linked message trace, audit checks, unit tests, and scheduled GitHub Actions runs. A separate CPU workflow runs an openly available local Qwen model and archives the model outputs alongside the handoff record. [Verified live-data + three model-backed roles run](https://github.com/AMMARICA1791/bioreason/actions/runs/40258295368).

**Optional model-backed reasoning:** All eight roles support per-role model suggestions through an explicitly configured OpenAI-compatible endpoint. No credentials are bundled; opt-in remote calls require `BIOREASON_MODEL_ENDPOINT`, `BIOREASON_MODEL_NAME`, and optionally `BIOREASON_MODEL_API_KEY`. Send only metadata appropriate for a trusted endpoint. Alternatively, the GitHub Actions [local model council](https://github.com/AMMARICA1791/bioreason/actions/workflows/model-council.yml) uses CPU-only Qwen without a paid API key and attempts real Europe PMC collection. The offline deterministic CLI is the default. **Not implemented:** separately hosted autonomous models, full-text verification, scientific originality/patent review, a product service, billing, or proved commercial usefulness. The `--legacy` flag retains the original flat pipeline.

Research use only. Do not use generated questions for diagnosis, treatment, laboratory safety, or claims of novelty. Contributions should include reproducible cases, citations, and counterexamples.

**License:** not selected. This repository is publicly readable but is **not licensed for redistribution or reuse** until a license is explicitly added.
