# Estimation finale de l’énergie d’inférence IA — sanity check méthodologique

## Résultat révisé

**Estimation centrale : 0,5 kWh ; intervalle plausible : 0,1–2 kWh.** Cette estimation est attribuable aux interactions d’inférence IA du fact-checking. Ce n’est pas une mesure de l’infrastructure OpenAI ni de ses centres de données.

La version précédente (0,2 kWh ; 0,08–0,7 kWh) était insuffisamment explicite : son point central se rapprochait de 53 × 3,91 Wh alors que les 53 entrées du journal ne sont pas 53 appels modèle. Elles représentent un mélange de batches, de checkpoints de continuité, de nettoyages, de résolution des sources, de cohérence et de QA. Les traiter toutes comme une seule inférence lourde sous-estime les itérations; les traiter toutes comme des conversations indépendantes les surestime.

## Ce que mesure réellement le journal

Directement enregistré : 53 entrées avant l’estimation, 522 affirmations marquées terminées dans les lignes qui renseignent ce champ, environ 75 appels/lots de recherche et 548 autres appels d’outils. Les tokens d’entrée/sortie/raisonnement/cache sont tous inconnus.

Reconstruction : 50 **batches substantiels** (lignes avec affirmations traitées et/ou nettoyage, sources ou cohérence). Une entrée peut couvrir 5–54 affirmations; des checkpoints consécutifs peuvent segmenter une même exécution. Aucun des deux comptes n’est un nombre observé d’inférences internes.

## Méthode A — activité agentique

Les 623 interactions outils/recherche ne sont pas assimilées à 623 requêtes longues. Elles servent de proxy de continuité/itération, avec seulement une fraction convertie en tours de coordination. Les synthèses de raisonnement long sont attribuées aux 50 batches, pas aux checkpoints isolés.

| Scénario | Calcul reproductible | Résultat |
|---|---:|---:|
| Bas | 50 × 1 × 1,5 Wh + 62 × 0,16 Wh | 0,085 kWh → **0,1 kWh** |
| Central | 50 × 2 × 3,91 Wh + 187 × 0,31 Wh | 0,449 kWh → **0,5 kWh** |
| Haut | 50 × 5 × 7,05 Wh + 436 × 0,60 Wh | 2,024 kWh → **2 kWh** |

## Méthode B — contrôle par affirmations regroupées

Cette méthode ne transforme pas 522 affirmations en 522 appels. Elle suppose respectivement 10, 4,5 et 2 affirmations par synthèse de raisonnement : 53, 116 et 261 synthèses équivalentes. À 1,5, 3,91 et 7,05 Wh, elle donne **0,08, 0,45 et 1,84 kWh**. Sa valeur centrale (0,45 kWh) converge avec la méthode A (0,449 kWh).

Le résultat final est donc l’arrondi prudent de cette convergence : **0,5 kWh**, avec une plage de **0,1–2 kWh**. La hausse est méthodologique, pas la prétention de connaître les tokens, le matériel, l’utilisation, le batching ou le PUE réels.

## Périmètre et limites

Inclus : inférence IA associée au travail documenté de fact-checking. Les serveurs de recherche/outils sont signalés comme activité auxiliaire mais non mesurés séparément, afin d’éviter un double compte arbitraire. Sont exclus : entraînement, fabrication du matériel, ordinateur utilisateur, réseau, stockage GitHub et impacts indirects.

## Références

- [Oviedo et al., *Energy Use of AI Inference*](https://arxiv.org/abs/2509.20241) : 0,31 Wh médian par requête >200B dans leurs hypothèses de service et 3,91 Wh dans leur scénario de test-time compute 15×; référence de charge, non mesure OpenAI.
- [Elsworth et al. (Google), *Measuring the environmental impact of delivering AI at Google scale*](https://services.google.com/fh/files/misc/measuring_the_environmental_impact_of_delivering_ai_at_google_scale.pdf) : mesure en production; 0,24 Wh pour le prompt Gemini Apps médian, non transposé.
- [Chung et al., *ML.ENERGY Benchmark*](https://proceedings.neurips.cc/paper_files/paper/2025/hash/73750e4e965ab29ac16a4bb38c4c1b9f-Abstract-Datasets_and_Benchmarks_Track.html) et [Niu et al., *TokenPowerBench*](https://arxiv.org/abs/2512.03024) : l’énergie varie fortement selon préremplissage, décodage, contexte, batch, parallélisme et matériel.
