# Artifact manifest

Ce manifeste recopie l'état de récupération enregistré le 6 septembre 2026 à 13:32 UTC. Les chemins sont ceux de l'environnement du run original.

| Path original | Taille | SHA-256 | État de transfert GitHub |
|---|---:|---|---|
| `upload/vdef-programme-1.pdf` | 1,860,294 B | `2fafd160291ff6677207c57ce1504ae6e62608cd19d8310e01a522b95beb50fc` | Référencé, binaire non transféré par le connecteur texte actuel |
| `tmp_programme.txt` | 508,800 B | `00da4c787824960d8e87108f519036154015a0f94ae53a3f2f946a8ce8cc2c62` | Pas matériellement accessible depuis cette conversation |
| `tmp/pages.json` | 464,767 B | `6c627e4730b7e65be66017f4c6e1cee9363ec0ce3bec5e9dd7a41fe8f3f2e3a2` | Pas matériellement accessible depuis cette conversation |
| `tmp/claim_candidates.json` | 493,260 B | `a68fcee391330a7e396af3711212d7c67c0e20e911d004b491e4e3d54a9cef50` | Pas matériellement accessible depuis cette conversation |
| `tmp/triage_candidates.json` | 712,947 B | `8bf74572f1113dd120c21d47855736600824e1c18fa1fed6c5f010783bd7a46a` | Pas matériellement accessible depuis cette conversation |
| `tmp/ledger_restored.json` | 924,961 B | `da8fa8b6beead5a118ac2b10ae728cf126d291c8851cee085688a7ad4bc98702` | Pas matériellement accessible depuis cette conversation |
| `scripts/extract_candidates.py` | 7,088 B | `0f61af2b97a488c6d72003a91a22f4c8146bf8f3838fae31281cc4fa049b642b` | Pas matériellement accessible depuis cette conversation |
| `scripts/triage_candidates.py` | 6,208 B | `653f2c07414a4174b25cc1486c8288cd65038f392d63251769e702c1619fe380` | Pas matériellement accessible depuis cette conversation |
| `scripts/ledger_data.py` | 180,063 B | `e264aaa1d391ef4f5978512ae4a8dec9009551deb53df13c19a07fb615ff260d` | Pas matériellement accessible depuis cette conversation |

Le run signalait également **208 images de pages** (`tmp/pdfs/source-pages/page-001.jpg` à `page-208.jpg`) et **16 planches de contact**. Leur manifeste avec tailles et SHA-256 existe dans le checkpoint persistant, mais les binaires ne sont pas montés dans l'environnement de cette conversation.

## Fichiers historiques explicitement perdus avant la reconstruction

Le checkpoint indique que les versions originales de `ledger_data.py`, `ledger.json`, `ledger.csv` et `audit_summary.json`, mentionnées dans l'état compacté de la session précédente, n'étaient plus présentes dans le workspace ni dans les fichiers persistants retrouvés. Les fichiers `ledger_data.py` / `ledger_restored.json` ci-dessus sont des **reconstructions ultérieures**, pas le ledger historique original avec toutes les preuves ligne par ligne.
