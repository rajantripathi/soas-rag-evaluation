# Targeted Corpus Coverage Repair in an English–Uzbek Retrieval Pilot

**Rajan Prasad Tripathi**

AI² Lab, American University of Technology, Uzbekistan; Centre for AI Futures, SOAS University of London

**Status:** Working manuscript for a descriptive research preprint. Historical retrieval results are transcribed from repository reports; the public-data structural audit is reproducible from the release. This manuscript does not report a new model run or a held-out generalisation experiment.

## Abstract

A retrieval failure can reflect missing source material as well as a retriever's inability to rank available evidence. We examine this distinction through an English–Uzbek pilot covering governance, history, institutions, and culture. Historical reports describe an evaluation of 200 questions in which targeted supplementation with evaluation-linked Uzbek sources increased Uzbek source hit rate from 39% to 98%, with the embedding model held fixed. Across the bilingual set, the corresponding change was 51% to 80.5%. An expanded evaluation retained the original items and added deterministic alternate phrasings, yielding 79.5% overall. We release 400 retrieval-only rows and audit their structure: they refer to 200 language-scoped source targets, each appearing in two question rows; 20 rows have quality flags and 74 English rows lack resolved source titles. The findings document coverage repair on known targets, not performance on unseen sources. We separate the descriptive historical evidence from public reproducibility, omit inferential statistics whose provenance remains unresolved, and specify a source-disjoint evaluation design for further work.

## 1. Introduction

Retrieval-augmented systems need relevant evidence to be both available and retrievable. If an intended source is absent from the corpus, changes to its ranking cannot recover that source. Conversely, source presence alone does not guarantee successful retrieval. These mechanisms require separate measurement.

This study examines a small English–Uzbek collection using questions assigned to governance, history, institutions, and culture. Its contribution is a documented case study of targeted source coverage repair, accompanied by a retrieval-only release and an executable structural audit. The work does not claim to introduce a new retrieval algorithm or establish that corpus interventions universally outperform model changes.

We address three questions: (1) what retrieval changes were reported after adding known missing Uzbek sources; (2) how the expanded question set relates to the original evaluation; and (3) what evidence the public artifact can support independently. Distinguishing these questions prevents a descriptive corpus-repair result from becoming an unsupported generalisation claim.

## 2. Related work

MIRACL provides a multilingual monolingual-retrieval benchmark across 18 languages, with relevance judgments produced by native speakers [1]. TyDi QA evaluates information-seeking question answering across typologically diverse languages [2]. These resources motivate attention to multilingual evaluation; we do not claim that their designs assume universal corpus adequacy or that this pilot establishes gaps in their cultural coverage.

Multilingual E5 provides multilingual embedding models trained through contrastive learning and subsequent fine-tuning [3]. We use historical comparisons involving its large variant as implementation-specific observations, subject to the encoding caveat below. RAGAs addresses automated assessment of retrieval-augmented generation [4]. The present public release supplies neither generated answers nor answer references, and therefore supports a narrower source-document retrieval task.

Our scope is an English–Uzbek coverage-repair case study with explicit data dependencies and quality limitations. No exhaustive novelty claim is made about prior corpus-curation research.

## 3. Data and construction

### 3.1 Evaluation phases

The original collection contained 200 items, balanced across two languages and four assigned domains. The historical v2 experiments used 100 English and 100 Uzbek questions. The v4 construction script preserved these items and generated one deterministic alternate phrasing per item, retaining its source target. Version v5 added source titles, heuristic difficulty labels, and quality flags. The English and Uzbek halves are not parallel translations.

The public release contains question IDs, language and domain labels, question text, source-document identifiers, answerability and cultural-specificity metadata, source titles, difficulty labels, and quality flags. Answer-bearing fields and source text are excluded. Cultural-specificity metadata and domain balance should not be interpreted as independent expert validation of cultural representativeness.

### 3.2 Reproducible structural audit

We audited the released JSONL with `scripts/audit_public_benchmark.py`. The [generated audit](../public_benchmark_structure.md) records its input SHA-256, allowing the counts to be tied to exact release bytes.

| Language | Question rows | Source targets | Flagged rows | Unresolved source titles |
| --- | ---: | ---: | ---: | ---: |
| English | 200 | 100 | 6 | 74 |
| Uzbek | 200 | 100 | 14 | 0 |
| Total | 400 | 200 | 20 | 74 |

Every row has one source target. Every language-scoped target appears in two rows. No exact question-text duplicates occur within a language. Each language-domain cell contains 50 rows. These properties confirm balanced row counts but do not establish 400 independent observations. Alternate phrasings sharing a source are related observations.

There are 16 domain-misclassification flags and four question-quality flags. Flagging is incomplete; unflagged rows cannot be treated as a manually validated clean subset. The 74 unresolved English titles are metadata gaps and should not be equated with 74 independently verified corpus omissions.

### 3.3 Corpus provenance and intervention

The repository's data-staging code references MIRACL English raw material, TyDi QA material, and Uzbek Wikipedia through `yakhyo/uz-wiki`. The exact historical corpus snapshots and indexes are not present in the public checkout. Consequently, this manuscript does not supply an independently verified corpus-size or snapshot-date claim.

The principal Uzbek supplement extracted structured rows for evaluation-linked source documents absent from the baseline corpus. Selection therefore used known evaluation targets. This is targeted coverage repair on the observed collection. It is not an intervention developed independently of the test set.

## 4. Retrieval and measurement

### 4.1 Metric

For question i, let G_i be its target source identifiers and R_i(k) the document identifiers attached to its top-k retrieved contexts. The source hit is H_i(k) = 1 when G_i and R_i(k) overlap, and 0 otherwise. The reported score is the mean of H_i(k) over questions.

The repository calls this Recall@k; we use **source hit rate** to distinguish it from fractional recall over multiple relevant documents. The checked-in experiment configurations inherit **k = 3** from `configs/base.yaml`. Without archived run configurations, this is configuration evidence rather than independently recovered runtime provenance. The historical reports label scores as Recall@k without restating the cutoff.

The standalone public scorer takes a ranked list of source IDs per question and counts missing predictions as misses. Its oracle mode supplies gold source IDs as predictions and checks wiring only; it is not a retrieval result.

### 4.2 Implementations

The checked-in retrievers include a TF–IDF-style simple vector implementation, BM25, embedding retrieval, and a hybrid implementation. Embedding retrieval uses Sentence Transformers to encode texts with normalised vectors and NumPy dot products for ranking. The inspected implementation does not use FAISS. Historical reports identify `intfloat/multilingual-e5-large` and `sentence-transformers/paraphrase-multilingual-mpnet-base-v2` as compared embedding models.

The current embedding code passes raw text to `encode`; it does not explicitly add E5 query and passage prefixes. The model card specifies those prefixes for retrieval [5]. This limits interpretation of the historical model comparison. A corrected encoding experiment must be reported as a new run, with pinned model revisions and encoding settings, rather than silently replacing historical scores.

The historical compute acknowledgement identifies Isambard-AI project u6ef. Full run logs, library versions, model revisions, and index artifacts are not distributed. Generation is a first-sentence stub; its overlap-based diagnostics are excluded from the paper's result claims.

## 5. Descriptive historical results

### 5.1 Targeted supplementation on v2

Table 2 transcribes the [v2 supplementation report](../../results/reports/manual_eval_v2_uz_supplement_v2_report_20260309.md). Each condition uses 100 questions per language.

| Corpus condition with e5-large | English | Uzbek | Overall |
| --- | ---: | ---: | ---: |
| Baseline | 63.0% | 39.0% | 51.0% |
| Uzbek supplement v1 | 63.0% | 80.0% | 71.5% |
| Uzbek supplement v2 | 63.0% | 98.0% | 80.5% |

The reported baseline-to-v2 increase is 59 percentage points on the Uzbek subset and 29.5 points overall. English is unchanged in this supplementation comparison. Adding source material selected against known targets substantially changed the reported outcome, but does not establish performance on targets unseen during curation.

### 5.2 Embedding comparison on v2

The [embedding report](../../results/reports/manual_eval_v2_embedding_report_20260308.md) describes a fixed baseline corpus and the following scores:

| Retriever | English | Uzbek | Overall |
| --- | ---: | ---: | ---: |
| Simple vector | 61.0% | 37.0% | 49.0% |
| Multilingual mpnet | 62.0% | 25.0% | 43.5% |
| Multilingual E5 large | 63.0% | 39.0% | 51.0% |

The mpnet-to-E5 difference is 14 points for Uzbek and 7.5 overall. Comparisons with supplementation must use the same population. Even then, targeted source addition and model replacement are different interventions, and the E5 encoding caveat prevents treating these scores as definitive model capability estimates.

### 5.3 Expanded v4 evaluation

The [v4 report](../../results/reports/manual_eval_v4_research_report_20260309.md) records 79.5% overall with supplement v2 and E5: 63.0% English and 96.0% Uzbek. The [hybrid report](../../results/reports/manual_eval_v4_hybrid_report_20260309.md) records the same aggregate scores for hybrid retrieval; BM25 scores 67.0% overall, 62.0% English, and 72.0% Uzbek. Equality of aggregate scores does not establish equality of per-item outcomes or statistical equivalence.

| Domain, v4 E5 with supplement v2 | English | Uzbek |
| --- | ---: | ---: |
| Governance | 80% | 98% |
| History | 40% | 96% |
| Institutions | 32% | 96% |
| Culture | 100% | 94% |

This phase measures performance on the original questions plus template variants sharing their targets. It is a phrasing-sensitivity check, not replication on 200 additional independent sources. The 98% Uzbek v2 result and 96% v4 result must be identified by phase.

### 5.4 Statistical provenance

We report descriptive scores only. Earlier repository narratives included Cohen's d, bootstrap intervals, and paired-test p-values. Their exact provenance remains unresolved. In particular, the checked-in pooled-population-standard-deviation formula applied to binary means of 0.39 and 0.98 yields approximately 1.64, rather than the historically reported 2.91. We do not substitute this arithmetic result for a verified inferential analysis.

Paired predictions and a verified run-to-condition mapping are needed to reconstruct comparisons. Source-group dependence must also be accounted for in expanded-set uncertainty estimates. Accordingly, this manuscript makes no significance or statistical-equivalence claims.

## 6. Limitations and research integrity

**Evaluation-targeted curation.** The intervention uses known source labels. Its observed improvement cannot establish a generalisation benefit on untouched questions or sources. Selection and evaluation decisions are not blinded.

**Question quality and dependence.** Template artifacts, domain mismatches, and incomplete flags remain. Source-sharing variants increase row count without increasing distinct targets. Human linguistic review and relevance assessment have not been completed.

**Source labels.** A source-ID match measures recovery of the designated source, not necessarily every valid answer source. Alternative evidence may be counted as a miss. Topic coverage and cultural representativeness have not been independently validated.

**Model and corpus provenance.** Historical snapshots, complete predictions, and encoding details need recovery or replacement by a fully specified new experiment. Current code is insufficient to establish every historical runtime setting.

**Retracted English supplementation.** An earlier synthetic English supplement included reference-answer text; its results were invalidated and are excluded here. This does not resolve the separate issue of evaluation-targeted Uzbek source selection.

**Scope.** The study does not measure generated-answer quality, cross-lingual retrieval, or general performance across low-resource languages. The dataset's labels should not be used to rank cultures or communities.

## 7. Design for a confirmatory extension

A stronger follow-up requires newly collected, source-disjoint test targets that have not informed corpus curation. Merely splitting the current collection after target-directed supplementation would not produce an untouched test set. All question variants sharing a source must remain in the same partition.

Before evaluation, freeze corpus snapshots, question annotations, source identifiers, model revisions, input-prefix policy, chunking, and cutoff. Compare the same retrievers on the same corpora, including correctly configured E5. Report both source availability in the corpus and hit rate conditional on availability; this separates coverage repair from ranking performance.

Publish retrieval-only per-question predictions with stable IDs, configuration hashes, corpus manifests, and a run-to-condition mapping. Report results on all reviewed items and predeclared quality subsets. Estimate paired differences with source-group-aware uncertainty rather than treating alternate phrasings as independent observations. This is a proposed design; no confirmatory result is claimed here.

## 8. Conclusion

Historical reports show a large descriptive change after adding known missing Uzbek sources, with E5 held fixed: 39% to 98% on 100 Uzbek questions. The public structural audit establishes that the expanded 400-row release contains 200 source targets with two question phrasings each. Together, these observations support a scoped coverage-repair case study and an inspectable pilot resource. Held-out source collection, annotation review, and reproducible model reruns are needed to establish broader empirical claims.

## Data, code, and acknowledgements

The [repository](https://github.com/rajantripathi/soas-rag-evaluation) provides the public evaluator and structural audit. The dataset is available on [Hugging Face](https://huggingface.co/datasets/Rajan2026/soas-english-uzbek-rag-evaluation) and under [DOI 10.5281/zenodo.21067667](https://doi.org/10.5281/zenodo.21067667). The dataset DOI identifies the data release, not this manuscript. Code is MIT-licensed and the public dataset is CC BY 4.0. Excluded answer-bearing material and corpora are not implied to share those redistribution permissions.

Reported historical computations used Isambard-AI under project u6ef. This acknowledgement does not imply current compute access. The author-maintained artifact does not represent an official institutional position.

## References

1. Zhang, X., et al. (2023). [MIRACL: A Multilingual Retrieval Dataset Covering 18 Diverse Languages](https://aclanthology.org/2023.tacl-1.63/). *Transactions of the Association for Computational Linguistics*, 11, 1114–1131.
2. Clark, J. H., et al. (2020). [TyDi QA: A Benchmark for Information-Seeking Question Answering in Typologically Diverse Languages](https://aclanthology.org/2020.tacl-1.30/). *Transactions of the Association for Computational Linguistics*, 8, 454–470.
3. Wang, L., et al. (2024). [Multilingual E5 Text Embeddings: A Technical Report](https://arxiv.org/abs/2402.05672). arXiv:2402.05672.
4. Es, S., James, J., Espinosa Anke, L., and Schockaert, S. (2024). [RAGAs: Automated Evaluation of Retrieval Augmented Generation](https://aclanthology.org/2024.eacl-demo.16/). *EACL System Demonstrations*, 150–158.
5. intfloat. [multilingual-e5-large model card](https://huggingface.co/intfloat/multilingual-e5-large). Encoding instructions, accessed 6 October 2026.
