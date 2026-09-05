# Culturally Grounded Multilingual RAG Evaluation: Project Synthesis V2

---
## ⚠️ PARTIAL RETRACTION: English Supplement Results Invalid (March 2026)

**Status:** The English supplement (v1) evaluation results have been retracted.

**Issue:** Synthetic documents contained gold_answer text (data leakage). Results claiming 100% English recall are invalid.

**Valid Results:** Uzbek supplementation (39% to 98%) and all baseline comparisons remain valid.

**Note:** English supplementation is NOT reported in this document. English performance is reported at baseline only.

---

## Executive Summary

This project reports evidence from a 400-row pilot bilingual retrieval benchmark in English and Uzbek across governance, history, institutions, and culture. In the validated v2 comparison, targeted Uzbek corpus supplementation increased retrieval recall from 39% to 98% (59 percentage points; *p* < 0.001; Cohen's *d* = 2.91). The observed overall difference between the compared embedding models was 7.5 percentage points (Cohen's *d* = 0.31). These findings concern retrieval in this evaluation setting, not generated-answer quality or all low-resource languages.

## Key Contributions

1. **Pilot bilingual retrieval benchmark**: 400-item evaluation set (`manual_eval_v5`) with difficulty, quality flags, and source titles

2. **Empirical demonstration**: Uzbek recall improved from 39% to 98% through corpus supplementation (p < 0.001, d = 2.91)

3. **English gap analysis**: Identified 74 missing English documents (37% gap), with weakest coverage in history (40%) and institutions (32%)

4. **Statistical analysis**: Key reported comparisons include bootstrap confidence intervals, effect sizes, and significance tests

5. **Research implication**: Corpus coverage merits explicit testing alongside retrieval-model choices

6. **Public research outputs**: Policy brief, workshop paper draft, reports, code, and retrieval-only dataset

## Experimental Summary

### Benchmark Evolution

| Version | Size | Key Features | Purpose |
|---------|------|--------------|---------|
| v1 | 200 items | Initial balanced set | Baseline experiments |
| v2 | 200 items | Quality audit, failure taxonomy | Error analysis |
| v4 | 400 items | Expanded evaluation set | Robustness analysis |
| v5 | 400 items | Enriched schema (difficulty, quality_flag, source_title) | Public pilot release |

### Overall Recall@k Across All Conditions

| Condition | Corpus | Retrieval | Overall | EN | UZ |
|-----------|---------|-----------|--------|-----|-----|
| No retrieval | baseline | none | 0.0% | 0.0% | 0.0% |
| Vector baseline | baseline | simple_vector | 49.0% | 61.0% | 37.0% |
| + e5-large | baseline | multilingual_e5_large | 51.0% | 63.0% | 39.0% |
| + mpnet | baseline | mpnet | 43.5% | 62.0% | 25.0% |
| + UZ supp v1 | baseline_plus_manual_uzbek | multilingual_e5_large | 71.5% | 63.0% | 80.0% |
| + UZ supp v2 | baseline_plus_structured_uzbek | multilingual_e5_large | 80.5% | 63.0% | 98.0% |
| BM25 | supplement_v2 | bm25 | 67.0% | 62.0% | 72.0% |
| Hybrid | supplement_v2 | bm25_plus_multilingual_e5_large | 79.5% | 63.0% | 96.0% |

### Statistical Significance

| Comparison | Metric | Difference | 95% CI | p-value | Cohen's d |
|------------|--------|------------|--------|---------|-----------|
| Baseline vs UZ supp v2 | UZ recall | +59.0% | [52.1%, 65.9%] | <0.001*** | 2.91 |
| Baseline vs UZ supp v2 | Overall recall | +29.5% | [23.8%, 35.2%] | <0.001*** | 1.45 |
| mpnet vs e5-large | Overall recall | +7.5% | [1.2%, 13.8%] | 0.020* | 0.31 |
| BM25 vs Vector | UZ recall | +24.0% | [18.1%, 29.9%] | <0.001*** | 0.98 |
| Vector vs Hybrid | Overall recall | 0.0% | [-2.1%, 2.1%] | 1.000 | 0.00 |

*** p < 0.001, ** p < 0.01, * p < 0.05*

## Per-Language Analysis

### English Performance (Baseline only)

- Overall: 63.0%
- Governance: 80.0%
- History: 40.0%
- Institutions: 32.0%
- Culture: 100.0%

**Key insight:** English shows asymmetric performance. Culture is fully covered, governance is well-covered, but history and institutions are weak due to missing sources. A 37% gap (74 documents) was identified but English supplementation results are not reported (the initial attempt was retracted due to data leakage).

### Uzbek Performance

**Baseline (before supplementation):**
- Overall: 39.0%
- Governance: 100.0%
- History: 16.0%
- Institutions: 12.0%
- Culture: 28.0%

**After Uzbek supplementation v2 (validated v2 comparison):**
- Overall: 98.0%
- Governance: 100.0%
- History: 96.0%
- Institutions: 96.0%
- Culture: 100.0%

**Interpretation:** Uzbek supplementation produced gains across history, institutions, and culture in this evaluation setting. The absolute improvement was 59 percentage points (Cohen's *d* = 2.91).

## Per-Domain Analysis

### Baseline Coverage by Domain

| Domain | English | Uzbek | English-Uzbek Gap |
|--------|---------|-------|-------------------|
| Governance | 80% | 100% | -20% |
| History | 40% | 16% | +24% |
| Institutions | 32% | 12% | +20% |
| Culture | 100% | 28% | +72% |

### Expanded v4 Evaluation under the Supplemented Setup

| Domain | English | Uzbek | English-Uzbek Gap |
|--------|---------|-------|-------------------|
| Governance | 80% | 98% | -18% |
| History | 40% | 96% | +56% |
| Institutions | 32% | 96% | +64% |
| Culture | 100% | 94% | +6% |

**Interpretation:** The v4 evaluation used 400 items and should not be compared directly with the 200-item v2 phase. Its 96% Uzbek result is distinct from the validated v2 supplementation comparison, which reached 98%. English history and institutions remained weaker than the other English domains.

## Failure Taxonomy

### Original Classification (Phase 1-2)

1. **Retriever Collapse** (10 items): When sources missing, retrieval falls back on generic hub documents
2. **Corpus Gaps** (5 items): Source documents absent from corpus (dominant failure mode)
3. **Quality Issues** (1 item): Source present but chunking/embedding fails

### Updated Classification

1. **Corpus Gaps - Uzbek** (61 items): Uzbek history/institutions documents missing from corpus
   - Resolved: Uzbek supplement v2 added 61 structured documents
   - Actual impact: 59% absolute improvement (39% to 98%)

2. **Corpus Gaps - English** (74 items): English history/institutions documents missing from corpus
   - NOT resolved: English supplementation attempted but results retracted due to data leakage in synthetic documents
   - Gap remains: 37% of English documents missing

3. **Retriever Collapse** (10 items): Collapsed onto hub documents (doc IDs 1790, 1570, 1798)
   - Resolved through supplementation for Uzbek

4. **Question-quality flags** (4 public rows): Known question-quality issues retained in the pilot release
   - Documented through the `quality_flag` field

5. **Domain misclassification flags** (16 public rows): Seed-item and generated-variant domain mismatches
   - Documented through the `quality_flag` field; the audit is not exhaustive

## Methodological Limitations

### Current Limitations

1. **Stub generation**: Generation module returns first retrieved sentence, not actual LLM output
   - Impact: Token overlap metrics primarily reflect retrieval success
   - Mitigation: LLM-as-judge evaluation infrastructure available for future work

2. **Benchmark size**: 400 items provides initial insights but limited statistical power
   - Impact: Wide confidence intervals for sub-group analyses
   - Mitigation: Bootstrap CIs reported; larger benchmarks planned for future work

3. **English not supplemented**: The 37% English gap was identified but not successfully addressed
   - Impact: English performance reported at baseline only
   - Note: Initial supplementation attempt was retracted due to data leakage

4. **Only 2 languages**: English and Uzbek represent different resource levels but limited generalisability
   - Impact: Findings may not extend to African, South Asian, or Indigenous languages
   - Mitigation: Explicitly stated as limitation; expansion to third language planned

### Evaluation Metrics

**Primary metric:** Recall@k (retrieval success)
- Robust to stub generation limitations
- Directly measures corpus coverage
- Statistically validated with bootstrap CIs

**Secondary metric:** Token overlap (Jaccard similarity)
- Measures answer grounding but conflates retrieval and generation
- Should be interpreted cautiously due to stub generation

## Remaining Gaps

### Unresolved Issues

1. **English supplementation not completed**: 74 English documents (37% gap) remain missing
   - Initial attempt retracted due to data leakage in synthetic documents
   - Future work required with real MIRACL sources

2. **LLM-as-judge not completed**: Infrastructure available but evaluation not executed
   - Impact: No structured assessment of answer quality beyond token overlap

3. **Cross-lingual evaluation**: Not attempted
   - Impact: Findings limited to monolingual retrieval scenarios

### Open Questions

1. **Cross-language generalisation**: Will findings replicate in Arabic, Swahili, Hindi, or Indigenous languages?
2. **Long-term maintenance**: How to keep supplemented corpora current as knowledge evolves?
3. **Human evaluation**: Do LLM-as-judge scores correlate with human assessments of answer quality?
4. **Cost-benefit analysis**: Is corpus supplementation more cost-effective than model scaling at scale?

## Research and Policy Considerations

### For Research Programmes

1. **Test knowledge curation**: Include corpus-coverage interventions in multilingual retrieval research designs

2. **Community-led documentation**: Support local communities to document their own knowledge in machine-readable formats

3. **Evaluation standards**: Consider cultural-coverage audits as one component of multilingual retrieval evaluation

### For AI Developers

1. **Audit before optimise**: Check corpus coverage before investing in larger models or better embeddings

2. **Domain-specific corpora**: Evaluate whether curated sources address documented retrieval gaps before changing models

3. **Cultural specificity**: Generic benchmarks hide performance gaps for culturally grounded queries

### For Policymakers

1. **Digital sovereignty**: Local knowledge curation is essential for AI systems to serve communities effectively

2. **Language preservation**: AI deployment can incentivise documentation and preservation of underrepresented languages

3. **Evaluation standards**: Current AI regulations do not address cultural knowledge gaps

## Conclusion

This project provides evidence that corpus coverage was an important retrieval constraint in this English-Uzbek evaluation setting. Targeted Uzbek corpus supplementation produced a 59-percentage-point gain (Cohen's *d* = 2.91), while the compared embedding models differed by 7.5 percentage points overall (Cohen's *d* = 0.31).

The 59-percentage-point gain from corpus supplementation was approximately 7.9 times the 7.5-point gain observed from embedding-model variation. This is a ratio of absolute recall gains, not a ratio of Cohen's *d* values.

The findings have immediate implications:

- **For researchers**: Corpus-centric approaches should precede model-centric approaches for culturally grounded AI
- **For research programmes**: Corpus curation and model comparison can be evaluated as separate interventions
- **For policymakers**: Cultural-coverage audits may be considered when evaluating multilingual retrieval systems
- **For communities**: Local knowledge documentation is essential for AI systems to serve effectively

The benchmark, code, and findings are publicly available for reproducibility and community engagement.

---

**Project Status**: Core experiments complete, Uzbek supplementation validated, English supplementation incomplete
**Code Available**: https://github.com/rajantripathi/soas-rag-evaluation
**Affiliations**: AI² Lab, American University of Technology, Uzbekistan; Centre for AI Futures, SOAS University of London

This report is an author-maintained research artifact and does not represent an official institutional position of SOAS University of London or the American University of Technology.

**Last Updated**: 20 March 2026
