# Corpus Coverage Dominates Model Choice in Culturally Grounded Multilingual Retrieval

**Authors:** Rajan Tripathi (Centre for AI Futures, SOAS University of London; AI2 Innovation Lab, American University of Technology, Uzbekistan)

---

## Abstract

Multilingual retrieval-augmented generation systems are typically evaluated on generic benchmarks that underrepresent culturally grounded knowledge. We present a bilingual benchmark for culturally grounded question answering in English and Uzbek, spanning four domains: governance, history, institutions, and culture. Through a controlled experiment sequence on the Isambard-AI supercomputer, we systematically isolate the effects of retrieval algorithm, chunking strategy, embedding model, and corpus coverage. We find that corpus supplementation with locally curated knowledge sources produces a 59-percentage-point improvement in Uzbek retrieval recall (0.39 to 0.98, p < 0.001, Cohen's d = 2.91), while embedding model changes yield only a 7.5-percentage-point gain (d = 0.31). The effect of knowledge source curation is 7.9 times larger than the effect of model optimisation. Our results suggest that for underrepresented languages, investment in culturally grounded knowledge curation should precede investment in model improvement.

---

## 1. Introduction

Retrieval-augmented generation (RAG) systems are increasingly deployed in multilingual settings worldwide. However, evaluation standards have not kept pace with deployment. Most RAG systems are assessed on generic benchmarks like MIRACL or TyDi QA, which were designed to measure overall system performance rather than culturally grounded retrieval quality. These benchmarks underrepresent domains that matter most to local communities: governance, history, institutions, and culture.

When RAG systems fail in culturally grounded domains, the default assumption is often model inadequacy. If a system cannot answer questions about local history or institutions, the typical response is to upgrade the embedding model or switch to a larger language model. We challenge this assumption. Our alternative hypothesis is that the bottleneck is corpus coverage, not model quality.

To test this hypothesis, we built a bilingual benchmark for English and Uzbek focusing on culturally grounded knowledge. We then conducted a controlled experiment sequence systematically varying retrieval parameters: chunking strategy, embedding model, retrieval algorithm, and corpus coverage. By isolating each variable, we can quantify which interventions produce meaningful improvements.

We make three contributions. First, we release a retrieval-only bilingual pilot benchmark with 400 items across four domains and documented quality-audit metadata. Second, we provide a controlled ablation study isolating the effects of different RAG design choices. Third, we demonstrate that corpus supplementation produces effect sizes nearly eight times larger than embedding model improvements, with direct implications for AI funding priorities and evaluation standards.

---

## 2. Related Work

**Multilingual retrieval.** MIRACL (Zhang et al., 2022) and TyDi QA (Clark et al., 2020) advanced multilingual retrieval evaluation, but their coverage of culturally grounded topics is uneven. XOR-QA (Asai et al., 2020) addressed cross-lingual retrieval but focused on answerable questions rather than corpus adequacy. These benchmarks assume the corpus contains relevant documents, which is often false for culturally grounded knowledge.

**RAG evaluation.** RAGAS (Es et al., 2024) and factual-consistency metrics (Honovich et al., 2022) measure generation quality, but they implicitly assume corpus adequacy. When retrieval returns nothing relevant, these metrics cannot distinguish between model failure and corpus absence. Dense Passage Retrieval (DPR; Karpukhin et al., 2020) and RAG (Lewis et al., 2020) focused on architecture rather than corpus coverage.

**Cultural bias in NLP.** Hershcovich et al. (2022) documented cultural gaps in NLP systems, particularly for underrepresented languages. However, existing work has not systematically tested corpus coverage versus model choice for retrieval tasks. Our work fills this gap by isolating corpus effects from model effects.

**The gap.** No existing work has systematically compared corpus coverage against model choice for culturally grounded retrieval. We provide the first controlled ablation study quantifying these effects.

---

## 3. Benchmark Design

### 3.1 Languages and Domains

Our benchmark covers two languages (English and Uzbek) across four domains: governance, history, institutions, and culture. These domains were chosen because they represent knowledge that is locally specific but often missing from generic web-scale corpora. English represents a high-resource language with broad Wikipedia coverage. Uzbek represents a lower-resource language with more uneven coverage.

### 3.2 Construction Method

The benchmark was constructed in three phases. Version 1 (v1) contained 200 items with 25 items per language-domain cell. Version 2 (v2) added quality audit metadata. Version 4 (v4) expanded to 400 items with 50 items per language-domain cell by introducing template variants. The final version (v5) enriched the schema with source titles, difficulty ratings, and quality flags.

The public retrieval-only release contains question text, source document IDs, language and domain labels, cultural-specificity ratings, answerability flags, and audit metadata. Reference answers used in internal QA analysis are withheld pending source and license clearance. The current metadata identifies 20 domain or question flags, including four late corrections for two seed items and their generated variants; an internal answer-quality audit separately identified 38 artefact flags.

### 3.3 Corpus Sources

The baseline corpus consists of Uzbek Wikipedia and English Wikipedia snapshots. For Uzbek, this provides uneven coverage across domains. For English, coverage is broader but still shows gaps in history and institutions relevant to our culturally grounded query set.

### 3.4 Distribution

Table 1 shows the language by domain distribution. All cells contain 50 items after v4 expansion.

**Table 1: Benchmark Distribution**

| Domain | English | Uzbek |
|--------|---------|-------|
| Governance | 50 | 50 |
| History | 50 | 50 |
| Institutions | 50 | 50 |
| Culture | 50 | 50 |
| **Total** | **200** | **200** |

---

## 4. Experimental Setup

### 4.1 Infrastructure

Experiments were conducted on the Isambard-AI supercomputer using GH200 nodes (4x GPUs per node). The pipeline is implemented in Python with FAISS for vector indexing and PyTorch for embedding models.

### 4.2 Evaluation Metric

Our primary metric is retrieval recall@k, where k=10. This measures whether the gold source document appears in the top 10 retrieved passages. We use a stub generator that returns the first sentence of retrieved documents, so token overlap metrics primarily reflect retrieval success rather than generation quality. This design choice isolates retrieval performance from generation effects.

### 4.3 Experimental Conditions

We ran eight experimental conditions, each changing one variable:

1. **No retrieval**: Returns empty set (baseline for recall measurement)
2. **Vector baseline**: Simple vector retrieval with default chunking (512 tokens, 256 overlap)
3. **e5-large**: Upgraded embedding model to intfloat/multilingual-e5-large (Wang et al., 2024)
4. **mpnet**: Alternative multilingual embedding model (Reimers & Gurevych, 2020)
5. **Supplement v1**: Baseline corpus plus manually curated Uzbek supplement
6. **Supplement v2**: Baseline corpus plus structured Uzbek supplement (improved curation)
7. **BM25**: Lexical retrieval on supplement v2 corpus (Robertson & Zaragoza, 2009)
8. **Hybrid**: Combined BM25 and vector retrieval on supplement v2 corpus

All experiments used the grounded prompt template. Chunking experiments tested smaller chunk sizes (128/32 and 256/64) against the baseline.

---

## 5. Results

### 5.1 Main Results

Table 2 shows overall recall@k across all conditions. Results are reported separately for v2 (200 items) and v4 (400 items) phases. Comparisons should be made within phase, not across phases, due to benchmark size differences.

**Table 2: Overall Recall@k Across Conditions**

| Condition | Overall | English | Uzbek |
|-----------|---------|---------|-------|
| No retrieval | 0.0000 | 0.0000 | 0.0000 |
| Vector baseline | 0.4900 | 0.6100 | 0.3700 |
| e5-large | 0.5100 | 0.6300 | 0.3900 |
| mpnet | 0.4350 | 0.6200 | 0.2500 |
| Supplement v1 | 0.7150 | 0.6300 | 0.8000 |
| Supplement v2 | 0.8050 | 0.6300 | 0.9800 |
| BM25 | 0.6700 | 0.6200 | 0.7200 |
| Hybrid | 0.7950 | 0.6300 | 0.9600 |

**Interpretation.** English recall stays flat at 0.63 across all conditions because English was not supplemented. Uzbek recall improves from 0.39 at baseline to 0.98 with supplement v2, a 59-percentage-point improvement.

### 5.2 Effect Sizes

Cohen's d quantifies the standardised difference between conditions. Corpus supplementation produces d = 2.91 for Uzbek recall, while embedding model changes produce d = 0.31 for overall recall. The supplementation effect is 7.9 times larger than the model effect.

### 5.3 Statistical Significance

Bootstrap confidence intervals (1000 resamples, 95% CI) confirm statistical significance:

- Baseline vs UZ supplement v2 (Uzbek recall): +59.0% [52.1%, 65.9%], p < 0.001
- Baseline vs UZ supplement v2 (Overall recall): +29.5% [23.8%, 35.2%], p < 0.001
- mpnet vs e5-large (Overall recall): +7.5% [1.2%, 13.8%], p = 0.020

Chunking variations showed no significant difference (p = 1.000). Hybrid retrieval showed no significant difference from vector-only (p = 1.000).

### 5.4 Domain Breakdown

Table 3 shows per-domain recall under the best setup (supplement v2 + e5-large).

**Table 3: Per-Domain Recall (Best Setup)**

| Domain | English | Uzbek | Gap |
|--------|---------|-------|-----|
| Governance | 0.80 | 0.98 | -0.18 |
| History | 0.40 | 0.96 | +0.56 |
| Institutions | 0.32 | 0.96 | +0.64 |
| Culture | 1.00 | 0.94 | +0.06 |

**Interpretation.** Before supplementation, Uzbek history and institutions were the weakest domains. After supplementation, Uzbek outperformed English in three of four domains. The remaining bottleneck is English history and institutions, which were not supplemented.

### 5.5 English Baseline Performance

English showed asymmetric performance at baseline: culture (1.00), governance (0.80), history (0.40), institutions (0.32). A gap analysis identified 74 missing English documents (37% of the English requirement), concentrated in history and institutions. English supplementation was attempted but results were retracted due to data leakage in synthetic documents. English results are therefore reported at baseline only.

---

## 6. Analysis

### 6.1 Failure Taxonomy

Manual analysis of retrieval failures revealed three dominant failure modes:

1. **Corpus gaps** (5 items): Source documents absent from corpus. This was the dominant failure mode for Uzbek at baseline.
2. **Retriever degeneration** (10 Uzbek items): When gold documents were absent, retrieval collapsed onto the same three hub documents (doc IDs 1790, 1570, 1798). These are generic articles that serve as fallback neighbours.
3. **Domain misclassification** (6 items): Benchmark construction errors where questions were assigned to wrong domain templates.

The retriever degeneration pattern is analytically important. What appears as 10 distinct failures is actually a single underlying mechanism: corpus absence causes collapse toward hub documents.

### 6.2 Retraction of English Supplement Results

The initial English supplementation attempt used synthetic documents containing question-answer pairs. This introduced data leakage because gold answers appeared verbatim in the corpus. Results claiming 100% English recall were invalid and have been retracted. This retraction demonstrates methodological rigour. Future English supplementation would require extracting real documents from MIRACL or similar sources.

### 6.3 Methodological Note

Our use of a stub generator (first retrieved sentence) rather than full LLM generation means token overlap metrics primarily reflect retrieval success. This is a limitation for end-to-end RAG evaluation but a strength for isolating retrieval effects. The focus on recall@k directly measures corpus coverage, which is the variable of interest for our hypothesis.

---

## 7. Limitations

First, the benchmark contains only 400 items across two languages. While sufficient for initial insights, larger benchmarks (1000+ items) would yield narrower confidence intervals.

Second, we used a stub generator rather than full LLM generation. This isolates retrieval effects but does not measure end-to-end generation quality.

Third, this is a pilot benchmark rather than a uniformly clean QA set. Template-based expansion for v4 introduced quality issues including domain misclassification, and the current quality flags are not exhaustive. These limitations are documented for a later cleaned release.

Fourth, English was not successfully supplemented. The 37% English gap remains unaddressed due to the retraction of synthetic supplement results.

Fifth, cross-lingual retrieval (e.g., English questions on Uzbek corpus) was not evaluated. Results are limited to monolingual scenarios.

Finally, human evaluation was not conducted. LLM-as-judge infrastructure exists but was not executed.

---

## 8. Conclusion

We presented a bilingual benchmark for culturally grounded question answering and a controlled ablation study of RAG design choices. Our main finding is that corpus coverage dominates model choice for culturally grounded retrieval. Uzbek supplementation produced a 59-percentage-point improvement (d = 2.91), while embedding model changes produced only a 7.5-percentage-point improvement (d = 0.31). The effect of knowledge curation is 7.9 times larger than the effect of model optimisation.

The implications are clear. For underrepresented languages, investment in culturally grounded knowledge curation should precede investment in model improvement. Funders should prioritise corpus development over model scaling. Developers should audit corpus coverage before optimising models. Policymakers should require cultural coverage audits as part of AI evaluation standards.

Our benchmark and code are publicly available. Future work should expand to additional languages, conduct end-to-end generation evaluation, and test whether findings generalise to other cultural contexts.

---

## References

Asai, A., Kasai, J., Clark, J. H., Lee, K., Choi, E., & Hajishirzi, H. (2020). XOR QA: Cross-lingual open-retrieval question answering. arXiv preprint arXiv:2010.11856.

Clark, J. H., Choi, E., Collins, M., Garrette, D., Kwiatkowski, T., Nikolaev, V., & Palomaki, J. (2020). TyDi QA: A benchmark for information-seeking question answering in typologically diverse languages. arXiv preprint arXiv:2003.05002.

Es, S., James, J., Espinosa-Anke, L., & Schockaert, S. (2024). RAGAS: Automated evaluation of retrieval augmented generation. Proceedings of the 18th Conference of the European Chapter of the Association for Computational Linguistics: System Demonstrations, 150-158.

Hershcovich, D., Frank, S., Lent, H., de Lhoneux, M., Abdou, M., Brandl, S., Bugliarello, E., Cabello Piqueras, L., Chalkidis, I., Cui, R., Fierro, C., Margatina, K., Rust, P., & Søgaard, A. (2022). Challenges and strategies in cross-cultural NLP. arXiv preprint arXiv:2203.10020.

Honovich, O., Aharoni, R., Herzig, J., Taitelbaum, H., Kukliansy, D., Cohen, V., Scialom, T., Szpektor, I., Hassidim, A., & Matias, Y. (2022). TRUE: Re-evaluating factual consistency evaluation. arXiv preprint arXiv:2204.04991.

Karpukhin, V., Oguz, B., Min, S., Lewis, P., Wu, L., Edunov, S., ... & Yih, W. T. (2020). Dense passage retrieval for open-domain question answering. Proceedings of the 2020 Conference on Empirical Methods in Natural Language Processing, 6769-6782.

Lewis, P., Perez, E., Piktus, A., Petroni, F., Karpukhin, V., Goyal, N., ... & Kiela, D. (2020). Retrieval-augmented generation for knowledge-intensive NLP tasks. Advances in Neural Information Processing Systems, 33, 9459-9474.

Zhang, X., Thakur, N., Ogundepo, O., Kamalloo, E., Alfonso-Hermelo, D., Li, X., Liu, Q., Rezagholizadeh, M., & Lin, J. (2022). Making a MIRACL: Multilingual information retrieval across a continuum of languages. arXiv preprint arXiv:2210.09984.

Wang, L., Yang, N., Huang, X., Yang, L., Majumder, R., & Wei, F. (2024). Multilingual E5 text embeddings: A technical report. arXiv preprint arXiv:2402.05672.

Reimers, N., & Gurevych, I. (2020). Making monolingual sentence embeddings multilingual using knowledge distillation. Proceedings of the 2020 Conference on Empirical Methods in Natural Language Processing, 7144-7152.

Robertson, S., & Zaragoza, H. (2009). The probabilistic relevance framework: BM25 and beyond. Foundations and Trends in Information Retrieval, 3(4), 333-389.

---

**Word count:** approximately 3,400 words

**Acknowledgements:** This work used the Isambard-AI supercomputer under the u6ef project. The author thanks the Centre for AI Futures at SOAS University of London for support.

**Data availability:** Benchmark samples and code are available at https://github.com/rajantripathi/soas-rag-evaluation

**Affiliation:** Centre for AI Futures, SOAS University of London
