# Fact-check du programme des Écologistes 2026

Revue factuelle exhaustive du programme 2026 des Écologistes.

## État courant

- PDF source : 208 pages
- Chapitres couverts : 66 / 66
- Affirmations factuelles uniques : **564**
- Occurrences : **568**
- Affirmations sourcées et vérifiées : **564 / 564**
- Audit contradictoire exhaustif indépendant : **0 / 564**
- QA mécanique finale : **réussie**
- Anomalies bloquantes : **0**
- `report_ready` : **true**

Distribution finale des verdicts : Exact 73 ; Globalement exact 255 ; À nuancer 161 ; Trompeur 20 ; Faux 7 ; Invérifiable ou insuffisamment étayé 48.

`checkpoints/latest.json` désigne l'état machine courant. Le checkpoint factuel autoritatif est :

`checkpoints/final_coherence_2026-09-09_targeted.json.xz.b64`

## Rapport final

- PDF : `reports/final/revue_factuelle_programme_ecologistes_2026.pdf`
- Source Markdown : `reports/final/revue_factuelle_programme_ecologistes_2026.md`
- Manifeste : `reports/final/REPORT_MANIFEST.json`
- Publication courante : release **v1.0.1**

L'estimation énergétique réconciliée est **0,7 kWh** en valeur centrale, avec une plage plausible de **0,1–4 kWh**. L'ancienne estimation intermédiaire de 2,7 kWh utilisait une approximation différente (« une requête lourde par affirmation ») ; la méthode finale est documentée dans `metrics/energy_estimate.md` et `.json`.

## Reproduire le PDF

Les instructions complètes sont dans [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md). En bref :

```bash
python scripts/generate_final_report.py
```

Le même processus peut être lancé via `.github/workflows/generate_final_report.yml`. Le générateur contrôle le checkpoint, les 564 IDs, les verdicts et les liens, puis rend toutes les pages en PNG pour la QA. Ces PNG sont temporaires et ne sont pas versionnés.

## Structure utile

- `methodology/analysis_spec.md` : cahier des charges méthodologique ;
- `checkpoints/` : `latest.json` et le seul checkpoint factuel final ;
- `analysis/` : statistiques, QA, registre des sources et journal de nettoyage finaux ;
- `metrics/` : journal d'exécution et estimation énergétique ;
- `reports/final/` : rapport publiable et manifeste ;
- `scripts/` : générateurs et utilitaires de pipeline ;
- `source/` : copie exacte du programme source en fragments ;
- `data/` : extractions amont utiles pour auditer la sélection des affirmations.

Les dizaines de checkpoints de progression, rapports/payloads intermédiaires, bundles de récupération et rendus PNG de QA ont été retirés de `main` après finalisation. Ils restent récupérables dans l'historique Git ; les tags/releases publiés ne sont pas réécrits.

Le rapport évalue la précision factuelle des affirmations retenues ; il ne constitue ni une note politique globale du programme ni une recommandation d'adopter ou de rejeter ses mesures.
