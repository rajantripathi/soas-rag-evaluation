# Workshop Paper Outline: Corpus Coverage Dominates Model Choice in Culturally Grounded Multilingual Retrieval

## Target Venue
LREC/MRL, ACL Findings, or EMNLP workshops on multilingual NLP or evaluation

## 1. Title

Corpus Coverage Dominates Model Choice in Culturally Grounded Multilingual Retrieval

## 2. Abstract (150 words)

**Problem:** Culturally grounded AI evaluation is challenging because standard benchmarks do not test whether systems can answer questions requiring local institutional, historical, or cultural knowledge.

**Finding:** Corpus coverage matters more than model quality for retrieval-augmented QA in culturally specific domains. Through targeted corpus supplementation, we demonstrate dramatic performance improvements that model optimisation cannot match.

**Evidence:** In a bilingual benchmark (English, Uzbek), Uzbek recall improved from 39% to 98% through corpus supplementation, while model changes produced minimal gains. English showed similar patterns, with history and institutions domains weak due to missing sources.

**Implication:** AI developers and funders should prioritise knowledge curation over model scaling for culturally grounded applications. Small, well-curated domain-specific corpora outperform generic web-scale data for local knowledge tasks.

## 3. Introduction

- **Culturally specific knowledge challenges:** Standard AI benchmarks fail to test whether systems understand local contexts. Communities deploy AI systems that cannot answer basic questions about local history, institutions, or culture.

- **Research question:** What drives retrieval performance for culturally grounded QA - model quality or knowledge source coverage?

- **Contributions:** (1) Bilingual benchmark (English, Uzbek) testing cultural knowledge across governance, history, institutions, culture; (2) Empirical demonstration that corpus supplementation outperforms model optimisation; (3) Analysis of failure modes showing retriever collapse when sources missing; (4) Policy implications for AI funding and evaluation standards.

## 4. Related Work

- **Multilingual benchmarks:** XTREME (Hu et al., 2020) - cross-lingual transfer but not cultural knowledge; MIRACL (Zhang et al., 2023) - multilingual retrieval but generic topics; TyDi QA (Clark et al., 2021) - typologically diverse languages but culturally neutral questions.

- **RAG evaluation methods:** Kandpal et al. (2023) - retrieval augmentation for QA; Lewis et al. (2020) - RAG for knowledge-intensive tasks; but limited evaluation of cultural grounding.

- **Cultural AI and knowledge representation:** Bird (2022) - language diversity in NLP; Joshi et al. (2020) - social biases in multilingual models; but limited work on corpus coverage gaps for underrepresented languages.

- **Specific papers to cite:** 5-8 key papers on multilingual benchmarks, RAG evaluation, cultural AI, and knowledge representation gaps.

## 5. Benchmark Design

- **Languages:** English and Uzbek - chosen as a high-resource language paired with a typologically distinct low-resource language from Central Asia, representing different script families (Latin vs Cyrillic) and cultural contexts.

- **Domains:** Four domains selected for cultural specificity: governance (political systems, policies), history (historical events, figures, periods), institutions (organisations, formal bodies), culture (cultural practices, traditions).

- **Dataset versions:** Evolution from v1 (200 items) through v2 (quality audit), v4 (Uzbek supplementation), to v5 (400 items with enriched schema including difficulty, quality flags, source titles). Each version addressed specific limitations identified through analysis.

- **Quality audit methodology:** Manual review of all 400 items by domain experts, classification of failure modes (retriever collapse, corpus gaps, quality issues), and iterative refinement based on error analysis.

## 6. Experimental Setup

- **Retrieval conditions tested:**
  - Baseline: no retrieval (ablation)
  - Vector retrieval: TF-IDF, sentence embeddings (mpnet, multilingual-e5-large)
  - Lexical retrieval: BM25 with configurable parameters
  - Hybrid retrieval: BM25 + vector combination with reranking
  - Corpus supplementation: targeted Uzbek supplement (v1 structured, v2 structured), English supplement (synthetic v1)

- **Metrics:**
  - Primary: Recall@k (whether gold source document appears in top-k retrieved passages)
  - Secondary: Token overlap (Jaccard similarity) between system answer and gold answer
  - Statistical: Bootstrap confidence intervals (95%, 1000 resamples), McNemar's test for paired comparisons, Cohen's d for effect sizes

- **Infrastructure:** GH200 GPUs on Isambard cluster (UK national HPC service), embedding models loaded from Hugging Face (intfloat/multilingual-e5-large), indexes built with sentence-transformers, evaluation pipeline orchestrated with custom Python framework.

## 7. Results (define exact tables/figures)

- **Table 1: Overall Recall@k Across All Conditions**
  - Rows: Baseline (no retrieval), Vector (TF-IDF), Vector (mpnet), Vector (e5-large), + Uzbek supp v1, + Uzbek supp v2, + Full supplement (UZ + EN)
  - Columns: Overall recall@k, English recall@k, Uzbek recall@k
  - Key finding: Uzbek supp v2 shows largest jump (39% to 98%), full supplement shows additional improvement

- **Table 2: Per-Language Recall@k**
  - Rows: Same as Table 1
  - Columns: English recall@k, Uzbek recall@k
  - Key finding: English improvements in history/institutions after supplementation

- **Table 3: Per-Domain Recall@k**
  - Rows: Same conditions
  - Columns: Governance, History, Institutions, Culture
  - Key finding: History and institutions show weakest performance before supplementation, strongest improvement after

- **Figure 1: Supplementation Impact (Bar Chart)**
  - X-axis: Retrieval conditions
  - Y-axis: Recall@k
  - Bars: Overall (blue), English (green), Uzbek (red)
  - Annotation: Vertical line where supplementation begins, showing dramatic improvement

- **Statistical Significance Table:**
  - Columns: Condition A, Condition B, Metric, Difference, 95% CI, p-value
  - Rows: Baseline vs UZ supp v2, UZ supp v2 vs Full supplement, others as relevant
  - Key finding: All supplementation effects statistically significant (p < 0.001)

## 8. Analysis

- **Failure taxonomy:** Classified all retrieval failures into three categories: (1) Retriever collapse - when source documents missing, system falls back on generic hub passages; (2) Corpus gaps - source documents absent from corpus (dominant failure mode); (3) Quality issues - source present but chunking or embedding fails.

- **Retriever collapse pattern:** In Uzbek history and institutions before supplementation, all failures collapsed onto same 3 hub documents (doc IDs 1790, 1570, 1798). This is not independent failure but dense-retrieval collapse in absence of relevant sources.

- **English vs Uzbek asymmetry:** English had higher baseline performance (63% vs 39%) due to better generic coverage in MIRACL/TyDi QA, but showed same weakness pattern (history 40%, institutions 32%). English items have readable Wikipedia titles as doc IDs vs opaque numeric IDs for Uzbek, making gap analysis easier.

- **Stub generation artifacts:** Current generation module returns first retrieved sentence, which affects answer quality scoring. However, recall@k metric (primary) is unaffected by this limitation. Token overlap scores should be interpreted cautiously.

## 9. Discussion

- **Implications for multilingual AI deployment:** Model-centric approaches (larger models, better embeddings) produce marginal gains for culturally grounded tasks. Corpus-centric approaches (targeted knowledge curation) produce transformational improvements. Developers should audit corpus coverage before scaling models.

- **Corpus-first design principle:** For culturally grounded applications, start with corpus curation not model selection. A small, well-curated domain-specific corpus (100-200 documents) can outperform generic web-scale corpora. This is cost-effective and reproducible.

- **Limitations:**
  - Benchmark size: 400 items is sufficient for initial analysis but larger benchmarks needed for definitive conclusions
  - Stub generation: No actual LLM integration, answer quality not fully evaluated
  - Cultural specificity: Findings may not generalise beyond English/Uzbek or these four domains
  - Synthetic supplements: English supplements are synthetic (Q+A pairs) rather than extracted from raw sources

## 10. Limitations

- **Benchmark size:** 400 items (200 per language) provides initial insights but statistical power limited for fine-grained sub-group analysis. Future work should expand to 1000+ items.

- **Stub generation:** Current generation module returns first retrieved sentence, not actual LLM generation. Answer quality metrics (token overlap) reflect retrieval success more than generation capability. LLM-as-judge evaluation (in progress) will provide better quality assessment.

- **Only 2 languages:** English and Uzbek represent different resource levels and script families but do not capture full diversity of world's languages. Findings may not extend to African, South Asian, or Indigenous languages.

- **Findings may not generalise:** Cultural specificity of domains (history, institutions) may not apply to other domains (science, technology). Different communities may have different knowledge organisation patterns.

## 11. Conclusion

- **Summary:** Corpus coverage is the dominant bottleneck for culturally grounded multilingual retrieval. Uzbek recall improved from 39% to 98% through supplementation (59 point improvement). English showed similar patterns with history/institutions weak before supplementation. Model optimisation produced minimal gains by comparison.

- **Call to action:** Fund knowledge curation not just model scaling. Support community-led documentation projects. Require cultural coverage audits in AI evaluation standards. Develop open benchmarks that test local knowledge, not just translation accuracy.

- **Future work:** Expand to third language (Arabic, Swahili, or Hindi) to test generalisability; integrate actual LLM generation and LLM-as-judge evaluation; human evaluation of answer quality; broader range of domains; longitudinal study of corpus maintenance.

---

**Estimated length:** 4 pages plus references
**Key contribution:** Empirical demonstration that corpus coverage matters more than model quality for culturally grounded AI
**Policy relevance:** Findings directly inform funding priorities (AHRC, ESRC, British Academy) and evaluation standards
**Code and data availability:** https://github.com/rajantripathi/soas-rag-evaluation
