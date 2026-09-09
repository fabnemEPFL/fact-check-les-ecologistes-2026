# Reproduire le rapport final

Le rapport final est généré de manière déterministe au niveau du **contenu** à partir du checkpoint factuel autoritatif et des artefacts de QA/énergie présents dans le dépôt. Le PDF publié dans une release reste l'artefact canonique pour la vérification d'un SHA-256 exact : ReportLab peut faire varier certains octets de métadonnées internes entre deux exécutions sans changer le contenu visible.

## Entrées autoritatives

Le générateur `scripts/generate_final_report.py` lit automatiquement :

- `checkpoints/latest.json` ;
- le checkpoint complet désigné par `authoritative_recovery_source` ;
- `analysis/statistics_final.json` ;
- `metrics/energy_estimate.json`.

À la version finale 2026-09-09, le checkpoint factuel est :

`checkpoints/final_coherence_2026-09-09_targeted.json.xz.b64`

Le générateur vérifie le SHA-256 du JSON décompressé avant de produire le rapport.

## Méthode recommandée : GitHub Actions

Le workflow `.github/workflows/generate_final_report.yml` est exécutable manuellement depuis l'onglet **Actions** de GitHub via `workflow_dispatch`.

Il :

1. utilise Ubuntu et Python 3.11 ;
2. installe `reportlab`, `pypdf` et `poppler-utils` ;
3. exécute `python scripts/generate_final_report.py` ;
4. vérifie les 564 identifiants et leurs verdicts ;
5. vérifie la présence de liens dans le PDF ;
6. rend toutes les pages en PNG avec `pdftoppm` pour une QA de rendu ;
7. régénère `reports/final/REPORT_MANIFEST.json` ;
8. commit les artefacts de rapport sur `main`.

## Reproduction locale

Prérequis :

- Python 3.11 ;
- `pip` ;
- Poppler (`pdftoppm`) ;
- idéalement les polices DejaVu Sans installées (sinon le script retombe sur Helvetica).

Sous Debian/Ubuntu :

```bash
sudo apt-get update
sudo apt-get install -y poppler-utils fonts-dejavu-core
python3.11 -m venv .venv
source .venv/bin/activate
pip install reportlab pypdf
python scripts/generate_final_report.py
```

Les artefacts produits sont :

- `reports/final/revue_factuelle_programme_ecologistes_2026.pdf` ;
- `reports/final/revue_factuelle_programme_ecologistes_2026.md` ;
- `reports/final/REPORT_MANIFEST.json` ;
- `reports/final/qa_render/*.png`.

## Contrôles attendus

Le générateur doit terminer sans exception et le manifeste doit indiquer :

- `qa.status = "passed"` ;
- 564 IDs ;
- distribution des verdicts identique à `analysis/statistics_final.json` ;
- estimation énergétique reprise depuis `metrics/energy_estimate.json` ;
- nombre de pages et SHA-256 du PDF nouvellement généré.

Le rapport final doit explicitement contenir la **consommation électrique totale estimée pour l'ensemble de l'analyse** : 0,5 kWh en valeur centrale, avec une plage plausible de 0,1 à 2 kWh pour l'état final actuel.

## Vérification d'une version publiée

Pour vérifier le PDF canonique téléchargé depuis une release :

```bash
sha256sum revue_factuelle_programme_ecologistes_2026.pdf
```

Comparer le résultat au SHA-256 inscrit dans `reports/final/REPORT_MANIFEST.json` de la même release/tag.
