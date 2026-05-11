# Data sources for Panel

All sources are public / open-license. Verify license before committing data into the repo — store raw downloads in Unity Catalog Volumes, not in git.

## Labor codes (destination countries)

| Country | Instrument | URL | License | Format |
|---|---|---|---|---|
| Saudi Arabia | Labor Law (Royal Decree M/51 2005, w/ 2017 amendments) | https://www.ilo.org/dyn/natlex/ → search "Saudi Arabia Labor Law" | Public | PDF (EN + AR) |
| Malaysia | Employment Act 1955 (latest consolidated 2022 amendments) | https://www.mohr.gov.my/ | Public | PDF |
| Singapore | Employment of Foreign Manpower Act + Employment Act | https://sso.agc.gov.sg/ | Public | HTML |
| Hong Kong | Employment Ordinance (Cap 57) | https://www.elegislation.gov.hk/ | Public | HTML |
| UAE | Federal Decree-Law No. 33 of 2021 | https://u.ae/en/information-and-services/jobs/labour-rights-and-responsibilities | Public | PDF |

## Labor codes (origin countries — for understanding worker rights at home)

| Country | Instrument | URL | License | Format |
|---|---|---|---|---|
| Philippines | RA 11641 (Migrant Workers and Overseas Filipinos Act, amended) | https://www.officialgazette.gov.ph/ | Public | HTML |
| Indonesia | UU 18/2017 (Pelindungan Pekerja Migran Indonesia) | https://peraturan.bpk.go.id/Details/37772 | Public | PDF (ID) |

## International standards

| Source | Document | URL | Format |
|---|---|---|---|
| ILO | C97 — Migration for Employment Convention | https://www.ilo.org/dyn/normlex/en/ | HTML |
| ILO | C143 — Migrant Workers Supplementary Provisions | https://www.ilo.org/dyn/normlex/en/ | HTML |
| ILO | C181 — Private Employment Agencies | https://www.ilo.org/dyn/normlex/en/ | HTML |
| ILO | C189 — Domestic Workers Convention | https://www.ilo.org/dyn/normlex/en/ | HTML |
| ILO | C190 — Violence and Harassment Convention | https://www.ilo.org/dyn/normlex/en/ | HTML |
| ILO | Fair Recruitment Initiative — general principles | https://www.ilo.org/global/topics/fair-recruitment/ | HTML/PDF |
| ASEAN | Rights-Based Standard Employment Contract (research compilation) | https://asean.org/wp-content/uploads/2023/12/Research-On-Workers-Right-Based-Standard-Employment-Contract-DEC20-Final.pdf | PDF |

## Case archive seed corpora

| Source | What | URL | Notes |
|---|---|---|---|
| ILO | "Empowering Filipino Migrant Workers" — case studies | https://www.ilo.org/media/315011/download | PDF, ~80 cases extractable |
| ILO | "Combating Forced Labour and Trafficking of Indonesian Migrant Workers" — Phase II report | https://www.ilo.org/projects-and-partnerships/projects/combating-forced-labour-and-trafficking-indonesian-migrant-workers-phase-ii | Project reports w/ cases |
| Human Rights Watch | Reports on KSA / Gulf domestic workers | https://www.hrw.org/topic/womens-rights/domestic-workers | Permission: cite + link, do not redistribute raw text |
| Amnesty International | "Exploited for Profit, Failed by Governments" series | https://www.amnesty.org/ | Same — cite + link |

## Embassy + NGO directory seed

| Source | URL | Notes |
|---|---|---|
| DFA Philippines — POLOs | https://dfa.gov.ph/list-of-philippine-overseas-labor-offices | Live JSON if possible, else scrape table |
| BP2MI (Indonesia migrant worker agency) | https://bp2mi.go.id/ | Indonesian-only; translate field names |
| Migrante International | https://migranteinternational.org/ | NGO directory by country |
| ILO Migrant Worker Resource Centres | https://www.ilo.org/asia/projects/labour-migration | Per-country listings |

## Multilingual model selection

| Language pair | Model | Why |
|---|---|---|
| Tagalog ↔ English | SEA-LION v3 or NLLB-200 | SEA-LION trained on SEA languages; better Filipino than vanilla GPT-class models |
| Bahasa Indonesia ↔ English | SEA-LION v3 / Sailor | Same |
| Arabic → English (statute names only) | gpt-4o-mini or claude-sonnet | Quality matters less since we only render citations |

## Ingestion order

1. Labor codes → `labor_codes` Delta table (most predictable, smallest)
2. ILO conventions + ASEAN standard → `international_standards` Delta table
3. Case studies → embed → `case_archive` (Lakebase)
4. Embassy / NGO directories → `embassy_directory`, `ngo_directory` (Lakebase)
5. Test corpus: 5-10 real contracts (anonymized, from publicly-published ILO case reports) for the smoke test
