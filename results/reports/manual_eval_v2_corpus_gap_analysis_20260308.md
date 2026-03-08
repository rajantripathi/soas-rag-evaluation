# Manual Eval v2 Corpus Gap Analysis

## Why corpus coverage is the main bottleneck
- In the weak domains, every low-recall case corresponds to a missing gold source document in the current corpus.
- There were no cases in the focus domains where the gold document existed in the corpus but retrieval still missed it.
- This makes corpus coverage the first bottleneck, ahead of chunk size and embedding choice.

## Coverage Summary
| Language | Domain | Total | Gold docs present | Gold docs missing | Low recall |
| --- | --- | ---: | ---: | ---: | ---: |
| uz | history | 25 | 4 | 21 | 21 |
| uz | institutions | 25 | 3 | 22 | 22 |
| en | history | 25 | 10 | 15 | 15 |
| en | institutions | 25 | 8 | 17 | 17 |

## Example Missing Coverage Cases
### uz / history
- `uz_39` gold=1802 question=Tarixshunoslik tarixda nima?
- `uz_41` gold=1823 question=Turkiston tarixda nima?
- `uz_45` gold=1921 question=Oʻzbekiston siyosiy partiyalari tarixda nima?
- `uz_48` gold=2036 question=Muhammadsharif Soʻfizoda tarixda nima?
- `uz_59` gold=2277 question=Buyuk Ipak yoʻli tarixda nima?
- `uz_60` gold=2325 question=Oʻzbekiston tarixi tarixda nima?
- `uz_62` gold=2699 question=Avesto tarixda nima?
- `uz_63` gold=2704 question=Oʻrxun-Enasoy obidalari tarixda nima?

### uz / institutions
- `uz_42` gold=1887 question=Oʻzbekistondagi universitetlar qanday muassasa yoki tashkilot?
- `uz_43` gold=1903 question=Jahon iqtisodiyoti va diplomatiya universiteti qanday muassasa yoki tashkilot?
- `uz_50` gold=2067 question=Birlashgan Millatlar Tashkilotining Nizomi qanday muassasa yoki tashkilot?
- `uz_51` gold=2126 question=Google Scholar qanday muassasa yoki tashkilot?
- `uz_71` gold=2826 question=Munavvarqori Abdurashidxon oʻgʻli qanday muassasa yoki tashkilot?
- `uz_78` gold=4080 question=Coldplay qanday muassasa yoki tashkilot?
- `uz_80` gold=5309 question=Oʻzbekiston milliy teleradiokompaniyasi qanday muassasa yoki tashkilot?
- `uz_81` gold=5342 question=Oʻzbekcha Vikipediya qanday muassasa yoki tashkilot?

### en / history
- `en_63` gold=Súper Sábado Sensacional question=What is Súper Sábado Sensacional in historical context?
- `en_66` gold=Taoism question=What is Taoism in historical context?
- `en_68` gold=Emperor Xian of Han question=What is Emperor Xian of Han in historical context?
- `en_69` gold=Monte Carlo question=What is Monte Carlo in historical context?
- `en_72` gold=Emperor Gaozu of Tang question=What is Emperor Gaozu of Tang in historical context?
- `en_73` gold=History of the World Wide Web question=What is History of the World Wide Web in historical context?
- `en_74` gold=History of Freemasonry question=What is History of Freemasonry in historical context?
- `en_76` gold=World War I casualties question=What is World War I casualties in historical context?

### en / institutions
- `en_64` gold=Really Achieving Your Childhood Dreams question=What institution, organization, or formal body is Really Achieving Your Childhood Dreams?
- `en_84` gold=Llantrisant and Taff Vale Junction Railway question=What institution, organization, or formal body is Llantrisant and Taff Vale Junction Railway?
- `en_85` gold=Apprenticeship question=What institution, organization, or formal body is Apprenticeship?
- `en_86` gold=Maryland Terrapins football question=What institution, organization, or formal body is Maryland Terrapins football?
- `en_87` gold=Twelfth grade question=What institution, organization, or formal body is Twelfth grade?
- `en_88` gold=Global Marshall Plan Initiative question=What institution, organization, or formal body is Global Marshall Plan Initiative?
- `en_89` gold=Media conglomerate question=What institution, organization, or formal body is Media conglomerate?
- `en_90` gold=Discovery Channel question=What institution, organization, or formal body is Discovery Channel?

## Likely Missing Content Types
- Missing source documents: the dominant issue in Uzbek history and institutions.
- Named entity coverage: people, institutions, charters, and article titles are absent from the current corpus slice.
- Institutional descriptions: several questions require concise role or mandate descriptions that are not present.
- Historical context: historical concepts and figures need short, query-matching summaries to support retrieval.

## Corpus Expansion Plan
| source_type | target_language | target_domain | why this source is needed | expected benefit |
| --- | --- | --- | --- | --- |
| manual_curated_jsonl | uz | history | Current corpus is missing most gold source documents for Uzbek history examples. | Direct recall lift for named entities, historical concepts, and short definitional questions. |
| manual_curated_jsonl | uz | institutions | Current corpus lacks many Uzbek institutional descriptions and named organizations. | Better coverage for universities, media bodies, legal charters, and formal organizations. |
| future_wikipedia_expansion | uz | history | Need broader historical context beyond sparse article selection. | Improves recall for historical periods, texts, and people not covered in the smoke corpus. |
| future_wikipedia_expansion | uz | institutions | Need more institution pages and alternate phrasing around roles and mandates. | Improves retrieval when questions use descriptive wording rather than exact titles. |
| future_english_fallback | en | history/institutions | English weak cases also show source-document absence in the current limited corpus. | Provides cleaner cross-language control once Uzbek coverage is no longer the dominant bottleneck. |
