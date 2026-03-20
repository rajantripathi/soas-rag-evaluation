#!/usr/bin/env python3
"""
Build semantic boundary test set.

Tests hypothesis: Multilingual embeddings capture conceptual equivalence 
across cultures but struggle with technical terminology.

Design: 10 domains × 10 topics × 3 question types × 2 directions = 600 test cases
"""

import json
from pathlib import Path

# Domain definitions with topics
test_spec = {
    # CULTURAL-CONCEPTUAL DOMAINS
    "geography": {
        "type": "cultural",
        "topics": [
            {"uz": "Oʻzbekiston", "en": "Uzbekistan", "qs": [
                {"uz": "Oʻzbekiston poytaxti qayer?", "en": "What is the capital of Uzbekistan?", "t": "factual"},
                {"uz": "Oʻzbekiston", "en": "Uzbekistan", "t": "direct"},
                {"uz": "Oʻzbekiston hududi", "en": "Uzbekistan territory area", "t": "keyword"},
            ]},
            {"uz": "Rossiya", "en": "Russia", "qs": [
                {"uz": "Rossiya maydoni", "en": "Russia area size", "t": "keyword"},
                {"uz": "Rossiya", "en": "Russia", "t": "direct"},
                {"uz": "Rossiya qaerda?", "en": "Where is Russia located?", "t": "factual"},
            ]},
            {"uz": "Qozogʻiston", "en": "Kazakhstan", "qs": [
                {"uz": "Qozogʻiston poytaxti", "en": "Kazakhstan capital", "t": "keyword"},
                {"uz": "Qozogʻiston", "en": "Kazakhstan", "t": "direct"},
                {"uz": "Qozogʻiston Oʻzbekiston bilan chegaradoshmi?", "en": "Is Kazakhstan bordering Uzbekistan?", "t": "factual"},
            ]},
            {"uz": "Turkiya", "en": "Turkey", "qs": [
                {"uz": "Turkiya qaysi qitʼada?", "en": "Which continent is Turkey in?", "t": "factual"},
                {"uz": "Turkiya", "en": "Turkey", "t": "direct"},
                {"uz": "Turkiya aholisi", "en": "Turkey population", "t": "keyword"},
            ]},
            {"uz": "Xitoy", "en": "China", "qs": [
                {"uz": "Xitoy aholisi soni", "en": "China population number", "t": "keyword"},
                {"uz": "Xitoy", "en": "China", "t": "direct"},
                {"uz": "Xitoy poytaxti", "en": "China capital city", "t": "keyword"},
            ]},
            {"uz": "Hindiston", "en": "India", "qs": [
                {"uz": "Hindiston qitʼasi", "en": "India continent", "t": "keyword"},
                {"uz": "Hindiston", "en": "India", "t": "direct"},
                {"uz": "Hindiston poytaxti", "en": "India capital", "t": "keyword"},
            ]},
            {"uz": "Yevropa", "en": "Europe", "qs": [
                {"uz": "Yevropa davlatlari soni", "en": "Number of European countries", "t": "keyword"},
                {"uz": "Yevropa", "en": "Europe", "t": "direct"},
                {"uz": "Yevropa maydoni", "en": "Europe area", "t": "keyword"},
            ]},
            {"uz": "Osiyo", "en": "Asia", "qs": [
                {"uz": "Osiyo davlatlari", "en": "Asian countries list", "t": "keyword"},
                {"uz": "Osiyo", "en": "Asia", "t": "direct"},
                {"uz": "Osiyo qitʼasi maydoni", "en": "Asia continent area", "t": "keyword"},
            ]},
            {"uz": "Markaziy Osiyo", "en": "Central Asia", "qs": [
                {"uz": "Markaziy Osiyo davlatlari roʻyxati", "en": "Central Asia countries list", "t": "keyword"},
                {"uz": "Markaziy Osiyo", "en": "Central Asia", "t": "direct"},
                {"uz": "Markaziy Osiyo qaerda?", "en": "Where is Central Asia?", "t": "factual"},
            ]},
            {"uz": "Kavkaz", "en": "Caucasus", "qs": [
                {"uz": "Kavkaz davlatlari", "en": "Caucasus countries", "t": "keyword"},
                {"uz": "Kavkaz", "en": "Caucasus", "t": "direct"},
                {"uz": "Kavkaz togʻlari", "en": "Caucasus mountains", "t": "keyword"},
            ]},
        ]
    },
    
    "cities": {
        "type": "cultural",
        "topics": [
            {"uz": "Toshkent", "en": "Tashkent", "qs": [
                {"uz": "Toshkent aholisi", "en": "Tashkent population", "t": "keyword"},
                {"uz": "Toshkent", "en": "Tashkent", "t": "direct"},
                {"uz": "Toshkentqa qachon asos solingan?", "en": "When was Tashkent founded?", "t": "factual"},
            ]},
            {"uz": "Samarqand", "en": "Samarkand", "qs": [
                {"uz": "Samarqand tarixi", "en": "Samarkand history", "t": "keyword"},
                {"uz": "Samarqand", "en": "Samarkand", "t": "direct"},
                {"uz": "Samarqand qachon tashkil topgan?", "en": "When was Samarkand established?", "t": "factual"},
            ]},
            {"uz": "Buxoro", "en": "Bukhara", "qs": [
                {"uz": "Buxoro eski shahar", "en": "Bukhara old city", "t": "keyword"},
                {"uz": "Buxoro", "en": "Bukhara", "t": "direct"},
                {"uz": "Buxoro yodgorliklari", "en": "Bukhara monuments", "t": "keyword"},
            ]},
            {"uz": "Xiva", "en": "Khiva", "qs": [
                {"uz": "Xiva Ichan qalʼa", "en": "Khiva Ichan Kala", "t": "keyword"},
                {"uz": "Xiva", "en": "Khiva", "t": "direct"},
                {"uz": "Xiva tarixiy yodgorliklari", "en": "Khiva historical monuments", "t": "keyword"},
            ]},
            {"uz": "Qoʻqon", "en": "Kokand", "qs": [
                {"uz": "Qoʻqon xonligi", "en": "Kokand Khanate", "t": "keyword"},
                {"uz": "Qoʻqon", "en": "Kokand", "t": "direct"},
                {"uz": "Qoʻqon poytaxti boʻlganmi?", "en": "Was Kokand a capital?", "t": "factual"},
            ]},
            {"uz": "Namangan", "en": "Namangan", "qs": [
                {"uz": "Namangan viloyati", "en": "Namangan region", "t": "keyword"},
                {"uz": "Namangan", "en": "Namangan", "t": "direct"},
                {"uz": "Namangan aholisi", "en": "Namangan population", "t": "keyword"},
            ]},
            {"uz": "Fargʻona", "en": "Fergana", "qs": [
                {"uz": "Fargʻona vodiysi", "en": "Fergana Valley", "t": "keyword"},
                {"uz": "Fargʻona", "en": "Fergana", "t": "direct"},
                {"uz": "Fargʻona shahrining tarixi", "en": "Fergana city history", "t": "keyword"},
            ]},
            {"uz": "Andijon", "en": "Andijan", "qs": [
                {"uz": "Andijon viloyati", "en": "Andijan region", "t": "keyword"},
                {"uz": "Andijon", "en": "Andijan", "t": "direct"},
                {"uz": "Andijon zilzilasi", "en": "Andijan earthquake", "t": "keyword"},
            ]},
            {"uz": "Termiz", "en": "Termez", "qs": [
                {"uz": "Termiz shahri", "en": "Termez city", "t": "keyword"},
                {"uz": "Termiz", "en": "Termez", "t": "direct"},
                {"uz": "Termiz tarixi", "en": "Termez history", "t": "keyword"},
            ]},
            {"uz": "Nukus", "en": "Nukus", "qs": [
                {"uz": "Nukus shahri", "en": "Nukus city", "t": "keyword"},
                {"uz": "Nukus", "en": "Nukus", "t": "direct"},
                {"uz": "Nukus Qoraqalpogʻiston poytaxti", "en": "Nukus Karakalpakstan capital", "t": "keyword"},
            ]},
        ]
    },
    
    "culture": {
        "type": "cultural",
        "topics": [
            {"uz": "Alisher Navoiy", "en": "Alisher Navoi", "qs": [
                {"uz": "Alisher Navoiy asarlari", "en": "Alisher Navoi works", "t": "keyword"},
                {"uz": "Alisher Navoiy", "en": "Alisher Navoi", "t": "direct"},
                {"uz": "Alisher Navoiy qachon yashagan?", "en": "When did Alisher Navoi live?", "t": "factual"},
            ]},
            {"uz": "Bobur", "en": "Babur", "qs": [
                {"uz": "Bobur zafarnomasi", "en": "Baburnama Babur memoir", "t": "keyword"},
                {"uz": "Bobur", "en": "Babur", "t": "direct"},
                {"uz": "Bobur imperiyasi", "en": "Babur Empire Mughal", "t": "keyword"},
            ]},
            {"uz": "Mirzo Ulugʻbek", "en": "Ulugh Beg", "qs": [
                {"uz": "Mirzo Ulugʻbek rasadxonasi", "en": "Ulugh Beg observatory", "t": "keyword"},
                {"uz": "Mirzo Ulugʻbek", "en": "Ulugh Beg", "t": "direct"},
                {"uz": "Mirzo Ulugʻbek astronom", "en": "Ulugh Beg astronomer", "t": "keyword"},
            ]},
            {"uz": "Amir Temur", "en": "Timur", "qs": [
                {"uz": "Amir Temur imperiyasi", "en": "Timur Empire", "t": "keyword"},
                {"uz": "Amir Temur", "en": "Timur", "t": "direct"},
                {"uz": "Amir Temur qabrining qayerda?", "en": "Where is Timur buried?", "t": "factual"},
            ]},
            {"uz": "Buyuk Ipak yoʻli", "en": "Silk Road", "qs": [
                {"uz": "Buyuk Ipak yoʻli tarixi", "en": "Silk Road history", "t": "keyword"},
                {"uz": "Buyuk Ipak yoʻli", "en": "Silk Road", "t": "direct"},
                {"uz": "Ipak yoʻli shaharlari", "en": "Silk Road cities", "t": "keyword"},
            ]},
            {"uz": "Oʻzbek taomlari", "en": "Uzbek cuisine", "qs": [
                {"uz": "Oʻzbek milliy taomlari", "en": "Uzbek national dishes", "t": "keyword"},
                {"uz": "Oʻzbek taomlari", "en": "Uzbek cuisine", "t": "direct"},
                {"uz": "Oʻzbek palovining turlari", "en": "Types of Uzbek pilaf", "t": "keyword"},
            ]},
            {"uz": "Oʻzbek musiqa", "en": "Uzbek music", "qs": [
                {"uz": "Oʻzbek xalq musiqa asboblari", "en": "Uzbek folk instruments", "t": "keyword"},
                {"uz": "Oʻzbek musiqa", "en": "Uzbek music", "t": "direct"},
                {"uz": "Oʻzbek shashmaqomi", "en": "Uzbek Shashmaqom", "t": "keyword"},
            ]},
            {"uz": "Oʻzbek kiyimlari", "en": "Uzbek clothing", "qs": [
                {"uz": "Oʻzbek milliy kiyimlari", "en": "Uzbek national clothing", "t": "keyword"},
                {"uz": "Oʻzbek kiyimlari", "en": "Uzbek clothing", "t": "direct"},
                {"uz": "Oʻzbek atlasi va adrasi", "en": "Uzbek atlas and adras", "t": "keyword"},
            ]},
            {"uz": "Oʻzbek bayramlari", "en": "Uzbek holidays", "qs": [
                {"uz": "Oʻzbekiston mustaqillik kuni", "en": "Uzbekistan Independence Day", "t": "keyword"},
                {"uz": "Oʻzbek bayramlari", "en": "Uzbek holidays", "t": "direct"},
                {"uz": "Oʻzbekiston navroʻzi", "en": "Uzbek Navruz", "t": "keyword"},
            ]},
            {"uz": "Oʻzbek meʼmorchiligi", "en": "Uzbek architecture", "qs": [
                {"uz": "Oʻzbek meʼmorchiligi uslublari", "en": "Uzbek architecture styles", "t": "keyword"},
                {"uz": "Oʻzbek meʼmorchiligi", "en": "Uzbek architecture", "t": "direct"},
                {"uz": "Oʻzbek madrasalari", "en": "Uzbek madrasas", "t": "keyword"},
            ]},
        ]
    },
    
    "orgs": {
        "type": "cultural",
        "topics": [
            {"uz": "Birlashgan Millatlar Tashkiloti", "en": "United Nations", "qs": [
                {"uz": "BMT aʼzo davlatlari", "en": "UN member states", "t": "keyword"},
                {"uz": "Birlashgan Millatlar Tashkiloti", "en": "United Nations", "t": "direct"},
                {"uz": "BMT qachon tashkil topgan?", "en": "When was UN founded?", "t": "factual"},
            ]},
            {"uz": "YUNESKO", "en": "UNESCO", "qs": [
                {"uz": "YUNESKO vazifalari", "en": "UNESCO functions", "t": "keyword"},
                {"uz": "YUNESKO", "en": "UNESCO", "t": "direct"},
                {"uz": "YUNESKO Oʻzbekiston obidalari", "en": "UNESCO Uzbek sites", "t": "keyword"},
            ]},
            {"uz": "Vikipediya", "en": "Wikipedia", "qs": [
                {"uz": "Vikipediya maqolalari soni", "en": "Wikipedia articles count", "t": "keyword"},
                {"uz": "Vikipediya", "en": "Wikipedia", "t": "direct"},
                {"uz": "Vikipediya kim tomonidan yaratilgan?", "en": "Who created Wikipedia?", "t": "factual"},
            ]},
            {"uz": "Google", "en": "Google", "qs": [
                {"uz": "Google qidiruv tizimi", "en": "Google search engine", "t": "keyword"},
                {"uz": "Google", "en": "Google", "t": "direct"},
                {"uz": "Google kompaniyasi asoschilari", "en": "Google company founders", "t": "keyword"},
            ]},
            {"uz": "Oʻzbekiston Milliy universiteti", "en": "National University of Uzbekistan", "qs": [
                {"uz": "Oʻzbekiston Milliy universiteti tarixi", "en": "National University of Uzbekistan history", "t": "keyword"},
                {"uz": "Oʻzbekiston Milliy universiteti", "en": "National University of Uzbekistan", "t": "direct"},
                {"uz": "OʻzMU Toshkentda joylashganmi?", "en": "Is NUUz in Tashkent?", "t": "factual"},
            ]},
            {"uz": "Oʻzbekiston futbol federatsiyasi", "en": "Uzbekistan Football Association", "qs": [
                {"uz": "Oʻzbekiston futbol terma jamoasi", "en": "Uzbekistan national football team", "t": "keyword"},
                {"uz": "Oʻzbekiston futbol federatsiyasi", "en": "Uzbekistan Football Association", "t": "direct"},
                {"uz": "Oʻzbekiston futbol ligasi tizimi", "en": "Uzbekistan football league system", "t": "keyword"},
            ]},
            {"uz": "Xalqaro Qizil Xoch Xayriya Jamiyati", "en": "International Red Cross", "qs": [
                {"uz": "Qizil Xoch tashkiloti vazifalari", "en": "Red Cross organization functions", "t": "keyword"},
                {"uz": "Xalqaro Qizil Xoch Xayriya Jamiyati", "en": "International Red Cross", "t": "direct"},
                {"uz": "Qizil Xoch qachon tashkil topgan?", "en": "When was Red Cross founded?", "t": "factual"},
            ]},
            {"uz": "Jahon Sogʻliqni Saqlash Tashkiloti", "en": "World Health Organization", "qs": [
                {"uz": "JSST shtab-kvartirasi", "en": "WHO headquarters", "t": "keyword"},
                {"uz": "Jahon Sogʻliqni Saqlash Tashkiloti", "en": "World Health Organization", "t": "direct"},
                {"uz": "JSST asosiy vazifalari", "en": "WHO main functions", "t": "keyword"},
            ]},
            {"uz": "Yevropa Ittifoqi", "en": "European Union", "qs": [
                {"uz": "Yevropa Ittifoqi aʼzo mamlakatlari", "en": "European Union member countries", "t": "keyword"},
                {"uz": "Yevropa Ittifoqi", "en": "European Union", "t": "direct"},
                {"uz": "Yevropa Ittifoqi qachon tashkil topgan?", "en": "When was EU founded?", "t": "factual"},
            ]},
            {"uz": "NATO", "en": "NATO", "qs": [
                {"uz": "NATO aʼzo davlatlari", "en": "NATO member states", "t": "keyword"},
                {"uz": "NATO", "en": "NATO", "t": "direct"},
                {"uz": "NATO tashkil topgan yili", "en": "NATO founding year", "t": "keyword"},
            ]},
        ]
    },
    
    # TECHNICAL-SCIENTIFIC DOMAINS
    "physics": {
        "type": "technical",
        "topics": [
            {"uz": "Newton qonunlari", "en": "Newton laws of motion", "qs": [
                {"uz": "Nyuton harakat qonunlari", "en": "Newton laws of motion", "t": "keyword"},
                {"uz": "Newton qonunlari", "en": "Newton laws", "t": "direct"},
                {"uz": "Birinchi Nyuton qonuni nima?", "en": "What is Newton first law?", "t": "factual"},
            ]},
            {"uz": "Energiya", "en": "Energy", "qs": [
                {"uz": "Energiya turini saqlash qonuni", "en": "Energy conservation law", "t": "keyword"},
                {"uz": "Energiya", "en": "Energy", "t": "direct"},
                {"uz": "Kinetik energiya nima?", "en": "What is kinetic energy?", "t": "factual"},
            ]},
            {"uz": "Elektr tok", "en": "Electric current", "qs": [
                {"uz": "Elektr tok kuchi", "en": "Electric current strength", "t": "keyword"},
                {"uz": "Elektr tok", "en": "Electric current", "t": "direct"},
                {"uz": "Elektr tok oʻlchov birligi", "en": "Electric current unit", "t": "keyword"},
            ]},
            {"uz": "Magnit maydon", "en": "Magnetic field", "qs": [
                {"uz": "Magnit maydon chiziqlari", "en": "Magnetic field lines", "t": "keyword"},
                {"uz": "Magnit maydon", "en": "Magnetic field", "t": "direct"},
                {"uz": "Magnit maydon kuchlanganligi", "en": "Magnetic field strength", "t": "keyword"},
            ]},
            {"uz": "Yorugʻlik tezligi", "en": "Speed of light", "qs": [
                {"uz": "Yorugʻlik tezligi son qiymati", "en": "Speed of light numerical value", "t": "keyword"},
                {"uz": "Yorugʻlik tezligi", "en": "Speed of light", "t": "direct"},
                {"uz": "Yorugʻlik tezligi sekundda necha kilometr?", "en": "Speed of light km per second?", "t": "factual"},
            ]},
            {"uz": "Atom tuzilishi", "en": "Atomic structure", "qs": [
                {"uz": "Atom yadrosi tuzilishi", "en": "Atomic nucleus structure", "t": "keyword"},
                {"uz": "Atom tuzilishi", "en": "Atomic structure", "t": "direct"},
                {"uz": "Atom elektronlari soni", "en": "Atomic electrons number", "t": "keyword"},
            ]},
            {"uz": "Termodinamika", "en": "Thermodynamics", "qs": [
                {"uz": "Termodinamika qonunlari", "en": "Thermodynamics laws", "t": "keyword"},
                {"uz": "Termodinamika", "en": "Thermodynamics", "t": "direct"},
                {"uz": "Termodinamika birinchi qonuni", "en": "Thermodynamics first law", "t": "keyword"},
            ]},
            {"uz": "Toʻlqin fizikasi", "en": "Wave physics", "qs": [
                {"uz": "Toʻlqin uzunligi", "en": "Wavelength", "t": "keyword"},
                {"uz": "Toʻlqin fizikasi", "en": "Wave physics", "t": "direct"},
                {"uz": "Toʻlqin chastotasi", "en": "Wave frequency", "t": "keyword"},
            ]},
            {"uz": "Kvant mexanikasi", "en": "Quantum mechanics", "qs": [
                {"uz": "Kvant mexanikasi asoslari", "en": "Quantum mechanics fundamentals", "t": "keyword"},
                {"uz": "Kvant mexanikasi", "en": "Quantum mechanics", "t": "direct"},
                {"uz": "Kvant fizikasi tarixi", "en": "Quantum physics history", "t": "keyword"},
            ]},
            {"uz": "Nisbiylik nazariyasi", "en": "Relativity theory", "qs": [
                {"uz": "Eynstein nisbiylik nazariyasi", "en": "Einstein relativity theory", "t": "keyword"},
                {"uz": "Nisbiylik nazariyasi", "en": "Relativity theory", "t": "direct"},
                {"uz": "Maxsus nisbiylik nazariyasi", "en": "Special relativity theory", "t": "keyword"},
            ]},
        ]
    },
    
    "chemistry": {
        "type": "technical",
        "topics": [
            {"uz": "Kimyoviy elementlar", "en": "Chemical elements", "qs": [
                {"uz": "Kimyoviy elementlar davriy jadvali", "en": "Periodic table elements", "t": "keyword"},
                {"uz": "Kimyoviy elementlar", "en": "Chemical elements", "t": "direct"},
                {"uz": "Elementlar soni qancha?", "en": "How many elements exist?", "t": "factual"},
            ]},
            {"uz": "Suv formulasi", "en": "Water formula", "qs": [
                {"uz": "Suv kimyoviy formulasi", "en": "Water chemical formula", "t": "keyword"},
                {"uz": "Suv formulasi", "en": "Water formula", "t": "direct"},
                {"uz": "H2O molekula tuzilishi", "en": "H2O molecule structure", "t": "keyword"},
            ]},
            {"uz": "Kislota", "en": "Acid", "qs": [
                {"uz": "Kislota asosiy xossalari", "en": "Acid main properties", "t": "keyword"},
                {"uz": "Kislota", "en": "Acid", "t": "direct"},
                {"uz": "Kislota pH qiymati", "en": "Acid pH value", "t": "keyword"},
            ]},
            {"uz": "Asos", "en": "Base", "qs": [
                {"uz": "Asos moddalar xossalari", "en": "Base substances properties", "t": "keyword"},
                {"uz": "Asos", "en": "Base", "t": "direct"},
                {"uz": "Asoslar pH qiymati", "en": "Bases pH value", "t": "keyword"},
            ]},
            {"uz": "Kimyoviy reaksiya", "en": "Chemical reaction", "qs": [
                {"uz": "Kimyoviy reaksiya turlari", "en": "Types of chemical reactions", "t": "keyword"},
                {"uz": "Kimyoviy reaksiya", "en": "Chemical reaction", "t": "direct"},
                {"uz": "Oksidlanish-qaytarilish reaksiyasi", "en": "Redox reaction", "t": "keyword"},
            ]},
            {"uz": "Atom massasi", "en": "Atomic mass", "qs": [
                {"uz": "Atom massasi birligi", "en": "Atomic mass unit", "t": "keyword"},
                {"uz": "Atom massasi", "en": "Atomic mass", "t": "direct"},
                {"uz": "Molekula massasi hisoblash", "en": "Calculate molecular mass", "t": "keyword"},
            ]},
            {"uz": "Valentlik", "en": "Valence", "qs": [
                {"uz": "Valentlik qanday aniqlanadi?", "en": "How is valence determined?", "t": "factual"},
                {"uz": "Valentlik", "en": "Valence", "t": "direct"},
                {"uz": "Kimyoviy valentlik", "en": "Chemical valence", "t": "keyword"},
            ]},
            {"uz": "Erigma", "en": "Solution", "qs": [
                {"uz": "Erigma kontsentratsiyasi", "en": "Solution concentration", "t": "keyword"},
                {"uz": "Erigma", "en": "Solution", "t": "direct"},
                {"uz": "Suvda erigan moddalar", "en": "Substances dissolved in water", "t": "keyword"},
            ]},
            {"uz": "Organik kimyo", "en": "Organic chemistry", "qs": [
                {"uz": "Organik kimyo asoslari", "en": "Organic chemistry basics", "t": "keyword"},
                {"uz": "Organik kimyo", "en": "Organic chemistry", "t": "direct"},
                {"uz": "Uglevodorodlar", "en": "Hydrocarbons", "t": "keyword"},
            ]},
            {"uz": "Kimyoviy bogʻlanish", "en": "Chemical bond", "qs": [
                {"uz": "Kimyoviy bogʻlanish turlari", "en": "Types of chemical bonds", "t": "keyword"},
                {"uz": "Kimyoviy bogʻlanish", "en": "Chemical bond", "t": "direct"},
                {"uz": "Kovalent bogʻlanish", "en": "Covalent bond", "t": "keyword"},
            ]},
        ]
    },
    
    "biology": {
        "type": "technical",
        "topics": [
            {"uz": "Hujayra", "en": "Cell", "qs": [
                {"uz": "Hujayra tuzilishi", "en": "Cell structure", "t": "keyword"},
                {"uz": "Hujayra", "en": "Cell", "t": "direct"},
                {"uz": "Hujayra organellari", "en": "Cell organelles", "t": "keyword"},
            ]},
            {"uz": "DNK", "en": "DNA", "qs": [
                {"uz": "DNK tuzilishi", "en": "DNA structure", "t": "keyword"},
                {"uz": "DNK", "en": "DNA", "t": "direct"},
                {"uz": "DNK ikki spiral", "en": "DNA double helix", "t": "keyword"},
            ]},
            {"uz": "Genetika", "en": "Genetics", "qs": [
                {"uz": "Genetika asoslari", "en": "Genetics basics", "t": "keyword"},
                {"uz": "Genetika", "en": "Genetics", "t": "direct"},
                {"uz": "Gen nima?", "en": "What is a gene?", "t": "factual"},
            ]},
            {"uz": "Fotosintez", "en": "Photosynthesis", "qs": [
                {"uz": "Fotosintez jarayoni", "en": "Photosynthesis process", "t": "keyword"},
                {"uz": "Fotosintez", "en": "Photosynthesis", "t": "direct"},
                {"uz": "Fotosintez tenglamasi", "en": "Photosynthesis equation", "t": "keyword"},
            ]},
            {"uz": "Nafas olish", "en": "Respiration", "qs": [
                {"uz": "Nafas olish jarayoni", "en": "Respiration process", "t": "keyword"},
                {"uz": "Nafas olish", "en": "Respiration", "t": "direct"},
                {"uz": "Hujayrali nafas olish", "en": "Cellular respiration", "t": "keyword"},
            ]},
            {"uz": "Oʻsimliklar", "en": "Plants", "qs": [
                {"uz": "Oʻsimliklar turlari", "en": "Types of plants", "t": "keyword"},
                {"uz": "Oʻsimliklar", "en": "Plants", "t": "direct"},
                {"uz": "Gulli oʻsimliklar", "en": "Flowering plants", "t": "keyword"},
            ]},
            {"uz": "Hayvonlar", "en": "Animals", "qs": [
                {"uz": "Hayvonlar dunyosi", "en": "Animal kingdom", "t": "keyword"},
                {"uz": "Hayvonlar", "en": "Animals", "t": "direct"},
                {"uz": "Umurtqali hayvonlar", "en": "Vertebrate animals", "t": "keyword"},
            ]},
            {"uz": "Evolyutsiya", "en": "Evolution", "qs": [
                {"uz": "Evolyutsiya nazariyasi", "en": "Evolution theory", "t": "keyword"},
                {"uz": "Evolyutsiya", "en": "Evolution", "t": "direct"},
                {"uz": "Tabiiy tanlash", "en": "Natural selection", "t": "keyword"},
            ]},
            {"uz": "Ekologiya", "en": "Ecology", "qs": [
                {"uz": "Ekologiya fanining oʻrganish obyekti", "en": "Ecology study object", "t": "keyword"},
                {"uz": "Ekologiya", "en": "Ecology", "t": "direct"},
                {"uz": "Ekosistema tarkibi", "en": "Ecosystem components", "t": "keyword"},
            ]},
            {"uz": "Viruslar", "en": "Viruses", "qs": [
                {"uz": "Viruslar tuzilishi", "en": "Virus structure", "t": "keyword"},
                {"uz": "Viruslar", "en": "Viruses", "t": "direct"},
                {"uz": "Viruslar koʻpayishi", "en": "Virus reproduction", "t": "keyword"},
            ]},
        ]
    },
    
    "medicine": {
        "type": "technical",
        "topics": [
            {"uz": "Yurak kasalliklari", "en": "Heart diseases", "qs": [
                {"uz": "Yurak yetishmovchiligi", "en": "Heart failure", "t": "keyword"},
                {"uz": "Yurak kasalliklari", "en": "Heart diseases", "t": "direct"},
                {"uz": "Yurak urishi tezligi", "en": "Heart rate", "t": "keyword"},
            ]},
            {"uz": "Qandli diabet", "en": "Diabetes", "qs": [
                {"uz": "Qandli diabet turlari", "en": "Types of diabetes", "t": "keyword"},
                {"uz": "Qandli diabet", "en": "Diabetes", "t": "direct"},
                {"uz": "Insulin qanday ishlaydi?", "en": "How does insulin work?", "t": "factual"},
            ]},
            {"uz": "Vaksina", "en": "Vaccine", "qs": [
                {"uz": "Vaksina turlari", "en": "Types of vaccines", "t": "keyword"},
                {"uz": "Vaksina", "en": "Vaccine", "t": "direct"},
                {"uz": "Vaksina qanday ishlaydi?", "en": "How do vaccines work?", "t": "factual"},
            ]},
            {"uz": "Antibiotik", "en": "Antibiotic", "qs": [
                {"uz": "Antibiotiklar turlari", "en": "Types of antibiotics", "t": "keyword"},
                {"uz": "Antibiotik", "en": "Antibiotic", "t": "direct"},
                {"uz": "Antibiotiklar taʼsiri", "en": "Antibiotics effects", "t": "keyword"},
            ]},
            {"uz": "Xirurgiya", "en": "Surgery", "qs": [
                {"uz": "Xirurgiya turlari", "en": "Types of surgery", "t": "keyword"},
                {"uz": "Xirurgiya", "en": "Surgery", "t": "direct"},
                {"uz": "Laparoskopik xirurgiya", "en": "Laparoscopic surgery", "t": "keyword"},
            ]},
            {"uz": "Nevrologiya", "en": "Neurology", "qs": [
                {"uz": "Nevrologik kasalliklar", "en": "Neurological diseases", "t": "keyword"},
                {"uz": "Nevrologiya", "en": "Neurology", "t": "direct"},
                {"uz": "Miya faoliyati", "en": "Brain function", "t": "keyword"},
            ]},
            {"uz": "Onkologiya", "en": "Oncology", "qs": [
                {"uz": "Saraton kasalligi", "en": "Cancer disease", "t": "keyword"},
                {"uz": "Onkologiya", "en": "Oncology", "t": "direct"},
                {"uz": "Oʻsmalar turlari", "en": "Types of tumors", "t": "keyword"},
            ]},
            {"uz": "Pulmonologiya", "en": "Pulmonology", "qs": [
                {"uz": "Oʻpka kasalliklari", "en": "Lung diseases", "t": "keyword"},
                {"uz": "Pulmonologiya", "en": "Pulmonology", "t": "direct"},
                {"uz": "Bronxial astma", "en": "Bronchial asthma", "t": "keyword"},
            ]},
            {"uz": "Gematologiya", "en": "Hematology", "qs": [
                {"uz": "Qon kasalliklari", "en": "Blood diseases", "t": "keyword"},
                {"uz": "Gematologiya", "en": "Hematology", "t": "direct"},
                {"uz": "Qon tarkibi", "en": "Blood composition", "t": "keyword"},
            ]},
            {"uz": "Terapiya", "en": "Therapy", "qs": [
                {"uz": "Davolash usullari", "en": "Treatment methods", "t": "keyword"},
                {"uz": "Terapiya", "en": "Therapy", "t": "direct"},
                {"uz": "Fizioterapiya", "en": "Physiotherapy", "t": "keyword"},
            ]},
        ]
    },
    
    "computing": {
        "type": "technical",
        "topics": [
            {"uz": "Algoritm", "en": "Algorithm", "qs": [
                {"uz": "Algoritm turlari", "en": "Types of algorithms", "t": "keyword"},
                {"uz": "Algoritm", "en": "Algorithm", "t": "direct"},
                {"uz": "Algoritm murakkabligi", "en": "Algorithm complexity", "t": "keyword"},
            ]},
            {"uz": "Maʼlumotlar bazasi", "en": "Database", "qs": [
                {"uz": "Maʼlumotlar bazasi turlari", "en": "Types of databases", "t": "keyword"},
                {"uz": "Maʼlumotlar bazasi", "en": "Database", "t": "direct"},
                {"uz": "SQL soʻrovlari", "en": "SQL queries", "t": "keyword"},
            ]},
            {"uz": "Dasturlash tillari", "en": "Programming languages", "qs": [
                {"uz": "Dasturlash tillari roʻyxati", "en": "Programming languages list", "t": "keyword"},
                {"uz": "Dasturlash tillari", "en": "Programming languages", "t": "direct"},
                {"uz": "Python dasturlash tili", "en": "Python programming language", "t": "keyword"},
            ]},
            {"uz": "Sunʼiy intellekt", "en": "Artificial intelligence", "qs": [
                {"uz": "Sunʼiy intellekt turlari", "en": "Types of AI", "t": "keyword"},
                {"uz": "Sunʼiy intellekt", "en": "Artificial intelligence", "t": "direct"},
                {"uz": "Machine learning algoritmlari", "en": "ML algorithms", "t": "keyword"},
            ]},
            {"uz": "Kompyuter tarmoqlari", "en": "Computer networks", "qs": [
                {"uz": "Internet protokollari", "en": "Internet protocols", "t": "keyword"},
                {"uz": "Kompyuter tarmoqlari", "en": "Computer networks", "t": "direct"},
                {"uz": "TCP/IP protokoli", "en": "TCP/IP protocol", "t": "keyword"},
            ]},
            {"uz": "Operatsion tizimlar", "en": "Operating systems", "qs": [
                {"uz": "Operatsion tizimlar turlari", "en": "Types of operating systems", "t": "keyword"},
                {"uz": "Operatsion tizimlar", "en": "Operating systems", "t": "direct"},
                {"uz": "Linux operatsion tizimi", "en": "Linux operating system", "t": "keyword"},
            ]},
            {"uz": "Veb-dasturlash", "en": "Web development", "qs": [
                {"uz": "HTML va CSS", "en": "HTML and CSS", "t": "keyword"},
                {"uz": "Veb-dasturlash", "en": "Web development", "t": "direct"},
                {"uz": "JavaScript dasturlash tili", "en": "JavaScript programming", "t": "keyword"},
            ]},
            {"uz": "Blokcheyn", "en": "Blockchain", "qs": [
                {"uz": "Blokcheyn texnologiyasi", "en": "Blockchain technology", "t": "keyword"},
                {"uz": "Blokcheyn", "en": "Blockchain", "t": "direct"},
                {"uz": "Kriptovalyutalar", "en": "Cryptocurrencies", "t": "keyword"},
            ]},
            {"uz": "Kiberxavfsizlik", "en": "Cybersecurity", "qs": [
                {"uz": "Kiberxavfsizlik tahdidlari", "en": "Cybersecurity threats", "t": "keyword"},
                {"uz": "Kiberxavfsizlik", "en": "Cybersecurity", "t": "direct"},
                {"uz": "Shifrlash algoritmlari", "en": "Encryption algorithms", "t": "keyword"},
            ]},
            {"uz": "Bulut hisoblash", "en": "Cloud computing", "qs": [
                {"uz": "Bulut hisoblash xizmatlari", "en": "Cloud computing services", "t": "keyword"},
                {"uz": "Bulut hisoblash", "en": "Cloud computing", "t": "direct"},
                {"uz": "AWS va Azure", "en": "AWS and Azure", "t": "keyword"},
            ]},
        ]
    },
}

# Generate test cases
test_cases = []
test_id = 0

for domain_name, domain_spec in test_spec.items():
    domain_type = domain_spec["type"]
    for topic in domain_spec["topics"]:
        for q in topic["qs"]:
            # Uzbek query → English corpus (cross-lingual)
            test_cases.append({
                "id": "sb_uz_on_en_{}".format(test_id),
                "domain": domain_name,
                "domain_type": domain_type,
                "query_language": "uz",
                "corpus_language": "en",
                "question": q["uz"],
                "target_title": topic["en"],
                "question_type": q["t"],
            })
            
            # English query → Uzbek corpus (cross-lingual)
            test_cases.append({
                "id": "sb_en_on_uz_{}".format(test_id),
                "domain": domain_name,
                "domain_type": domain_type,
                "query_language": "en",
                "corpus_language": "uz",
                "question": q["en"],
                "target_title": topic["uz"],
                "question_type": q["t"],
            })
            
            test_id += 1

# Write test cases
output_path = Path("/home/u6ef/rajantripathi.u6ef/soas_rag_eval/data/eval/semantic_boundary_test.jsonl")
with open(output_path, "w") as f:
    for case in test_cases:
        f.write(json.dumps(case, ensure_ascii=False) + "\n")

# Summary
print("=" * 60)
print("SEMANTIC BOUNDARY TEST SET CREATED")
print("=" * 60)
print()
print("Total test cases: {}".format(len(test_cases)))
print("Test domains: {}".format(len(test_spec)))
print("Topics per domain: ~10")
print("Question types: 3 (direct, keyword, factual)")
print("Directions: 2 (UZ→EN, EN→UZ)")
print()

# Count by domain type
cultural_count = len([c for c in test_cases if c["domain_type"] == "cultural"])
technical_count = len([c for c in test_cases if c["domain_type"] == "technical"])

print("By domain type:")
print("  Cultural: {} test cases".format(cultural_count))
print("  Technical: {} test cases".format(technical_count))
print()

# Count by domain
print("By domain:")
domain_counts = {}
for case in test_cases:
    d = case["domain"]
    domain_counts[d] = domain_counts.get(d, 0) + 1
for d in sorted(domain_counts.keys()):
    dt = test_spec[d]["type"]
    print("  {} ({}): {}".format(d, dt, domain_counts[d]))

print()
print("Saved to: {}".format(output_path))
