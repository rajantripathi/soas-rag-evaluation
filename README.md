# SOAS RAG Evaluation — English–Uzbek Retrieval Pilot

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21067667.svg)](https://doi.org/10.5281/zenodo.21067667)
[![Checks](https://github.com/rajantripathi/soas-rag-evaluation/actions/workflows/public-artifact.yml/badge.svg)](https://github.com/rajantripathi/soas-rag-evaluation/actions/workflows/public-artifact.yml)
![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)
[![Code: MIT](https://img.shields.io/badge/code-MIT-blue.svg)](LICENSE)

**How much does missing source material constrain multilingual retrieval?** This research pilot examines English and Uzbek questions about governance, history, institutions, and culture. It combines a public retrieval-only dataset, an evaluation harness, and reports from a sequence of corpus and retriever experiments.

The main reported finding is that targeted Uzbek corpus supplementation increased source-document retrieval from **39% to 98%** on the 100 Uzbek items in the historical v2 evaluation. The supplementation deliberately added evaluation-linked sources missing from the corpus. This is evidence of coverage repair on a known evaluation set; generalisation to unseen questions requires a held-out study.

## Start here

- **Review the research:** [Evidence and reviewer guide](docs/reviewer_guide.md), including experiment phases, claim boundaries, and statistical provenance.
- **Inspect the data structure:** [Reproducible audit](research_outputs/public_benchmark_structure.md): 400 question rows, 200 source targets, and two phrasings per target.
- **Inspect the data:** [Dataset card](hf_dataset/README.md), [400-row JSONL](hf_dataset/manual_eval_v5_retrieval_only.jsonl), and [quality audit](research_outputs/dataset_quality_audit_20260309.md).
- **Reuse the evaluator:** Follow the dependency-free quickstart below.
- **Read the research narrative:** [Working paper](research_outputs/workshop_paper_2026/paper_final.md) and [policy brief](research_outputs/policy_brief_culturally_grounded_ai.md). These are repository research outputs; their presence does not establish peer-reviewed publication.

## Reported retrieval results

| Evaluation phase and condition | Items | English | Uzbek | Overall |
| --- | ---: | ---: | ---: | ---: |
| v2: e5-large, baseline corpus | 200 | 63% | 39% | 51% |
| v2: e5-large, Uzbek supplement v2 | 200 | 63% | 98% | 80.5% |
| v4: e5-large, Uzbek supplement v2 | 400 | 63% | 96% | 79.5% |

Sources: [v2 supplementation report](results/reports/manual_eval_v2_uz_supplement_v2_report_20260309.md) and [v4 research report](results/reports/manual_eval_v4_research_report_20260309.md). These experiments use a top-k cutoff of 3. The metric is the proportion of questions with at least one gold source document retrieved, called Recall@k in this repository.

The v2 supplementation gain is **59 percentage points for Uzbek**, or **29.5 points overall**. The embedding comparison (mpnet to e5-large) yielded **14 points for Uzbek**, or **7.5 points overall**. Compare gains within the same population; the earlier “7.9×” framing mixed Uzbek-only and overall results. These are different interventions, not a universal ranking of corpus curation and model choice.

The 400-row **v5 public release** adds metadata to the expanded benchmark. It should not be confused with the 200-item v2 experiment behind the 39% → 98% result. Historical significance and effect-size figures require further verification; see the [statistical provenance note](docs/reviewer_guide.md#statistical-provenance).

## Quickstart: inspect and score the public release

Python 3.10+ is sufficient for the local evaluator; no GPU, model download, or additional packages are needed.

```bash
git clone https://github.com/rajantripathi/soas-rag-evaluation.git
cd soas-rag-evaluation
python3 scripts/compute_retrieval_recall.py --oracle-check --k 3
python3 -m unittest discover -s tests -v
```

The oracle check uses gold source IDs as predictions. A score of 1.0 checks evaluator wiring only; it is not a retrieval-model result.

To evaluate your own retriever, create a JSONL file with one row per question, using the dataset's exact question and source-document IDs:

```json
{"id": "your-dataset-item-id", "retrieved_doc_ids": ["first-doc-id", "second-doc-id"]}
```

```bash
python3 scripts/compute_retrieval_recall.py --predictions predictions.jsonl --k 3 --json
```

Retrieved IDs must be ranked from highest to lowest relevance. Missing predictions count as misses. Output includes language and domain breakdowns. This evaluator measures whether any target source appears in the top k; it does not measure answer correctness or fractional recall over multiple relevant documents.

The dataset is also available on [Hugging Face](https://huggingface.co/datasets/Rajan2026/soas-english-uzbek-rag-evaluation):

```python
from datasets import load_dataset  # pip install datasets

dataset = load_dataset("Rajan2026/soas-english-uzbek-rag-evaluation", split="train")
```

## Research scope and limitations

- **Pilot data:** 400 rows, balanced across two languages and four domains. Template artifacts, domain mismatches, and incomplete quality flags remain. Unflagged rows are not necessarily manually validated.
- **Targeted supplementation:** Added sources were selected using known evaluation targets. An independent held-out evaluation is needed to establish generalisation.
- **Retrieval only:** Generation is a first-sentence stub. Human evaluation, LLM-as-judge evaluation, and cross-lingual retrieval have not been completed.
- **Retracted English experiment:** Synthetic English supplementation included gold-answer text. Its results are invalid and excluded from the table above; English is reported at baseline only.
- **Reproducibility:** Public data and scoring can be checked locally. Historical runs cannot be reproduced from this checkout alone: source corpus snapshots, indexes, and full prediction artifacts are excluded.

See [limitations](docs/limitations.md), [methodology](docs/methodology.md), and [historical reproducibility notes](docs/isambard_reproducibility.md).

## Pipeline and repository layout

| Location | Contents |
| --- | --- |
| [`hf_dataset/`](hf_dataset/) | Retrieval-only dataset, preview, and release metadata |
| [`src/`](src/) and [`scripts/`](scripts/) | Retrieval, evaluation, corpus preparation, and reporting |
| [`configs/`](configs/) | Experiment configurations |
| [`results/reports/`](results/reports/) | Historical experiment reports |
| [`research_outputs/`](research_outputs/) | Working paper, brief, tables, figures, and audits |
| [`docs/`](docs/README.md) | Reviewer guide, methodology, and architecture |
| [`slurm/`](slurm/) | Historical cluster job templates |
| [`tests/`](tests/) | Public evaluator and release-integrity checks |

For the full pipeline, use the [environment and execution notes](docs/isambard_reproducibility.md) and [technical architecture](docs/technical_architecture.md). Model-backed workflows require the project dependencies and corpus downloads. Report-generation scripts depend on historical artifacts and can overwrite checked-in reports; they are not part of the public evaluator quickstart.

## Citation and licensing

```bibtex
@dataset{tripathi_2026_soas_en_uz_rag,
  author       = {Tripathi, Rajan Prasad},
  title        = {SOAS English-Uzbek RAG Evaluation (Retrieval-Only)},
  year         = {2026},
  publisher    = {Zenodo},
  version      = {manual_eval_v5},
  doi          = {10.5281/zenodo.21067667},
  url          = {https://doi.org/10.5281/zenodo.21067667}
}
```

Machine-readable citation: [CITATION.cff](CITATION.cff). Code: [MIT](LICENSE). Public dataset: CC BY 4.0, as recorded in the [dataset card](hf_dataset/README.md).

## Author and acknowledgements

Rajan Prasad Tripathi. Author affiliations: AI² Lab, American University of Technology, Uzbekistan; Centre for AI Futures, SOAS University of London.

This repository is maintained by the author and does not represent an official institutional position. Reported computations used the Isambard-AI supercomputer under project u6ef; this acknowledgement does not imply current or future access.

Contributions and reproducible issue reports are welcome; see [CONTRIBUTING.md](CONTRIBUTING.md).
