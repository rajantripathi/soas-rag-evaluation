# Dataset Quality Audit

This audit cross-checks an internal v4 QA sample, the original v1 seed set on Isambard, the deterministic v4 expansion logic in `scripts/build_manual_eval_v4.py`, and the scoring/generation code in `src/evaluation.py` and `src/generation.py`. The answer-bearing source files are not part of the public branch pending source and license clearance.

## Gold Answer Quality

### Overlap Between v1 and the Internal v4 Sample

The internal v4 sample contains 25 items. Of these, 23 are seed items that also appear in v1:

`en_00`, `en_01`, `en_02`, `en_03`, `en_04`, `en_05`, `en_06`, `en_07`, `en_08`, `en_09`, `en_10`, `en_11`, `en_12`, `en_19`, `uz_00`, `uz_01`, `uz_02`, `uz_03`, `uz_04`, `uz_07`, `uz_08`, `uz_09`, `uz_10`.

The two non-overlapping sample items are `en_20` and `en_23`.

### Wikipedia Navigation Artifacts in v1 Gold Answers

The v1 seed set contains obvious Wikipedia or template artifacts for at least these overlapping items:

- `en_01`: the answer begins with a language-series navigation template.
- `en_03`: the answer begins with coordinate metadata.
- `en_05`: the answer begins with a religion-series navigation template.
- `en_12`: the answer contains a long page-navigation template.
- `en_19`: the answer begins with a science-series navigation template.

These are not concise answers. They are page-level navigation or template dumps.

### Raw Passage Dumps in v1

Several v1 answers are unedited Wikipedia passage dumps rather than benchmark-quality gold answers:

- `en_01`
- `en_05`
- `en_12`
- `en_19`

These items are especially problematic because they turn answer quality into a formatting contest. The "gold" includes material that a reasonable grounded system should not be expected to reproduce.

### Overly Vague v4 Rewrites

The v4 sample improves cleanliness substantially, but some rewrites over-compress the answer and lose specificity:

- `en_07`: the v4 rewrite drops useful locality and jurisdiction detail.
- `en_09`: the v4 rewrite drops the entity's constitutional and numerical context.
- `en_10`: the v4 rewrite drops the source's comparative-size detail.
- `en_03`: the v4 rewrite removes coordinate residue but also loses useful location detail.

These are usable, but weaker than they should be for a retrieval benchmark that depends on interpretable gold answers.

### v1 to v4 Changes

The v4 sample clearly rewrites many v1 answers into short declarative summaries. This generally improves quality:

- `en_01`, `en_05`, `en_12`, and `en_19` are much cleaner in v4 than in v1
- `uz_03` improves materially from a fragment containing only an area measurement to a complete statement of the entity's status.

But the rewriting is not uniformly beneficial:

- some v4 English answers become less specific than the v1 source-text version
- the rewrite process appears optimized for brevity, not always for factual completeness

Net assessment: v4 gold-answer rewriting is an improvement overall, but it is not quality-controlled enough to treat every rewrite as automatically superior.

## Question Quality

### Domain Misclassification

These items have domain labels or domain templates that do not fit the entity type:

- `en_20`: `"What place, state, or political entity is Quantum field theory?"`
- `en_61`: `"What place, state, or political entity is List of battleships of the United States Navy?"`
- `en_62`: `"What institution, organization, or formal body is Ron Rivera?"`
- `uz_71`: `"Munavvarqori Abdurashidxon oʻgʻli qanday muassasa yoki tashkilot?"`
- `uz_78`: `"Coldplay qanday muassasa yoki tashkilot?"`
- `uz_82`: `"1477 qanday muassasa yoki tashkilot?"`
- `uz_83`: `"1917 qanday muassasa yoki tashkilot?"`
- `uz_89`: `"Gmail qanday muassasa yoki tashkilot?"`

These are not borderline cases. They are category errors.

### Semantically Broken Questions

The following questions are grammatically well-formed but semantically nonsensical because the template does not match the entity:

- `en_20`
- `en_61`
- `en_62`
- `uz_71`
- `uz_78`
- `uz_82`
- `uz_83`
- `uz_89`

The clearest broken examples are:

- `en_20`: `"What place, state, or political entity is Quantum field theory?"`
- `uz_82`: `"1477 qanday muassasa yoki tashkilot?"`
- `uz_83`: `"1917 qanday muassasa yoki tashkilot?"`

### Overly Generic Questions

At least one item is too generic to function as a strong retrieval probe:

- `uz_93`: `"Institut qanday muassasa yoki tashkilot?"`

This is a generic noun definition framed as an institution lookup. It has very low discriminative value and encourages dense-retrieval hub behavior.

### Template Propagation

`build_manual_eval_v4.py` expands v2 into v4 by:

1. grouping seed items by `(language, domain)`
2. sorting each group by `id`
3. inferring a subject from the title, doc ID, or stripped question
4. generating one alternate question from a fixed domain template bank
5. assigning a deterministic variant ID of the form `{lang}_{domain}_v4_{nn}`

This means seed-item mistakes propagate deterministically into v4.

Examples:

- `en_61` -> `en_governance_v4_19`
- `uz_71` -> `uz_institutions_v4_07`
- `uz_78` -> `uz_institutions_v4_08`
- `uz_82` -> `uz_institutions_v4_11`
- `uz_83` -> `uz_institutions_v4_12`
- `uz_89` -> `uz_institutions_v4_16`
- `uz_93` -> `uz_institutions_v4_18`

So v4 is not only larger; it also duplicates some seed-quality problems in a more polished-looking form.

## Schema Consistency

The benchmark schema is asymmetric across languages:

- English `source_doc_ids` are human-readable titles such as `Art Deco` and `Château de Brest`
- Uzbek `source_doc_ids` are opaque numeric identifiers such as `793` and `1046`

This matters for auditability:

- a reviewer can understand an English source ID immediately
- a reviewer cannot interpret Uzbek IDs like `8090` or `13959` without corpus access
- failure analysis becomes dependent on Isambard-only lookups

This is a real documentation problem, not a cosmetic one. It makes the Uzbek half less transparent and harder to externally validate.

Recommendation: v5 should resolve Uzbek numeric `source_doc_ids` to readable `source_title` values for every item, and future reports should show both fields together.

## Sample Representativeness

The public sample contains `25` items, and it is not balanced.

### Language Distribution

- English: `16`
- Uzbek: `9`

### Domain Distribution Per Language

| language | governance | history | institutions | culture |
|----------|------------|---------|--------------|---------|
| en | 4 | 4 | 4 | 4 |
| uz | 4 | 3 | 0 | 2 |

Missing or underfilled cells:

- Uzbek institutions: `0` items
- Uzbek history: `3` items instead of `4`
- Uzbek culture: `2` items instead of `4`

This sample is therefore not representative of the benchmark's claimed balanced structure.

## Metric Validity

`src/generation.py` uses a stub generator:

- it returns only the first sentence of the top retrieved passage under `prompt_style == "grounded"`
- it does not synthesize or normalize an answer

`src/evaluation.py` then scores that stub output using token overlap:

- `answer_overlap = overlap_ratio(answer, gold)`
- `context_overlap = overlap_ratio(answer, context_text)`
- `grounded_answer_score = max(answer_overlap, context_overlap)`

This creates a methodological collision visible in the "Grounded Answers That Remain Incorrect" section of `manual_eval_v2_error_analysis_20260308.md`.

Observed pattern:

- retrieval recall is `1.0`
- the correct source document was retrieved
- but the generated answer is marked problematic because the stub only returns the first sentence and the scoring is overlap-based

The root causes are straightforward:

1. the generator truncates to the first sentence
2. the scorer compares that truncated sentence to the full gold answer
3. long or noisy gold answers reduce overlap even when retrieval succeeds
4. navigation-heavy passages make the first sentence especially brittle

Examples from the report:

- `en_01` and `en_05`: the retrieved source is correct, but the answer starts from navigation-heavy gold text
- `en_21`: the gold answer is longer than the first-sentence stub output
- `en_00`, `en_11`, and `en_18`: the report still lists them despite near-identical wording, showing that this section is not a clean retrieval-error inventory

Conclusion: the current benchmark does not cleanly separate retrieval quality from answer-quality artifacts when using the stub generator. Retrieval-only analysis should rely on `recall@k` and corpus-presence checks, not overlap-based answer judgments.

This distinction should be stated explicitly in both methodology and limitations documentation.

## Summary Table

| issue_type | severity | item_count | example_ids | recommended_action |
|------------|----------|------------|-------------|-------------------|
| Domain misclassification | critical | 8 | `en_20`, `en_61`, `en_62`, `uz_71`, `uz_78`, `uz_82`, `uz_83`, `uz_89` | Remove, relabel, or rewrite these items before a cleaned release. |
| Wikipedia navigation artifacts in v1 gold answers | moderate | 5 | `en_01`, `en_03`, `en_05`, `en_12`, `en_19` | Keep the v4 rewrites, but add manual QA to verify factual completeness after cleanup. |
| Raw passage dumps in v1 | moderate | 4 | `en_01`, `en_05`, `en_12`, `en_19` | Replace page dumps with concise, entity-specific answers. |
| Over-compressed v4 gold answers | minor | 4 | `en_03`, `en_07`, `en_09`, `en_10` | Revise for specificity rather than maximal brevity. |
| Overly generic question formulation | moderate | 1 | `uz_93` | Rewrite as a specific definitional item or remove it from retrieval evaluation. |
| Template-propagated broken variants | critical | 16 | `en_20`, `en_governance_v4_03`, `en_62`, `en_institutions_v4_07`, `uz_71`, `uz_institutions_v4_07` | Propagate quality flags and exclude these from any "clean" subset. |
| Schema asymmetry for Uzbek doc IDs | moderate | 200 | `uz_00`, `uz_71`, `uz_82` | Add `source_title` in v5 and show both ID and title in reports. |
| Public sample not representative | moderate | 3 | missing cells: `uz/institutions`, underfilled `uz/history`, `uz/culture` | Rebuild the public sample with enforced language-domain balance. |
| Retrieval/generation metric conflation | critical | 12 | `en_00`, `en_01`, `en_05`, `en_21` | Separate retrieval evaluation from answer evaluation in methodology, reporting, and score interpretation. |
