# Estimation finale de l’énergie d’inférence IA

## Résultat

**Estimation centrale : 0,2 kWh** ; **intervalle plausible : 0,08–0,7 kWh**. Il s’agit d’une estimation attribuable aux interactions d’inférence IA documentées pour ce projet, et non d’une mesure des centres de données ou d’OpenAI.

Rapporté aux 564 affirmations uniques, le point central représente environ **0,35 Wh par affirmation** (fourchette : 0,14–1,24 Wh). Cette division est seulement illustrative : une part notable du travail est transversale (récupération, nettoyage, sources, cohérence et QA).

## Périmètre

Inclus : l’électricité d’inférence associée aux interactions de fact-checking consignées de la reprise initiale à la QA finale. Hors périmètre : entraînement des modèles, fabrication du matériel, poste utilisateur, réseau, stockage GitHub et autres impacts indirects. Les moteurs de recherche et serveurs d’outils sont discutés séparément, mais ne sont pas chiffrés faute de télémétrie.

## A. Métriques directement enregistrées

- 53 entrées dans `metrics/compute_log.jsonl` ; 564 affirmations uniques et 568 occurrences au résultat final.
- Modèles nommés : 41 runs GPT-5 Codex et 3 runs GPT-5.6 Sol ; 9 entrées ne renseignent pas de modèle.
- 522 affirmations « completed » sont explicitement additionnables dans les entrées qui renseignent ce champ ; ce nombre recouvre des passes différentes et n’est **pas** un nombre d’appels IA.
- Environ 75 appels ou lots de recherche web et 548 autres appels d’outils sont consignés.
- `input_tokens`, `output_tokens`, `reasoning_tokens` et `cached_tokens` sont tous indisponibles (`null`) : aucune métrique de token n’est inventée ni convertie.

## B. Quantités reconstruites à partir du journal

Les grandes phases sont : reprise et passe primaire (la majeure partie des runs et des affirmations), préparation et 9 lots de nettoyage, 5 lots de résolution des sources, passe de cohérence ciblée (46 cas), puis QA mécanique. Le journal identifie 53 unités de travail; elles sont plus proches de runs agentiques que de simples prompts, car elles incluent des recherches, des outils et des reprises.

## C. Méthode et scénarios

Deux ancrages indépendants sont utilisés, sans les confondre avec une mesure OpenAI.

1. **Par unité de travail.** Les 53 unités enregistrées ont été réparties entre travail factuel lourd, nettoyage/résolution, cohérence et QA. Les scénarios bas, central et haut correspondent à des services efficacement batchés, à une charge de raisonnement longue plausible, puis à une charge prudente de long contexte et d’itérations. Le résultat est respectivement **0,08, 0,2 et 0,7 kWh**.
2. **Contrôle par requête.** Oviedo et al. estiment, sous hypothèses de service à grande échelle, 0,31 Wh médian par requête pour des modèles >200B (IQR 0,16–0,60 Wh) et 3,91 Wh lorsque le test-time compute est 15× plus long. Google rapporte 0,24 Wh pour le prompt textuel médian de Gemini Apps. Ces valeurs confirment que traiter les unités de ce projet comme de simples prompts moyens sous-estimerait probablement la charge, tandis que les assimiler systématiquement au scénario de raisonnement 15× la surestimerait.

Le point central représente environ quelques dizaines de requêtes équivalentes de raisonnement long ou plusieurs centaines de requêtes textuelles médianes. Ce rapprochement est un contrôle d’ordre de grandeur, pas une mesure de tokens ni une identité entre fournisseurs.

## Recherche, outils et énergie indirecte

Les 75 recherches/lots et 548 autres appels d’outils indiquent une activité auxiliaire substantielle. Mais le journal ne donne ni temps CPU, ni volume transféré, ni infrastructure des fournisseurs : leur consommation ne peut pas être isolée ni ajoutée avec rigueur. L’estimation d’inférence peut déjà inclure une partie de l’orchestration côté fournisseur; additionner un forfait non mesuré créerait un risque de double comptage.

## Références et limites

- [Oviedo et al. (2025), *Energy Use of AI Inference*](https://arxiv.org/abs/2509.20241) : modèle ascendant fondé sur débit de tokens, puissance de nœud, utilisation et PUE ; pertinent pour l’écart entre prompts usuels et raisonnement long, mais non spécifique à OpenAI.
- [Elsworth et al. (Google, 2025)](https://services.google.com/fh/files/misc/measuring_the_environmental_impact_of_delivering_ai_at_google_scale.pdf) : méthodologie de mesure en production couvrant la pile de service ; 0,24 Wh pour le prompt textuel médian Gemini Apps, non transposable tel quel.
- [Chung et al., *ML.ENERGY Benchmark*](https://proceedings.neurips.cc/paper_files/paper/2025/hash/73750e4e965ab29ac16a4bb38c4c1b9f-Abstract-Datasets_and_Benchmarks_Track.html) et [Niu et al., *TokenPowerBench*](https://arxiv.org/abs/2512.03024) : montrent que préremplissage, décodage, contexte, batch, parallélisme et matériel modifient fortement l’énergie.

L’incertitude dominante vient de l’absence de télémétrie de tokens, de modèle/version effectif, de matériel, de batching et de PUE. L’intervalle ne prétend donc pas être une borne physique certaine.

## Illustrations uniquement

0,2 kWh correspond approximativement à une ampoule LED de 10 W allumée pendant 20 heures, ou à une à quelques recharges complètes de smartphone selon le téléphone et les pertes. Ces équivalences ne participent pas au calcul.
