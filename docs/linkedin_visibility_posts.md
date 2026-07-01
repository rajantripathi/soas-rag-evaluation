# LinkedIn Visibility Drafts

These drafts are written for AI engineering leaders. They use grounded claims and avoid depending on upstream OSS merge timing.

## Post 1: Dataset Release

I have released a small English-Uzbek RAG evaluation benchmark for retrieval-side evaluation.

The public dataset is now live on Hugging Face with 400 retrieval-evaluation rows, dataset viewer support, a Zenodo DOI, and a retrieval-only schema.

The engineering question is simple:

Before tuning embeddings, prompts, or rerankers, can the system retrieve the source document that actually contains the answer?

In this benchmark setting, targeted Uzbek corpus supplementation improved retrieval recall from 39% to 98% without changing the model. The result is specific to this dataset, but the lesson is broadly useful for multilingual RAG work: source coverage needs to be measured before model choice is over-optimized.

Dataset: https://huggingface.co/datasets/Rajan2026/soas-english-uzbek-rag-evaluation
Repository: https://github.com/rajantripathi/soas-rag-evaluation
DOI: https://doi.org/10.5281/zenodo.21067667

## Post 2: Why Retrieval-Only

I deliberately made the public Hugging Face release retrieval-only.

It includes questions, language/domain labels, and source-document targets. It excludes answer text, retrieved contexts, excerpts, and source text.

That makes the benchmark narrower, but cleaner.

For RAG evaluation, the first failure mode is often not generation quality. It is source coverage: the relevant document is missing, badly indexed, or not retrievable. A retrieval-only benchmark makes that failure visible without mixing it with answer correctness or faithfulness metrics.

This is especially important in multilingual and low-resource settings, where missing corpus coverage can look like a model weakness.

## Post 3: Practical Recall@k Workflow

A practical way to evaluate multilingual RAG retrieval:

1. Start with a set of questions.
2. Attach source-document IDs for the expected supporting evidence.
3. Run your retriever.
4. Store retrieved document IDs.
5. Compute recall@k by checking whether the expected source ID appears in the retrieved set.
6. Slice the result by language and domain.

That workflow is simple, but it prevents a common mistake: tuning the model before measuring whether the corpus contains the required evidence.

I added a minimal recall@k evaluator for the English-Uzbek benchmark:

https://github.com/rajantripathi/soas-rag-evaluation

## Post 4: Industry Lesson

The most useful lesson from this English-Uzbek RAG benchmark is not "use this model" or "use this vector database."

It is this:

For culturally grounded multilingual RAG, source coverage can be the first bottleneck.

In the Uzbek side of the benchmark, targeted corpus supplementation improved retrieval recall from 39% to 98% in this specific setup. Embedding-model changes had a much smaller observed effect.

That does not prove a universal rule. It does show why serious RAG evaluation needs to separate:

- corpus coverage
- retrieval behavior
- generation quality
- answer faithfulness

If those are mixed together too early, teams can spend weeks optimizing the wrong layer.
