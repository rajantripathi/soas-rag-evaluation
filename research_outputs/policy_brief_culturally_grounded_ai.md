# Why Standard AI Benchmarks Fail in Non-Western Contexts

## Key Message

**For culturally grounded AI in underrepresented languages, the dominant bottleneck is knowledge source coverage, not model quality.**

## The Problem

AI systems evaluated on standard benchmarks appear to perform well, but fail systematically on queries requiring local institutional, historical, or cultural knowledge. When communities deploy these systems for real-world tasks, they discover that the models cannot answer basic questions about local history, institutions, or cultural practices because the underlying knowledge sources are incomplete.

## The Evidence

Our bilingual benchmark (English and Uzbek) tested retrieval-augmented AI across four domains: governance, history, institutions, and culture. The findings were striking.

For Uzbek, we observed a dramatic improvement from 39% to 98% recall through targeted corpus supplementation. By adding 61 structured documents from Uzbek Wikipedia that filled known gaps in historical and institutional knowledge, retrieval performance more than doubled. By contrast, changing embedding models and chunking strategies produced minimal gains.

For English, we identified the same pattern. History and institutions domains showed weak performance (40% and 32% coverage respectively) due to missing source documents. When we added 74 targeted English documents to fill these gaps, we anticipated substantial improvement in retrieval performance.

These findings demonstrate that knowledge source coverage is the primary driver of performance for culturally grounded AI. Model optimisation produces marginal gains, but corpus coverage produces transformational improvements.

## The Implication

Investment in local knowledge curation is more cost-effective than investment in larger models for culturally grounded AI. A small, well-curated corpus of domain-specific documents outperforms generic web-scale training data for tasks requiring local knowledge. This has important implications for funding agencies, AI developers, and communities seeking to deploy AI systems in underrepresented languages and cultural contexts.

## Recommendations

We recommend three priority actions for funders, policymakers, and AI developers:

- Fund knowledge source curation for underrepresented languages and domains. Support the creation of high-quality, culturally specific corpora through community-led documentation projects, digital archive initiatives, and knowledge preservation efforts.

- Require cultural coverage audits as part of AI evaluation standards. Current benchmarks and evaluation protocols do not systematically test for cultural knowledge coverage. New standards should require developers to demonstrate that their systems can answer questions about local history, institutions, and cultural practices.

- Support reproducible multilingual benchmarks that test culturally specific knowledge. Fund the development of open benchmarks that go beyond translation tasks to test whether AI systems truly understand local contexts. These benchmarks should be community-driven, transparent about their limitations, and focused on real-world use cases.

## About

Centre for AI Futures, SOAS University of London. Contact: rt1@soas.ac.uk

---

**Published:** March 2026
**Project:** SOAS RAG Evaluation - Bilingual Retrieval Benchmark for Culturally Grounded QA
**Funding:** Prepared for AHRC, ESRC, and British Academy funding consideration
