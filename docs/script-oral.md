# Script oral — Analyse ANSSI/CVE (10 min)

---

## PARTIE 1 — Contexte & pipeline (~3 min)

---

**[Slide 0 — Contexte]**

Bonjour. On va vous présenter un projet de data science appliqué à la cybersécurité, construit autour des bulletins de l'ANSSI.

L'ANSSI — l'Agence Nationale de la Sécurité des Systèmes d'Information — publie chaque jour des avis et des alertes sur des vulnérabilités logicielles. Le problème, c'est que ces données sont éparpillées sur quatre sources différentes : un flux RSS, une API JSON ANSSI, l'API MITRE pour les détails techniques, et l'API FIRST pour les scores d'exploitation.

Notre question centrale : comment transformer cette veille brute en données structurées, analysables, et actionnables ? C'est le pipeline qu'on vous présente aujourd'hui.

---

**[Slide 1 — Architecture du pipeline]**

Le pipeline suit quatre étapes enchaînées.

D'abord `rss_extraction.py` lit les flux RSS de l'ANSSI — avis et alertes — pour récupérer les bulletins disponibles.

Ensuite `cve_extraction.py` va chercher le JSON détaillé de chaque bulletin et en extrait les identifiants CVE, avec une regex en complément pour ne rien manquer.

`cve_enrichment.py` enrichit chaque CVE en interrogeant MITRE pour le score CVSS et la CWE, et FIRST pour le score EPSS.

Enfin `consolidation.py` assemble tout ça dans un CSV de 284 000 lignes.

---

**[Slide 2 — Pourquoi ces choix ?]**

On a fait quatre choix techniques qui méritent d'être expliqués.

Le **cache JSON local** : avec plus de 37 000 CVE à enrichir, on ne peut pas se permettre de rappeler les APIs à chaque exécution. Le cache évite ça et résiste aux pannes réseau.

L'**écriture incrémentale en .tmp** : le pipeline peut durer plusieurs heures. On écrit ligne par ligne dans un fichier temporaire avec flush immédiat — si la machine plante à l'heure 3, on ne perd rien.

Le **mode fallback** : pour travailler et tester sans accès réseau, on peut tout faire tourner sur des données pré-téléchargées localement. C'est d'ailleurs ce mode qu'on a utilisé pour générer toutes les données présentées aujourd'hui — les APIs ANSSI, MITRE et FIRST ont été interrogées en amont, et les réponses stockées dans `data_fallback/`.

Et le modèle de données : **1 ligne = 1 combinaison bulletin × CVE × produit**. Ça permet des agrégations pandas directes, sans jointures complexes.

---

## PARTIE 2 — Données & visualisations (~3 min 30)

---

**[Slide 3 — Qualité des données brutes]**

Toutes les statistiques et graphiques qui suivent sont issus de ce dataset fallback — 284 000 lignes générées hors réseau, représentatives de 4 103 bulletins ANSSI.

Avant d'analyser quoi que ce soit, on a fait un état des lieux de la qualité des données.

Résultat : 51 % des CVE n'ont pas de score CVSS renseigné — parce que les CNA, les organismes qui attribuent les CVE, ne remplissent pas systématiquement ce champ. 63,5 % n'ont pas de CWE disponible. Et 0,5 % manquent de score EPSS — des CVE trop récentes que FIRST n'a pas encore indexées.

---

**[Slide 4 — Choix de filtrage]**

Face à ces valeurs manquantes, on a eu une approche chirurgicale : on ne nettoie pas pour nettoyer, on filtre là où c'est nécessaire.

Pour le CVSS manquant : on a créé un sous-dataset `df_cvss` utilisé uniquement pour les analyses qui en ont besoin. Filtrer globalement aurait fait disparaître la moitié du corpus pour rien.

Pour les CWE "Non disponible" : on les a exclues uniquement du modèle ML et du graphique CWE. Pourquoi ? Parce que le `LabelEncoder` de scikit-learn les encodait comme une vraie CWE, ce qui polluait les features.

Pour la classe NONE de sévérité : 11 exemples seulement dans tout le dataset — pas suffisant pour être apprise par un modèle.

---

**[Slide 5 — Répartitions après filtrage]**

Ces deux graphiques montrent concrètement l'effet de nos filtres. À gauche, la distribution des sévérités CVSS sur les lignes qui ont un score — on voit que HIGH domine à 54 %, MEDIUM à 37 %. À droite, les CWE les plus fréquentes une fois les "Non disponible" exclus.

C'est exactement pour ça que les filtres sont ciblés : ces vues seraient impossibles ou trompeuses avec un filtre global.

---

**[Slide 6 — Distribution CVSS]**

Sur la distribution CVSS, ce qui frappe c'est le pic à 7,5. La moyenne est à 6,9, la médiane à 7,5. Ce n'est pas un hasard : l'ANSSI ne publie pas sur des vulnérabilités anodines. Les scores bas sont quasi absents du corpus.

---

**[Slide 7 — Distribution EPSS]**

Pour l'EPSS c'est l'inverse : la distribution est extrêmement concentrée près de zéro. À gauche, l'échelle linéaire — on ne voit rien, 98 % des points sont écrasés sur le bord gauche.

À droite, l'échelle logarithmique révèle la structure réelle : la médiane est à 0,00048. Seulement 1,09 % des CVE dépassent le seuil de 0,5 — c'est ce seuil qu'on utilisera pour les alertes.

---

**[Slide 8 — Top éditeurs]**

Sur les éditeurs, Microsoft arrive en tête, suivi de Google, Apple, Qualcomm, Samsung. Ce sont les acteurs dont les produits sont les plus représentés dans les bulletins ANSSI — ce qui reflète leur part de marché et la surface d'attaque qu'ils représentent.

---

## PARTIE 3 — Machine Learning & conclusion (~3 min 30)

---

**[Slide 9 — Elbow + Silhouette]**

Pour le clustering, on a appliqué KMeans — qu'on a vu en TD2 — sur les scores CVSS et EPSS. La question c'est : combien de clusters ?

On a utilisé deux méthodes en parallèle. Le score de silhouette, à gauche, est maximisé à k=2 avec un score de 0,835. Mais k=2 ne donne que deux groupes : "dangereux" et "moins dangereux" — ça ne nous apprend rien.

La méthode elbow, à droite, montre un coude net à k=3. On a choisi k=3 parce que ça correspond à trois profils de risque interprétables et actionnables.

---

**[Slide 10 — KMeans scatter]**

Voilà ces trois profils.

Le **cluster 0** en bleu : CVSS moyen 4,9, EPSS 0,003. Des failles modérées, peu susceptibles d'être exploitées. On les surveille.

Le **cluster 1** en orange : CVSS 7,8, EPSS 0,010. Des failles graves mais pas encore exploitées activement. Il faut patcher.

Le **cluster 2** en vert : CVSS 8,4 et surtout EPSS 0,754. Ces failles sont graves ET ont une forte probabilité d'exploitation imminente. C'est l'urgence.

---

**[Slide 11 — KNN cross-val]**

Pour la partie supervisée, l'objectif est de prédire la sévérité d'une CVE avant que MITRE lui attribue un score CVSS — utile pour les 51 % sans score.

On a utilisé KNN — vu en TD3 — avec une validation croisée stratifiée à 5 folds. Stratifiée parce que les classes sont déséquilibrées : 54 % HIGH, 37 % MEDIUM. Un KFold classique concentrerait toutes les CRITICAL dans un seul fold.

La courbe montre que l'accuracy progresse régulièrement de K=1 à K=15. On retient K=15 avec une accuracy de 61,1 %.

---

**[Slide 12 — KNN résultats]**

Les résultats sont honnêtes. HIGH et MEDIUM sont bien prédits — F1 de 0,67 et 0,60 — parce que ce sont les classes majoritaires avec suffisamment de signal.

CRITICAL et LOW sont mal prédits — F1 de 0,17 et 0,06. CRITICAL est souvent confondu avec HIGH, et LOW est absorbé par MEDIUM. Avec seulement deux features — EPSS et CWE — on ne peut pas discriminer les extrêmes de sévérité. Le modèle reste utile comme premier filtre.

---

**[Slide 13 — Alertes]**

Le dernier module c'est `alerting.py`. Il envoie des mails personnalisés par produit suivi, déclenché quand CVSS ≥ 9 ou EPSS ≥ 0,5.

Ce qui est intéressant : le cluster 2 du KMeans a un EPSS moyen de 0,754. Ces deux seuils isolent exactement ce cluster. Le clustering ne fait pas que de l'analyse — il valide rétrospectivement nos choix métier.

---

**[Slide 14 — Conclusion]**

Pour conclure, trois chiffres.

**37 287 CVE** traitées sur 4 103 bulletins ANSSI.

**k=3 clusters**, dont un cluster urgence avec un EPSS moyen de 0,754 — directement exploitable pour prioriser les actions.

**60,5 % d'accuracy** sur KNN — pas parfait, mais utile comme premier filtre avant l'attribution officielle d'un score CVSS.

La piste d'amélioration principale : enrichir les features avec le type de bulletin, l'éditeur, ou l'historique de la CVE. Avec ces informations supplémentaires, les modèles gagneraient significativement en précision.

Merci.

---

## Timing estimé

| Partie | Slides | Durée |
|---|---|---|
| Partie 1 — Contexte + Pipeline | 0 → 2 | ~3 min |
| Partie 2 — Données + Visualisations | 3 → 8 | ~3 min 30 |
| Partie 3 — ML + Conclusion | 9 → 14 | ~3 min 30 |
