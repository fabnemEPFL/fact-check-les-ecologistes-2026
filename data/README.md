# Données structurées amont

Ce répertoire conserve uniquement les dérivés utiles pour auditer la sélection initiale des affirmations :

- `programme_text.txt.xz` : texte extrait du PDF ;
- `pages.json.xz` : extraction structurée des 208 pages ;
- `claim_candidates.json.xz` : 1 466 candidats automatiques ;
- `triage_candidates.json.xz` : triage des candidats.

Les anciennes copies partielles du ledger ont été retirées de `main`. Le ledger autoritatif se trouve dans le checkpoint désigné par `checkpoints/latest.json`.

Les fichiers XZ se restaurent avec `xz -dc`.
