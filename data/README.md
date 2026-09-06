# Données de reprise

Les fichiers volumineux sont stockés en XZ, sans perte. Pour restaurer un fichier :

```bash
xz -dc ledger_restored.json.xz > ledger_restored.json
```

Les SHA-256 des fichiers compressés et restaurés figurent dans `checkpoints/latest.json` et `ARTIFACT_MANIFEST.md`.

`ledger_restored.json` contient les 562 lignes structurées. Le checkpoint intégral contient en plus les 1 466 candidats, le triage complet, les manifestes des 208 rendus de pages et des 16 planches de contact, ainsi que les métadonnées de récupération.
