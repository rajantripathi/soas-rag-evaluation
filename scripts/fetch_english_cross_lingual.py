#!/usr/bin/env python3
"""
Fetch English Wikipedia articles for cross-lingual evaluation.

This will create a small English corpus with articles that correspond
to Uzbek topics, enabling proper cross-lingual evaluation.
"""

import json
import requests
from pathlib import Path
import time

# Wikipedia API endpoints
WIKIPEDIA_API = "https://en.wikipedia.org/w/api.php"

# Topics to fetch (Uzbek title -> English title)
TOPICS_TO_FETCH = {
    "Rossiya": "Russia",
    "Amerika": "Americas",
    "Yevropa": "Europe",
    "Oʻzbekiston": "Uzbekistan",
    "Vikipediya": "Wikipedia",
    "Biologiya": "Biology",
    "Astronomiya": "Astronomy",
    "Algoritm": "Algorithm",
    "Antarktida": "Antarctica",
    "Litva": "Lithuania",
    "Toshkent": "Tashkent",
    "Samarqand": "Samarkand",
}

def fetch_wikipedia_article(title, lang="en"):
    """Fetch article content from Wikipedia."""
    params = {
        "action": "query",
        "prop": "extracts",
        "explaintext": True,
        "titles": title,
        "format": "json",
        "redirects": True,
    }
    
    try:
        response = requests.get(f"https://{lang}.wikipedia.org/w/api.php", params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        pages = data["query"]["pages"]
        for page_id, page_data in pages.items():
            if page_id == "-1":
                return None  # Page doesn't exist
            
            return {
                "title": page_data.get("title", title),
                "text": page_data.get("extract", ""),
                "page_id": page_id,
            }
    except Exception as e:
        print(f"  Error fetching {title}: {e}")
        return None

def create_document(title, text, doc_id, language="en"):
    """Create a document in the expected format."""
    return {
        "doc_id": doc_id,
        "chunk_id": f"{doc_id}::0",
        "source": "wikipedia_cross_lingual",
        "language": language,
        "title": title,
        "text": text[:2000],  # First 2000 chars
        "metadata": {
            "dataset_dir": "wikipedia_en",
            "fetch_strategy": "wikipedia_api_cross_lingual",
        }
    }

def main():
    base = Path("/home/u6ef/rajantripathi.u6ef/soas_rag_eval")
    output_file = base / "data/processed/corpus_cross_lingual_english.jsonl"
    
    print("Fetching English Wikipedia articles for cross-lingual evaluation...")
    print()
    
    documents = []
    doc_id = 1000  # Start from 1000 to avoid conflicts
    
    for uz_title, en_title in TOPICS_TO_FETCH.items():
        print(f"Fetching: {en_title} (for Uzbek: {uz_title})")
        
        article = fetch_wikipedia_article(en_title, "en")
        
        if article and article["text"]:
            doc = create_document(article["title"], article["text"], str(doc_id), "en")
            documents.append(doc)
            print(f"  ✓ Fetched {len(article[\"text\"])} chars")
            doc_id += 1
        else:
            print(f"  ✗ Not found")
        
        time.sleep(1)  # Be nice to the API
    
    # Save to file
    with open(output_file, "w") as f:
        for doc in documents:
            f.write(json.dumps(doc, ensure_ascii=False) + "\\n")
    
    print()
    print(f"Fetched {len(documents)} articles")
    print(f"Saved to: {output_file}")

if __name__ == "__main__":
    main()
