#!/usr/bin/env python3
"""
Create a proper cross-lingual evaluation dataset.

Strategy: Find overlapping topics that exist in BOTH languages,
then test if multilingual embeddings can retrieve across languages.

Focus: 10-15 overlapping topics from Uzbek corpus that have
English equivalents available.
"""

import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Topics that exist in Uzbek corpus and have English equivalents
CROSS_LINGUAL_TOPICS = {
    # Uzbek article -> English article
    "Rossiya": "Russia",
    "Amerika": "America", 
    "Yevropa": "Europe",
    "Oʻzbekiston": "Uzbekistan",
    "Vikipediya": "Wikipedia",
    "Biologiya": "Biology",
    "Astronomiya": "Astronomy",
    "Algoritm": "Algorithm",
    "Antarktida": "Antarctica",
    "Litva": "Lithuania",
}

def read_corpus(corpus_file):
    """Read corpus from JSONL file."""
    docs = []
    with open(corpus_file) as f:
        for line in f:
            if line.strip():
                docs.append(json.loads(line))
    return docs

def find_docs_by_title(corpus, titles, language="en"):
    """Find documents with matching titles."""
    title_to_doc = {}
    for doc in corpus:
        title = doc.get("title", "")
        if title in titles:
            title_to_doc[title] = doc
    return title_to_doc

def create_cross_lingual_questions():
    """Create test questions for overlapping topics."""
    questions = []
    
    # For each topic, create a question in both languages
    topics = [
        {
            "uz_title": "Rossiya",
            "en_title": "Russia", 
            "uz_question": "Rossiya nima?",
            "en_question": "What is Russia?",
            "domain": "governance"
        },
        {
            "uz_title": "Oʻzbekiston",
            "en_title": "Uzbekistan",
            "uz_question": "Oʻzbekiston nima?",
            "en_question": "What is Uzbekistan?",
            "domain": "governance"
        },
        {
            "uz_title": "Vikipediya",
            "en_title": "Wikipedia",
            "uz_question": "Vikipediya nima?",
            "en_question": "What is Wikipedia?",
            "domain": "institutions"
        },
        {
            "uz_title": "Biologiya",
            "en_title": "Biology",
            "uz_question": "Biologiya nima?",
            "en_question": "What is Biology?",
            "domain": "culture"
        },
        {
            "uz_title": "Yevropa",
            "en_title": "Europe",
            "uz_question": "Yevropa nima?",
            "en_question": "What is Europe?",
            "domain": "governance"
        },
    ]
    
    for i, topic in enumerate(topics):
        # Uzbek question about Uzbek doc (baseline - should work)
        questions.append({
            "id": f"xl_uz_baseline_{i}",
            "language": "uz",
            "query_language": "uz",
            "corpus_language": "uz",
            "question": topic["uz_question"],
            "target_title": topic["uz_title"],
            "domain": topic["domain"],
            "expected": "high_recall"
        })
        
        # English question about English doc (baseline - should work)
        questions.append({
            "id": f"xl_en_baseline_{i}",
            "language": "en",
            "query_language": "en",
            "corpus_language": "en",
            "question": topic["en_question"],
            "target_title": topic["en_title"],
            "domain": topic["domain"],
            "expected": "high_recall"
        })
        
        # Uzbek question about English doc (cross-lingual test)
        questions.append({
            "id": f"xl_uz_on_en_{i}",
            "language": "uz",
            "query_language": "uz",
            "corpus_language": "en",
            "question": topic["uz_question"],
            "target_title": topic["en_title"],
            "domain": topic["domain"],
            "expected": "tests_cross_lingual"
        })
        
        # English question about Uzbek doc (cross-lingual test)
        questions.append({
            "id": f"xl_en_on_uz_{i}",
            "language": "en",
            "query_language": "en",
            "corpus_language": "uz",
            "question": topic["en_question"],
            "target_title": topic["uz_title"],
            "domain": topic["domain"],
            "expected": "tests_cross_lingual"
        })
    
    return questions

def main():
    base = Path("/home/u6ef/rajantripathi.u6ef/soas_rag_eval")
    
    # Read current corpora
    uz_corpus = read_corpus(base / "data/processed/corpus_uzbek_only.jsonl")
    en_corpus = read_corpus(base / "data/processed/corpus_english_only.jsonl")
    
    print("Current corpus status:")
    print(f"  Uzbek docs: {len(uz_corpus)}")
    print(f"  English docs: {len(en_corpus)}")
    print()
    
    # Find which Uzbek topics we have
    uz_titles = set(doc.get("title", "") for doc in uz_corpus)
    print("Uzbek topics available:")
    for uz, en in CROSS_LINGUAL_TOPICS.items():
        if uz in uz_titles:
            print(f"  ✓ {uz} (needs English: {en})")
        else:
            print(f"  ✗ {uz} (not in corpus)")
    print()
    
    # Check if we have English articles
    en_titles = set(doc.get("title", "") for doc in en_corpus)
    print("English topics available:")
    for uz, en in CROSS_LINGUAL_TOPICS.items():
        if en in en_titles:
            print(f"  ✓ {en}")
        else:
            print(f"  ✗ {en} (MISSING)")
    print()
    
    # Create test questions
    questions = create_cross_lingual_questions()
    
    # Save questions
    output_file = base / "data/eval/cross_lingual_test.jsonl"
    output_file.parent.mkdir(exist_ok=True, parents=True)
    
    with open(output_file, "w") as f:
        for q in questions:
            f.write(json.dumps(q, ensure_ascii=False) + "\\n")
    
    print(f"Created {len(questions)} test questions")
    print(f"Saved to: {output_file}")
    print()
    print("Test breakdown:")
    print("  Baseline (matched language): 10 questions")
    print("  Cross-lingual (mismatched): 10 questions")
    print()
    print("NOTE: English corpus is too small for proper evaluation.")
    print("Recommendation: Fetch English Wikipedia articles for the Uzbek topics.")

if __name__ == "__main__":
    main()
