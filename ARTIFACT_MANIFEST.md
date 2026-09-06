# Manifeste des artefacts — reprise du 6 septembre 2026

État matériel de référence : checkpoint persistant version 8, créé à `2026-09-06T14:42:25.942789Z`, restauré et contrôlé à `2026-09-06T19:10:51Z`.

## Artefacts complets sauvegardés dans le dépôt

Les fichiers XZ sont des compressions sans perte. Les colonnes « SHA restauré » permettent de contrôler le fichier original après `xz -dc`.

| Chemin GitHub | Taille stockée | SHA-256 stocké | Taille restaurée | SHA-256 restauré | Contenu |
|---|---:|---|---:|---|---|
| `checkpoints/registre_revue_factuelle_checkpoint_recupere_v8.json.xz` | 172 068 | `bb5e2e3ad951919e670f55edadb1e7cf657c117402a0bf9e96460cdcd26c0c23` | 2 471 106 | `8ea6ccb1d71c155650fd1e61b0f18643accf95ffc6f1cdf68999a7e2d5b5bf14` | Checkpoint intégral : ledger, candidats, triage, sources, verdicts, justifications, manifestes |
| `data/ledger_restored.json.xz` | 101 084 | `e836d067dd0d4eb8bbbd43e4941e2a2bfdc25e8b226a8c7c6ac2b17458e16ae4` | 1 081 681 | `47db6ff6a97b7f44e7417b2e9347087205659c7f685109bf96555e01967b54db` | 562 affirmations structurées, 566 occurrences |
| `data/triage_candidates.json.xz` | 80 476 | `3b70bd0a0be695a18fe15cf3b7c2465e7d5ffad9b7d57e9c94d0d969bc165f2e` | 712 947 | `8bf74572f1113dd120c21d47855736600824e1c18fa1fed6c5f010783bd7a46a` | Triage complet des 1 466 candidats |
| `data/claim_candidates.json.xz` | 72 708 | `4f5c1f40e8c1d85e4aa7ea7589d2d45294a748179f997b8292d6d9a3e0f05404` | 493 260 | `a68fcee391330a7e396af3711212d7c67c0e20e911d004b491e4e3d54a9cef50` | Candidats automatiques extraits |
| `data/pages.json.xz` | 123 780 | `58187890b4de6a8b0d99511ded6336dc55653a101732009c5f5ba86ac75851e6` | 464 767 | `6c627e4730b7e65be66017f4c6e1cee9363ec0ce3bec5e9dd7a41fe8f3f2e3a2` | Extraction structurée des 208 pages |
| `data/programme_text.txt.xz` | 127 768 | `2bd91ca37689e2af474ad3a775d7cf40433da9f1a02c1ebcf7b84f5cc73a699c` | 508 800 | `00da4c787824960d8e87108f519036154015a0f94ae53a3f2f946a8ce8cc2c62` | Texte intégral extrait |
| `scripts/extract_candidates.py` | 7 088 | `0f61af2b97a488c6d72003a91a22f4c8146bf8f3838fae31281cc4fa049b642b` | — | — | Script d’extraction des candidats |
| `source/vdef-programme-1.pdf.part-00` | 700 000 | `c479d04f7bc48522685f03eb2713d456c493a875a85c79ec8822cb9d91d8a1e6` | — | — | Fragment 1/3 du PDF source |
| `source/vdef-programme-1.pdf.part-01` | 700 000 | `eaa6396c6e671a9385ecf7efd2c5358e4ff39b12405ca46eb9b6beeec3d9563c` | — | — | Fragment 2/3 du PDF source |
| `source/vdef-programme-1.pdf.part-02` | 460 294 | `3a6893b955f327e379dfe58f7bc92fad89ceb7b929a1f7fa1b8b283c6a2e1fc6` | — | — | Fragment 3/3 du PDF source |

Le PDF reconstitué mesure 1 860 294 octets et a le SHA-256 `2fafd160291ff6677207c57ce1504ae6e62608cd19d8310e01a522b95beb50fc`.

## Artefacts présents localement mais non transférés individuellement

| Chemin local | Nombre | Taille totale | État / raison |
|---|---:|---:|---|
| `tmp/pdfs/source-pages/page-001.jpg` … `page-208.jpg` | 208 | 9 320 449 octets | Rendus dérivés reproductibles ; limite de charge utile du connecteur. Le checkpoint intégral conserve le chemin, la taille et le SHA-256 de chaque image. |
| `tmp/pdfs/contact/*.jpg` | 16 | 2 941 789 octets | Planches dérivées reproductibles ; même limitation. Le manifeste détaillé est inclus dans le checkpoint intégral. |
| `bundles/recovery_core_artifacts_2026-09-06T191051Z.tar.xz` | 1 | 338 984 octets | Copie locale redondante des fichiers déjà sauvegardés séparément ; SHA-256 `9621ca7a4551738d3e30710b4ce3b89802a274800bed401f0d21c285c300930a`. |

## Fichiers autonomes perdus lors de l’interruption

| Dernier chemin connu | Dernière taille connue | Dernier SHA-256 connu | Portée de la perte |
|---|---:|---|---|
| `scripts/ledger_data.py` | 292 480 | `426bda34cccc307208e719305a74959f87a3d947c995a27d279d35d6ac129c0d` | Code source absent ; toutes les lignes et preuves produites jusqu’à la version 8 survivent dans le checkpoint. |
| `scripts/triage_candidates.py` | 6 208 | `653f2c07414a4174b25cc1486c8288cd65038f392d63251769e702c1619fe380` | Code source absent ; sortie complète restaurée et sauvegardée. |

Aucun verdict historique du corpus ancien de 403 affirmations n’est considéré comme restauré sans dossier matériel correspondant.
