# Site Entity Resolution Candidates v0.1

Candidate generation for manual resolution of manufacturing-site mentions.

> Lexical similarity is not evidence of physical facility identity.

- Unique raw site mentions: **9**
- Candidate pairs requiring review: **3**
- Automatically merged entities: **0**

## Candidate pairs

| Score | Reason | Left mention | Right mention | Decision |
|---:|---|---|---|---|
| 0.95 | `same_company_prefix` | Mefar İlaç San. A.Ş. | Mefar İlaç San. A.Ş., Ramazanoğlu Mah. Ensar Cad. No:20, Kurtköy-Pendik/İstanbul | `review_required` |
| 0.95 | `same_company_prefix` | VEM İlaç San. ve Tic. A.Ş., Çerkezköy Organize Sanayi Bölgesi, Karaağaç Mah. Fatih Blv. No:38, Kapaklı/Tekirdağ | VEM İlaç San. ve Tic. A.Ş., Çerkezköy Organize Sanayi Bölgesi, Karaağaç Mah. Fatih Bulv. No:38, Kapaklı/Tekirdağ | `review_required` |
| 0.84 | `lexical_similarity` | Gensenta İlaç Sanayi ve Ticaret A.Ş., Sanayi Cad. No:13, Yenibosna, Bahçelievler/İstanbul | Mustafa Nevzat İlaç Sanayii A.Ş., Sanayi Cad. No:13, Yenibosna, Bahçelievler/İstanbul | `review_required` |

## Interpretation

Pairs in this table are candidates for manual entity review only. A shared company name, address fragment, or high lexical similarity does not prove that two records identify the same manufacturing facility.

