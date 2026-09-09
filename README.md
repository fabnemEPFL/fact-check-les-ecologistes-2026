# Fact-check du programme des Écologistes 2026

Revue factuelle exhaustive du programme 2026 des Écologistes.

## État final

- PDF source : 208 pages
- Chapitres couverts : 66 / 66
- Candidats automatiques extraits : 1 466
- Affirmations factuelles uniques : **564**
- Occurrences : **568**
- Affirmations sourcées et vérifiées : **564 / 564**
- Audit contradictoire exhaustif indépendant : **0 / 564**
- QA mécanique finale : **réussie**
- Anomalies bloquantes : **0**
- `report_ready` : **true**

Distribution finale des verdicts :

- Exact : 73
- Globalement exact : 255
- À nuancer : 161
- Trompeur : 20
- Faux : 7
- Invérifiable ou insuffisamment étayé : 48

Le checkpoint factuel autoritatif est désigné par `checkpoints/latest.json`. À l'état final actuel, il s'agit de :

`checkpoints/final_coherence_2026-09-09_targeted.json.xz.b64`

## Rapport final

- PDF : `reports/final/revue_factuelle_programme_ecologistes_2026.pdf`
- Source Markdown : `reports/final/revue_factuelle_programme_ecologistes_2026.md`
- Manifeste de publication : `reports/final/REPORT_MANIFEST.json`

Le rapport reprend les **564 affirmations** et leurs sources finales. Il inclut aussi l'estimation de la **consommation électrique totale attribuable à l'inférence IA pour l'ensemble de l'analyse** : valeur centrale **0,5 kWh**, intervalle plausible **0,1–2 kWh**. Il s'agit d'une estimation, pas d'une mesure de l'infrastructure OpenAI.

## Reproduire le PDF

Les instructions complètes sont dans [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md).

En bref, le rapport peut être régénéré :

- via le workflow GitHub Actions `.github/workflows/generate_final_report.yml` (`workflow_dispatch`) ;
- ou localement avec Python 3.11, `reportlab`, `pypdf` et `pdftoppm`, puis :

```bash
python scripts/generate_final_report.py
```

Le générateur contrôle le SHA du checkpoint, les 564 IDs, les verdicts, les liens du PDF et rend toutes les pages en PNG pour la QA.

## Méthodologie et artefacts

- `methodology/analysis_spec.md` : cahier des charges méthodologique normatif ;
- `analysis/statistics_final.json` : statistiques finales ;
- `analysis/quality_control_final.json` : QA mécanique finale ;
- `analysis/source_registry_final.json` : registre final de résolution des sources ;
- `metrics/energy_estimate.md` et `.json` : estimation énergétique et hypothèses ;
- `ARTIFACT_MANIFEST.md` : état des principaux artefacts finaux et historiques.

Le rapport évalue la précision factuelle des affirmations retenues ; il ne constitue ni une note politique globale du programme ni une recommandation d'adopter ou de rejeter ses mesures.
