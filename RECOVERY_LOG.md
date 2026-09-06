# Journal de récupération après interruption

## État comparé

Le dépôt GitHub contenait au plus récent checkpoint confirmé : 558 affirmations, 562 occurrences et 36 affirmations sourcées/vérifiées à 14:13 UTC. Le workspace actif avait perdu les fichiers de travail avancés et ne conservait que les artefacts d’extraction. La File Library conservait toutefois un checkpoint version 8 créé à 14:42:25 UTC : 562 affirmations, 566 occurrences et 47 affirmations sourcées/vérifiées.

Le checkpoint version 8 a donc été retenu comme source de vérité. Aucun verdict de l’ancien corpus historique de 403 affirmations n’a été réinjecté.

## Pertes constatées

Les fichiers autonomes `scripts/ledger_data.py` et `scripts/triage_candidates.py` ne survivent pas dans le workspace courant. Leurs sorties complètes utiles survivent dans le checkpoint version 8. Cinq dossiers postérieurs évoqués dans l’état conversationnel compacté (`PT-005`, `PT-030`, `PT-004`, `PT-001`, `PT-031`) ne figurent pas dans ce checkpoint ; ils ne sont donc pas comptés comme restaurés et devront être reconstruits puis revérifiés avant d’être réintégrés.

## Contrôles d’intégrité

Le JSON version 8 est valide, contient 562 identifiants uniques sans doublon, 566 occurrences, 47 dossiers avec sources, verdict et justification, et 0 dossier marqué audité contradictoirement. Le premier identifiant non terminé selon l’ordre page/candidat/identifiant est `PT-005`.
