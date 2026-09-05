# Workshop Paper Outline

## 1. Introduction
- Motivation: multilingual AI systems often underperform on culturally grounded questions because relevant local knowledge is missing or weakly represented.
- Problem statement: standard RAG evaluations often confound model quality with corpus coverage.
- Research question: in bilingual English-Uzbek RAG evaluation, does retrieval quality depend more on model choice or knowledge source coverage?
- Main claim: in this evaluation setting, Uzbek corpus supplementation produced a larger retrieval gain than the compared model and retrieval interventions.

## 2. Related Work
- Multilingual QA and retrieval benchmarks
- Retrieval-augmented generation for knowledge grounding
- Work on hallucination reduction through retrieval
- Gaps in culturally grounded and Global South-oriented evaluation
- Corpora and representation asymmetries across languages

## 3. Benchmark and Dataset Design
- Languages: English and Uzbek
- Domains: governance, history, institutions, culture
- Manual benchmark construction
- `manual_eval_v2`: 200 items, balanced by language and domain
- `manual_eval_v4`: 400 items, balanced by language and domain, preserving original items plus alternate phrasings
- Example schema and source-document linkage

## 4. Methodology
- Reproducible pipeline on Isambard
- Data preparation and corpus normalization
- Retrieval settings:
- no retrieval
- vector retrieval
- BM25 lexical retrieval
- hybrid retrieval
- Prompt settings: baseline vs grounded
- Metrics:
- retrieval recall@k
- grounded answer score
- hallucination proxies

## 5. Experiments
- Baseline no-retrieval vs vector retrieval
- Chunking comparison
- Embedding comparison
- Corpus gap analysis
- Supplement v1: targeted manual Uzbek supplement
- Supplement v2: structured Uzbek supplement from Uzbek Wikipedia
- Hybrid retrieval comparison
- Scaling from `manual_eval_v2` to `manual_eval_v4`

## 6. Findings
- Retrieval improves grounding relative to no retrieval
- Chunking has limited effect on hard Uzbek cases
- Embedding changes produce modest gains
- Hybrid retrieval does not outperform vector retrieval in the final setup
- Corpus supplementation produces the largest improvements
- Uzbek weak domains improve sharply once missing documents are added

## 7. Discussion
- Why corpus coverage produced the largest observed gain in this setting
- Knowledge representation as a corpus design problem
- Limits of model-only optimization when local knowledge is absent
- Implications for multilingual AI evaluation in underrepresented settings

## 8. Limitations
- Heuristic scoring and stub generation path
- Manual benchmark scope remains moderate
- English source coverage remains thinner in some domains
- Supplement design currently tied to available Wikipedia-like sources
- Public release is a pilot with known template and domain-quality issues
- No human evaluation or LLM-as-judge evaluation completed

## 9. Future Work
- Expand culturally grounded corpora with institutional, legal, and historical sources
- Add stronger generation backends and judge-based evaluation
- Extend to more languages and cross-language equivalence testing
- Study source quality versus source quantity tradeoffs

## 10. Conclusion
- Restate the main empirical takeaway:
- corpus coverage and model choice should be tested as distinct retrieval interventions
- broader claims require replication across languages, corpora, and end-to-end generation settings
