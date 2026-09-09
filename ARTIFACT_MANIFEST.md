# Manifeste des artefacts — état final 2026-09-09

Ce fichier résume les artefacts autoritatifs du projet final. Les anciens checkpoints de reprise et artefacts intermédiaires sont conservés dans le dépôt pour traçabilité historique, mais ne doivent plus être utilisés comme état courant.

## Source de vérité

`checkpoints/latest.json` est le pointeur machine vers l'état courant.

Checkpoint factuel autoritatif final :

- chemin : `checkpoints/final_coherence_2026-09-09_targeted.json.xz.b64`
- encodage : texte Base64 représentant un flux XZ ; décoder le Base64 puis décompresser XZ
- SHA-256 du fichier JSON décompressé : `fce47f27418965733511a98e630129dc54afb574beb421f2bdfa22e23b6c0d32`
- 564 affirmations uniques
- 568 occurrences
- 564 affirmations sourcées et vérifiées

## QA et statistiques finales

- `analysis/statistics_final.json`
- `analysis/statistics_final.csv`
- `analysis/quality_control_final.json`
- `analysis/anomalies_final.md`
- `analysis/source_registry_final.json`
- `analysis/final_cleanup_changes.jsonl`

La QA finale indique `report_ready=true`, sans anomalie bloquante ni non bloquante.

## Estimation énergétique

- `metrics/energy_estimate.md`
- `metrics/energy_estimate.json`
- `scripts/estimate_energy.py`
- `metrics/compute_log.jsonl`

Estimation finale : **0,5 kWh** en valeur centrale, avec un intervalle plausible de **0,1–2 kWh** pour l'inférence IA attribuable au travail documenté. Cette valeur est une estimation et non une mesure de l'infrastructure OpenAI.

## Rapport final

- `reports/final/revue_factuelle_programme_ecologistes_2026.pdf`
- `reports/final/revue_factuelle_programme_ecologistes_2026.md`
- `reports/final/REPORT_MANIFEST.json`
- `reports/final/qa_render/` : rendu PNG des pages utilisé pour la QA
- `scripts/generate_final_report.py` : générateur et contrôles automatiques

Les valeurs exactes de taille, nombre de pages, nombre d'annotations de liens et SHA-256 du PDF publié sont inscrites dans `reports/final/REPORT_MANIFEST.json` et doivent être lues depuis le même commit/tag que le PDF.

## Reproduction

La procédure de reproduction du PDF est documentée dans `REPRODUCIBILITY.md`.

Le workflow `.github/workflows/generate_final_report.yml` fournit également une reproduction automatisée sur Ubuntu/Python 3.11 : installation des dépendances, génération, contrôle des 564 IDs, contrôle des verdicts, vérification des liens et rendu de toutes les pages avec Poppler.

## Artefacts historiques

Les fichiers de reprise du 6 septembre 2026 (`registre_revue_factuelle_checkpoint_recupere_v8.json.xz`, `data/ledger_restored.json.xz`, fragments du PDF source, etc.) sont conservés comme traces de récupération après interruption. Leurs compteurs historiques (562 affirmations / 566 occurrences, puis états intermédiaires ultérieurs) ne décrivent pas l'état final du projet.

Pour toute utilisation ou citation de la version finale, partir de `checkpoints/latest.json`, du checkpoint autoritatif qu'il désigne et de `reports/final/REPORT_MANIFEST.json`.
