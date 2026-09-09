# Reproduire le rapport final

Le rapport est généré de manière déterministe au niveau du **contenu** à partir du checkpoint factuel autoritatif et des artefacts de statistiques/énergie. Pour vérifier un SHA-256 exact, le PDF attaché à une release reste canonique : ReportLab peut faire varier certains octets de métadonnées entre deux exécutions sans changer le contenu visible.

## Entrées autoritatives

`scripts/generate_final_report.py` lit :

- `checkpoints/latest.json` ;
- le checkpoint désigné par `authoritative_recovery_source` ;
- `analysis/statistics_final.json` ;
- `metrics/energy_estimate.json`.

Checkpoint factuel : `checkpoints/final_coherence_2026-09-09_targeted.json.xz.b64`. Le générateur vérifie le SHA-256 du JSON décompressé avant génération.

## GitHub Actions

Le workflow `.github/workflows/generate_final_report.yml` est exécutable via **Actions → Generate final factual review report → Run workflow**. Il utilise Ubuntu/Python 3.11, installe `reportlab`, `pypdf` et `poppler-utils`, génère le rapport, contrôle les 564 identifiants et les verdicts, vérifie les liens et rend toutes les pages avec `pdftoppm` avant de régénérer le manifeste.

Les PNG de QA sont des sorties dérivées : ils sont ignorés par Git et ne doivent pas être conservés sur `main`.

## Reproduction locale

Sous Debian/Ubuntu :

```bash
sudo apt-get update
sudo apt-get install -y poppler-utils fonts-dejavu-core
python3.11 -m venv .venv
source .venv/bin/activate
pip install reportlab pypdf
python scripts/generate_final_report.py
```

Artefacts publiables produits :

- `reports/final/revue_factuelle_programme_ecologistes_2026.pdf` ;
- `reports/final/revue_factuelle_programme_ecologistes_2026.md` ;
- `reports/final/REPORT_MANIFEST.json`.

Le script crée aussi `reports/final/qa_render/*.png` pour la QA ; ce répertoire est volontairement non versionné et peut être supprimé après le contrôle.

## Contrôles attendus

Le manifeste doit notamment confirmer `qa.status = "passed"`, 564 IDs, la distribution validée des verdicts, l'estimation énergétique provenant de `metrics/energy_estimate.json`, le nombre de pages et le SHA-256 du PDF généré.

L'état énergétique courant est **0,7 kWh** en valeur centrale, plage plausible **0,1–4 kWh**. Il remplace l'approximation intermédiaire de **2,7 kWh**, qui assimilait chaque affirmation à une requête lourde indépendante ; la réconciliation complète est documentée dans `metrics/energy_estimate.md`.

## Vérifier une release

```bash
sha256sum revue_factuelle_programme_ecologistes_2026.pdf
```

Comparer au SHA de `REPORT_MANIFEST.json` du **même tag/release**.

## Traçabilité historique

`main` ne conserve plus les checkpoints de progression, rapports intermédiaires ni bundles de récupération. Ils restent accessibles dans l'historique Git et dans les anciens tags lorsqu'ils y étaient présents. Cette suppression n'altère pas le checkpoint factuel final.
