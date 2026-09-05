# Corpus Coverage in an English-Uzbek Retrieval Pilot

## Key Message

In this 400-row pilot bilingual retrieval benchmark, targeted Uzbek corpus supplementation produced a substantially larger observed recall gain than embedding-model variation. The result is evidence from this English-Uzbek evaluation setting, not a claim about all languages or end-to-end answer quality.

## The Evaluation Setting

The benchmark tests retrieval in English and Uzbek across governance, history, institutions, and culture. It measures whether a relevant source document is retrieved. The public release is retrieval-only, contains documented template-generated and domain-misaligned examples, and should not be treated as a uniformly clean or definitive QA benchmark.

No human evaluation or LLM-as-judge evaluation has been completed. The validated findings therefore concern retrieval recall, not the quality, faithfulness, or usefulness of generated answers.

## Validated Findings

The English baseline retrieval recall was 63%. The Uzbek baseline was 39%. After targeted Uzbek corpus supplementation, Uzbek recall reached 98%, an absolute gain of 59 percentage points (*p* < 0.001; Cohen's *d* = 2.91).

Across the compared embedding models, the overall recall difference was 7.5 percentage points (Cohen's *d* = 0.31). The 59-percentage-point gain from corpus supplementation was approximately 7.9 times the 7.5-point gain observed from embedding-model variation. This is a comparison of absolute recall gains, not a ratio of Cohen's *d* values, and it does not compare different generation LLMs.

English history and institutions had baseline recall of 40% and 32%, respectively. An English supplementation experiment was attempted, but its results were retracted because synthetic material leaked answer content into the corpus. English supplementation is therefore not evidence in this brief.

## Research and Policy Relevance

The evaluation suggests that corpus coverage should be audited explicitly when multilingual retrieval systems underperform on locally specific knowledge. In comparable settings, source curation may merit testing before more expensive changes to retrieval models. The present experiment does not establish comparative cost-effectiveness, and it does not show that a small curated corpus generally outperforms web-scale training data.

Possible next steps include:

- supporting transparent, community-informed source curation for underrepresented languages and domains;
- including corpus-coverage checks in multilingual retrieval evaluations;
- developing larger, independently reviewed benchmarks with clearer item-level provenance and quality controls; and
- validating retrieval findings with human assessment and end-to-end generation evaluation before making deployment claims.

## Scope and Limitations

- The benchmark contains 400 pilot items in two languages.
- Known template and domain-quality issues are documented, and current quality flags are not exhaustive.
- The result is limited to monolingual retrieval in the evaluated English-Uzbek setting.
- Cross-lingual retrieval, human evaluation, and LLM-as-judge evaluation were not completed.
- The public dataset excludes reference answers, source text, contexts, and generated answers pending source and licence clearance.

## About

Author affiliations: AI² Lab, American University of Technology, Uzbekistan; Centre for AI Futures, SOAS University of London.

This brief and its associated repository are research artifacts maintained by the author. They do not represent an official institutional position of SOAS University of London or the American University of Technology.

---

**Published:** March 2026

**Project:** SOAS English-Uzbek RAG Evaluation (Retrieval-Only)

**Dataset DOI:** https://doi.org/10.5281/zenodo.21067667
