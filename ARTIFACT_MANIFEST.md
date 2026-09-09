# Manifeste des artefacts — état courant

Ce fichier décrit les artefacts conservés sur `main` après finalisation et nettoyage.

## Source de vérité factuelle

- pointeur : `checkpoints/latest.json`
- checkpoint : `checkpoints/final_coherence_2026-09-09_targeted.json.xz.b64`
- encodage : Base64 d'un flux XZ
- SHA-256 du JSON décompressé : `fce47f27418965733511a98e630129dc54afb574beb421f2bdfa22e23b6c0d32`
- 564 affirmations uniques ; 568 occurrences ; 564/564 vérifiées

Les checkpoints de progression ne sont plus nécessaires pour restaurer l'état factuel final et ont été retirés de `main`.

## Analyse finale conservée

- `analysis/statistics_final.json` et `.csv`
- `analysis/quality_control_final.json`
- `analysis/anomalies_final.md`
- `analysis/source_registry_final.json`
- `analysis/final_cleanup_changes.jsonl`

## Données amont conservées

`data/` conserve le texte/pages extraits, les candidats automatiques et leur triage. Les copies historiques partielles du ledger ont été supprimées : le checkpoint final les remplace comme source de vérité.

## Énergie

- `metrics/energy_estimate.md` et `.json`
- `metrics/compute_log.jsonl`
- `scripts/estimate_energy.py`

Estimation réconciliée courante : **0,7 kWh**, plage plausible **0,1–4 kWh**. Le détail de l'écart avec l'estimation intermédiaire de 2,7 kWh est conservé dans la documentation énergétique.

## Rapport

- `reports/final/revue_factuelle_programme_ecologistes_2026.pdf`
- `reports/final/revue_factuelle_programme_ecologistes_2026.md`
- `reports/final/REPORT_MANIFEST.json`
- `scripts/generate_final_report.py`

`reports/final/qa_render/` est dérivé, régénérable et désormais ignoré par Git.

## Source

La copie exacte du programme analysé reste dans `source/` en trois fragments ; `source/README.md` documente leur concaténation et le SHA-256 attendu.

## Retiré de `main`

Après finalisation ont été supprimés : checkpoints intermédiaires, bundles de récupération, `analysis/interim_415/`, `reports/interim_415/`, rendus PNG de QA, workflows/scripts dédiés aux rapports intermédiaires et copies partielles du ledger.

Tous restent récupérables dans l'historique Git. Les tags/releases `v1.0` et `v1.0.1` ne sont ni réécrits ni supprimés.
