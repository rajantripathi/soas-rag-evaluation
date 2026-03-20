#!/usr/bin/env python3
"""
Design a robust cross-lingual evaluation.

Principles:
1. 30+ topic pairs (minimum for statistical validity)
2. Multiple question types per topic (what, how, where, list)
3. Harder queries (not just title matches)
4. Multiple domains (geography, science, culture, tech)
5. Confidence intervals via bootstrap
"""

import json
from pathlib import Path

# Select 30 topics with clear English equivalents
# Each topic gets 2-3 question types to test different aspects

topics = [
    # GEOGRAPHY - Countries
    {
        "uzbek_title": "Oʻzbekiston",
        "english_title": "Uzbekistan",
        "domain": "geography",
        "questions": [
            {"uz": "Oʻzbekiston poytaxti qayer?", "en": "What is the capital of Uzbekistan?", "type": "factual"},
            {"uz": "Oʻzbekiston qaerdagi davlat?", "en": "Where is Uzbekistan located?", "type": "location"},
            {"uz": "Oʻzbekiston", "en": "Uzbekistan", "type": "direct"},
        ]
    },
    {
        "uzbek_title": "Rossiya",
        "english_title": "Russia",
        "domain": "geography",
        "questions": [
            {"uz": "Rossiya maydoni qancha?", "en": "What is the area of Russia?", "type": "factual"},
            {"uz": "Rossiya poytaxti", "en": "Capital of Russia", "type": "keyword"},
            {"uz": "Rossiya", "en": "Russia", "type": "direct"},
        ]
    },
    {
        "uzbek_title": "Qozogʻiston",
        "english_title": "Kazakhstan",
        "domain": "geography",
        "questions": [
            {"uz": "Qozogʻiston poytaxti qayer?", "en": "What is the capital of Kazakhstan?", "type": "factual"},
            {"uz": "Qozogʻiston", "en": "Kazakhstan", "type": "direct"},
        ]
    },
    {
        "uzbek_title": "Turkiya",
        "english_title": "Turkey",
        "domain": "geography",
        "questions": [
            {"uz": "Turkiya qaysi qitʼada?", "en": "Which continent is Turkey in?", "type": "factual"},
            {"uz": "Turkiya", "en": "Turkey", "type": "direct"},
        ]
    },
    {
        "uzbek_title": "Amerika",
        "english_title": "United States",
        "domain": "geography",
        "questions": [
            {"uz": "Amerika Qoʻshma Shtatlari aholisi", "en": "Population of United States", "type": "factual"},
            {"uz": "Amerika", "en": "United States", "type": "direct"},
        ]
    },
    {
        "uzbek_title": "Yevropa",
        "english_title": "Europe",
        "domain": "geography",
        "questions": [
            {"uz": "Yevropa davlatlari soni", "en": "Number of countries in Europe", "type": "factual"},
            {"uz": "Yevropa", "en": "Europe", "type": "direct"},
        ]
    },
    {
        "uzbek_title": "Osiyo",
        "english_title": "Asia",
        "domain": "geography",
        "questions": [
            {"uz": "Osiyo maydoni", "en": "Area of Asia", "type": "factual"},
            {"uz": "Osiyo", "en": "Asia", "type": "direct"},
        ]
    },
    {
        "uzbek_title": "Markaziy Osiyo",
        "english_title": "Central Asia",
        "domain": "geography",
        "questions": [
            {"uz": "Markaziy Osiyo davlatlari", "en": "Central Asian countries", "type": "list"},
            {"uz": "Markaziy Osiyo", "en": "Central Asia", "type": "direct"},
        ]
    },
    {
        "uzbek_title": "Antarktida",
        "english_title": "Antarctica",
        "domain": "geography",
        "questions": [
            {"uz": "Antarktida aholisi bormi?", "en": "Does Antarctica have population?", "type": "factual"},
            {"uz": "Antarktida", "en": "Antarctica", "type": "direct"},
        ]
    },
    # GEOGRAPHY - Cities
    {
        "uzbek_title": "Toshkent",
        "english_title": "Tashkent",
        "domain": "cities",
        "questions": [
            {"uz": "Toshkent aholisi", "en": "Population of Tashkent", "type": "factual"},
            {"uz": "Toshkent qaerda?", "en": "Where is Tashkent located?", "type": "location"},
            {"uz": "Toshkent", "en": "Tashkent", "type": "direct"},
        ]
    },
    {
        "uzbek_title": "Samarqand",
        "english_title": "Samarkand",
        "domain": "cities",
        "questions": [
            {"uz": "Samarqand tarixi", "en": "History of Samarkand", "type": "factual"},
            {"uz": "Samarqand", "en": "Samarkand", "type": "direct"},
        ]
    },
    {
        "uzbek_title": "Buxoro",
        "english_title": "Bukhara",
        "domain": "cities",
        "questions": [
            {"uz": "Buxoro qadimiy shahar", "en": "Bukhara ancient city", "type": "keyword"},
            {"uz": "Buxoro", "en": "Bukhara", "type": "direct"},
        ]
    },
    {
        "uzbek_title": "Xorazm",
        "english_title": "Khwarezm",
        "domain": "cities",
        "questions": [
            {"uz": "Xorazm viloyati", "en": "Khwarezm region", "type": "keyword"},
            {"uz": "Xorazm", "en": "Khwarezm", "type": "direct"},
        ]
    },
    {
        "uzbek_title": "Fargʻona",
        "english_title": "Fergana",
        "domain": "cities",
        "questions": [
            {"uz": "Fargʻona vodiysi", "en": "Fergana Valley", "type": "keyword"},
            {"uz": "Fargʻona", "en": "Fergana", "type": "direct"},
        ]
    },
    # LANGUAGES
    {
        "uzbek_title": "Oʻzbek tili",
        "english_title": "Uzbek language",
        "domain": "languages",
        "questions": [
            {"uz": "Oʻzbek tili lotin yozuvi", "en": "Uzbek language Latin script", "type": "keyword"},
            {"uz": "Oʻzbek tili", "en": "Uzbek language", "type": "direct"},
        ]
    },
    {
        "uzbek_title": "Rus tili",
        "english_title": "Russian language",
        "domain": "languages",
        "questions": [
            {"uz": "Rus tili harflari", "en": "Russian alphabet letters", "type": "keyword"},
            {"uz": "Rus tili", "en": "Russian language", "type": "direct"},
        ]
    },
    {
        "uzbek_title": "Ingliz tili",
        "english_title": "English language",
        "domain": "languages",
        "questions": [
            {"uz": "Ingliz tili grammatikasi", "en": "English grammar", "type": "keyword"},
            {"uz": "Ingliz tili", "en": "English language", "type": "direct"},
        ]
    },
    # SCIENCE
    {
        "uzbek_title": "Biologiya",
        "english_title": "Biology",
        "domain": "science",
        "questions": [
            {"uz": "Biologiya fanidan", "en": "Biology science of", "type": "keyword"},
            {"uz": "Biologiya", "en": "Biology", "type": "direct"},
        ]
    },
    {
        "uzbek_title": "Fizika",
        "english_title": "Physics",
        "domain": "science",
        "questions": [
            {"uz": "Fizika asoslari", "en": "Physics fundamentals", "type": "keyword"},
            {"uz": "Fizika", "en": "Physics", "type": "direct"},
        ]
    },
    {
        "uzbek_title": "Astronomiya",
        "english_title": "Astronomy",
        "domain": "science",
        "questions": [
            {"uz": "Astronomiya fanini oʻrganish", "en": "Study of astronomy", "type": "keyword"},
            {"uz": "Astronomiya", "en": "Astronomy", "type": "direct"},
        ]
    },
    {
        "uzbek_title": "Koinot",
        "english_title": "Universe",
        "domain": "science",
        "questions": [
            {"uz": "Koinot yoshi", "en": "Age of the universe", "type": "factual"},
            {"uz": "Koinot", "en": "Universe", "type": "direct"},
        ]
    },
    {
        "uzbek_title": "Quyosh",
        "english_title": "Sun",
        "domain": "science",
        "questions": [
            {"uz": "Quyosh tarkibi", "en": "Composition of the Sun", "type": "keyword"},
            {"uz": "Quyosh", "en": "Sun", "type": "direct"},
        ]
    },
    # TECHNOLOGY
    {
        "uzbek_title": "Internet",
        "english_title": "Internet",
        "domain": "technology",
        "questions": [
            {"uz": "Internet tarixi", "en": "History of the Internet", "type": "keyword"},
            {"uz": "Internet", "en": "Internet", "type": "direct"},
        ]
    },
    {
        "uzbek_title": "Google",
        "english_title": "Google",
        "domain": "technology",
        "questions": [
            {"uz": "Google qidiruv tizimi", "en": "Google search engine", "type": "keyword"},
            {"uz": "Google", "en": "Google", "type": "direct"},
        ]
    },
    {
        "uzbek_title": "Linux",
        "english_title": "Linux",
        "domain": "technology",
        "questions": [
            {"uz": "Linux operatsion tizim", "en": "Linux operating system", "type": "keyword"},
            {"uz": "Linux", "en": "Linux", "type": "direct"},
        ]
    },
    {
        "uzbek_title": "Kompyuter",
        "english_title": "Computer",
        "domain": "technology",
        "questions": [
            {"uz": "Kompyuter qismlari", "en": "Computer parts", "type": "keyword"},
            {"uz": "Kompyuter", "en": "Computer", "type": "direct"},
        ]
    },
    # CULTURE/HISTORY
    {
        "uzbek_title": "Alisher Navoiy",
        "english_title": "Alisher Navoi",
        "domain": "culture",
        "questions": [
            {"uz": "Alisher Navoiy asarlari", "en": "Works of Alisher Navoi", "type": "keyword"},
            {"uz": "Alisher Navoiy", "en": "Alisher Navoi", "type": "direct"},
        ]
    },
    {
        "uzbek_title": "Bobur",
        "english_title": "Babur",
        "domain": "culture",
        "questions": [
            {"uz": "Bobur nomi", "en": "Babur name", "type": "keyword"},
            {"uz": "Bobur", "en": "Babur", "type": "direct"},
        ]
    },
    {
        "uzbek_title": "Buyuk Ipak yoʻli",
        "english_title": "Silk Road",
        "domain": "culture",
        "questions": [
            {"uz": "Ipak yoʻli tarixi", "en": "Silk Road history", "type": "keyword"},
            {"uz": "Buyuk Ipak yoʻli", "en": "Silk Road", "type": "direct"},
        ]
    },
    # ORGANIZATIONS
    {
        "uzbek_title": "Birlashgan Millatlar Tashkiloti",
        "english_title": "United Nations",
        "domain": "organizations",
        "questions": [
            {"uz": "BMT aʼzo davlatlari", "en": "UN member states", "type": "keyword"},
            {"uz": "Birlashgan Millatlar Tashkiloti", "en": "United Nations", "type": "direct"},
        ]
    },
    {
        "uzbek_title": "Vikipediya",
        "english_title": "Wikipedia",
        "domain": "organizations",
        "questions": [
            {"uz": "Vikipediya maqolalari", "en": "Wikipedia articles", "type": "keyword"},
            {"uz": "Vikipediya", "en": "Wikipedia", "type": "direct"},
        ]
    },
    # ADDITIONAL
    {
        "uzbek_title": "Nobel mukofoti",
        "english_title": "Nobel Prize",
        "domain": "other",
        "questions": [
            {"uz": "Nobel mukofoti sovrindorlari", "en": "Nobel Prize winners", "type": "keyword"},
            {"uz": "Nobel mukofoti", "en": "Nobel Prize", "type": "direct"},
        ]
    },
]

# Generate test cases
test_cases = []
test_id = 0

for topic in topics:
    for q in topic["questions"]:
        # Uzbek query -> Uzbek corpus (baseline)
        test_cases.append({
            "id": f"xl_uz_baseline_{test_id}",
            "query_language": "uz",
            "corpus_language": "uz",
            "question": q["uz"],
            "target_title": topic["uzbek_title"],
            "domain": topic["domain"],
            "question_type": q["type"],
        })
        
        # English query -> English corpus (baseline)
        test_cases.append({
            "id": f"xl_en_baseline_{test_id}",
            "query_language": "en",
            "corpus_language": "en",
            "question": q["en"],
            "target_title": topic["english_title"],
            "domain": topic["domain"],
            "question_type": q["type"],
        })
        
        # Uzbek query -> English corpus (cross-lingual)
        test_cases.append({
            "id": f"xl_uz_on_en_{test_id}",
            "query_language": "uz",
            "corpus_language": "en",
            "question": q["uz"],
            "target_title": topic["english_title"],
            "domain": topic["domain"],
            "question_type": q["type"],
        })
        
        # English query -> Uzbek corpus (cross-lingual)
        test_cases.append({
            "id": f"xl_en_on_uz_{test_id}",
            "query_language": "en",
            "corpus_language": "uz",
            "question": q["en"],
            "target_title": topic["uzbek_title"],
            "domain": topic["domain"],
            "question_type": q["type"],
        })
        
        test_id += 1

# Write test cases
output_path = Path("/home/u6ef/rajantripathi.u6ef/soas_rag_eval/data/eval/cross_lingual_robust_test.jsonl")
with open(output_path, "w") as f:
    for case in test_cases:
        f.write(json.dumps(case, ensure_ascii=False) + "\n")

# Summary
by_domain = {}
for case in test_cases:
    d = case["domain"]
    if d not in by_domain:
        by_domain[d] = 0
    by_domain[d] += 1

print("=== ROBUST CROSS-LINGUAL EVALUATION DESIGN ===")
print(f"\nTotal test cases: {len(test_cases)}")
print(f"Topics: {len(topics)}")
print(f"\nBreakdown by condition:")
print(f"  Uzbek -> Uzbek (baseline): {len([c for c in test_ids if c.startswith(xl_uz_baseline)])}")
print(f"  English -> English (baseline): {len([c for c in test_cases if c[id].startswith(xl_en_baseline)])}")
print(f"  Uzbek -> English (cross-lingual): {len([c for c in test_cases if c[id].startswith(xl_uz_on_en)])}")
print(f"  English -> Uzbek (cross-lingual): {len([c for c in test_cases if c[id].startswith(xl_en_on_uz)])}")
print(f"\nBy domain:")
for d, count in sorted(by_domain.items(), key=lambda x: -x[1]):
    print(f"  {d}: {count}")
print(f"\nBy question type:")
by_type = {}
for case in test_cases:
    t = case["question_type"]
    if t not in by_type:
        by_type[t] = 0
    by_type[t] += 1
for t, count in sorted(by_type.items(), key=lambda x: -x[1]):
    print(f"  {t}: {count}")
print(f"\nSaved to: {output_path}")
