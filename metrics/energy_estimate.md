# Réconciliation finale de l’estimation d’énergie d’inférence IA

## Estimation finale retenue

**Estimation centrale : 0,7 kWh ; intervalle plausible : 0,1–4 kWh.** Elle porte sur l’électricité attribuable aux interactions d’inférence IA documentées pour le fact-checking. Ce n’est pas une mesure de l’infrastructure OpenAI ni de ses centres de données.

Aucune télémétrie de tokens, d’appels internes, de matériel, de batch, de cache ou de PUE n’est disponible. Les chiffres ci-dessous sont donc une reconstruction explicite, séparant les observations du journal et les hypothèses.

## Pourquoi 2,7 kWh et 0,5 kWh différaient

Le rapport intermédiaire à 415 affirmations appliquait environ `415 × 4,32 Wh × 1,5 = 2,7 kWh`. Il traitait, par construction, chaque affirmation vérifiée comme une requête de raisonnement très lourde indépendante, puis ajoutait 50 % pour l’orchestration. Cette règle était simple et prudente, mais elle compte implicitement des synthèses répétées alors qu’un même run traite fréquemment 5–54 affirmations et mutualise contexte, recherche et décision.

La méthode finale précédente regroupait le travail en 50 batches substantiels : `50 × 2 × 3,91 Wh + 187 × 0,31 Wh = 0,449 kWh`, arrondi à 0,5 kWh. Elle corrige donc le double compte par affirmation, mais convertissait seulement une fraction des interactions outil/recherche en continuations de modèle. Elle sous-estimait possiblement les reprises après les outils.

La différence est ainsi principalement une différence d’**unité de comptage**, non la découverte d’une mesure énergétique nouvelle : affirmation individuelle lourde (ancienne méthode) contre batch agentique (méthode finale). Les deux extrêmes sont insuffisants seuls.

## Activité reconstruite — données observées

Le snapshot du journal utilisé lors de l’estimation finale contenait 53 entrées avant les deux entrées d’estimation elle-même : 41 nomment GPT-5 Codex, 3 GPT-5.6 Sol et 9 ne nomment pas de modèle; les entrées de génération déterministe GitHub Actions sont distinguées et ne sont pas converties en inférence de modèle. Il documente 522 affirmations marquées terminées, environ 75 appels ou lots de recherche et 548 autres appels d’outils, soit 623 interactions auxiliaires. Les compteurs d’outils sont approximatifs et les tokens sont tous `null`.

La reconstitution ramène ces lignes à **50 batches substantiels** (traitement d’affirmations, nettoyage, résolution des sources ou cohérence). Ce n’est pas un nombre mesuré d’inférences. En particulier, 623 interactions outil/recherche ne permettent pas de savoir combien de continuations modèle ont eu lieu : plusieurs appels peuvent être lancés dans un même tour, et un résultat peut déclencher zéro, une ou plusieurs reprises.

## Trois méthodes comparées

| Méthode | Hypothèse | Résultat |
|---|---|---:|
| A — approximation intermédiaire par affirmation | 415 × 4,32 Wh × 1,5; une requête très lourde par affirmation | **2,7 kWh** |
| B — batches agentiques, version précédente | 50 × 2 × 3,91 Wh + 187 × 0,31 Wh | **0,45 kWh** |
| C — réconciliation retenue | 50 × 2 × 3,91 Wh + 312 continuations plausibles × 1,0 Wh | **0,70 kWh** |

La méthode C conserve le regroupement empirique des affirmations, mais ajoute explicitement une continuation de coordination pour environ la moitié des interactions outil/recherche. Le facteur 50 % et 1,0 Wh par continuation sont des hypothèses de réconciliation, pas des données mesurées; 1,0 Wh se situe entre la requête médiane de 0,31 Wh et le scénario de raisonnement long de 3,91 Wh d’Oviedo et al.

## Intervalle

| Scénario | Calcul reproductible | Résultat |
|---|---:|---:|
| Bas | 50 × 1 × 1,5 Wh + 62 × 0,16 Wh | 0,085 kWh → **0,1 kWh** |
| Central (C) | 50 × 2 × 3,91 Wh + 312 × 1,0 Wh | 0,703 kWh → **0,7 kWh** |
| Haut plausible | 50 × 5 × 7,05 Wh + 623 × 3,6 Wh | 4,005 kWh → **4 kWh** |

La borne haute suppose que chaque interaction auxiliaire documentée entraîne une reprise substantielle, avec un contexte plus coûteux qu’une requête médiane mais inférieur au scénario long de 3,91 Wh; elle est conservatrice sans être un maximum physique. Elle englobe donc une part substantielle de l’ancienne estimation de 2,7 kWh. L’ancienne valeur n’est pas retenue au centre, car elle multiplie systématiquement une charge de raisonnement long par des affirmations qui étaient souvent traitées collectivement.

## Biais et périmètre

- **Méthode A** : surestime vraisemblablement le nombre de synthèses lourdes indépendantes; elle ignore mutualisation du contexte et les batches.
- **Méthode B** : sous-compte potentiellement les continuations internes des runs agentiques, surtout après les recherches et appels d’outils.
- **Méthode C** : rend ce risque visible mais reste sensible au taux réel de continuations et à leur longueur, inconnus.
- Inclus : inférence IA du travail documenté. Exclus : entraînement, fabrication, terminal utilisateur, réseau, stockage GitHub, recherche/outils exécutés hors modèle et impacts indirects; les outils sont seulement un proxy de continuité afin d’éviter un double compte arbitraire.

## Références

- [Oviedo et al., *Energy Use of AI Inference*](https://arxiv.org/abs/2509.20241) : pour modèles >200B sur nœuds H100, médiane 0,31 Wh par requête (IQR 0,16–0,60) et 3,91 Wh dans un scénario de test-time compute 15× (IQR 2,15–7,05). Estimation bottom-up, pas mesure OpenAI.
- [Elsworth et al., *Measuring the environmental impact of delivering AI at Google scale*](https://services.google.com/fh/files/misc/measuring_the_environmental_impact_of_delivering_ai_at_google_scale.pdf) : mesure de production complète pour Gemini Apps, médiane 0,24 Wh par prompt texte; non transposée directement.
- [Chung et al., *ML.ENERGY Benchmark*](https://proceedings.neurips.cc/paper_files/paper/2025/hash/73750e4e965ab29ac16a4bb38c4c1b9f-Abstract-Datasets_and_Benchmarks_Track.html) : la charge, le batch et le déploiement modifient fortement l’énergie par requête.

Les données de littérature calibrent seulement des ordres de grandeur; les nombres de batches et de continuations sont propres à cette reconstruction et explicitement hypothétiques.
