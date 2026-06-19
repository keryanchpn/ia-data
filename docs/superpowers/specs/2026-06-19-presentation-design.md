# Spec — Présentation projet ANSSI/CVE (10 min)

**Date :** 2026-06-19
**Durée :** 10 minutes
**Équipe :** Baptiste Dandé, Keryan Champion, Nathan Humeau
**Audience :** Interlocuteur expert du domaine (prof)
**Format :** Site statique déployé sur Vercel
**Stack :** Reveal.js + Chart.js (multi-fichiers vanilla, pas de bundler)
**Angle :** Présenter les choix techniques et les résultats obtenus

---

## Structure du projet

```
presentation/
├── index.html          # Reveal.js init + toutes les sections <slide>
├── vercel.json         # config minimale pour servir index.html
├── css/
│   └── theme.css       # thème custom par-dessus Reveal
└── js/
    ├── main.js         # init Reveal, slidechanged dispatcher
    ├── slide-04.js     # Chart.js CVSS + EPSS (double vue)
    ├── slide-05.js     # Chart.js scatter KMeans 3 clusters
    ├── slide-06.js     # Chart.js elbow + silhouette côte à côte
    └── slide-07.js     # Chart.js KNN cross-val courbe K
```

## Conventions techniques

- Chaque fichier `slide-XX.js` exporte une fonction `init()` appelée par `main.js` sur l'événement `slidechanged` de Reveal
- Les animations Chart.js se déclenchent uniquement quand la slide devient active (pas au chargement de la page)
- Reveal.js + Chart.js chargés via CDN (pas de npm, pas de build)
- Navigation : flèches, espace, touche `f` pour fullscreen
- Données : chiffres réels issus du notebook (pas de mock)
- Déploiement : dossier `presentation/` servi directement par Vercel, `vercel.json` minimal

---

## Contenu — 7 parties, 14 slides, 10 min

### Partie 1 — Contexte & problème (1 min, 1 slide)

**Objectif :** poser le problème en une phrase, montrer la complexité des sources.

**Contenu :**
- L'ANSSI publie des bulletins quotidiennement mais les données sont éparpillées sur 4 sources : flux RSS, JSON ANSSI, API MITRE, API FIRST EPSS
- Problème central : comment transformer cette veille brute en données structurées, analysables et actionnables ?

**Slide :** phrase de problème + schéma flux animé (`RSS -> JSON -> MITRE/EPSS -> CSV -> Alertes`)

---

### Partie 2 — Architecture pipeline (1 min 30, 2 slides)

**Objectif :** justifier les choix d'ingénierie du pipeline.

**Choix à présenter :**

| Choix | Pourquoi |
|---|---|
| Cache JSON local par namespace | Evite les appels réseau répétés sur 37 000+ CVE, survive aux pannes API |
| Ecriture incrémentale CSV (.tmp + flush) | Le pipeline peut durer des heures - on ne peut pas tout perdre sur une coupure réseau |
| Mode fallback (`--data-source fallback`) | Permet de travailler et tester sans réseau |
| 1 ligne = 1 (bulletin, CVE, produit) | Permet les agrégations pandas sans jointures complexes |

**Slides :** diagramme pipeline détaillé / tableau des choix

---

### Partie 3 — Choix de filtrage des données (1 min 30, 2 slides)

**Objectif :** montrer qu'on a analysé la qualité des données et filtré de façon chirurgicale.

**Constats chiffrés :**
- 51 % de `cvss_score` manquants (CNA ne renseignent pas systématiquement)
- 63.5 % de `cwe` a "Non disponible"

**Choix et justifications :**

| Problème | Choix | Pourquoi pas l'alternative |
|---|---|---|
| CVSS manquant | `df_cvss` ciblé uniquement sur les cellules qui en ont besoin | Filtrer globalement = perdre 51 % des données inutilement |
| CWE "Non disponible" | Exclu uniquement du modele ML et du camembert CWE | `LabelEncoder` l'encodait comme une CWE légitime, polluait les features |
| Classe NONE (11 exemples) | Exclue du modele supervisé | Trop peu d'exemples pour etre apprise |

**Message clé :** on ne nettoie pas pour nettoyer - on filtre là où c'est nécessaire.

**Slides :** tableau taux de valeurs manquantes / tableau des choix de filtrage

---

### Partie 4 — Ce que les données révèlent (2 min, 3 slides)

**Objectif :** présenter les insights clés, pas les graphiques pour les graphiques.

**Insights :**
1. **CVSS** : moyenne 6.9, médiane 7.5 - l'ANSSI ne publie que sur des failles sérieuses
2. **EPSS** : médiane 0.00048 - double vue linéaire/log, justification du choix log. Seulement 3 094 CVE (1.09 %) dépassent le seuil d'alerte 0.5
3. **Top éditeurs** : qui est le plus exposé dans le corpus

**Choix de visualisation :** log10 sur l'axe EPSS car l'échelle linéaire compresse 98 % des points a zéro.

**Slides :** histogramme CVSS animé / double vue EPSS linéaire+log animée / bar chart top éditeurs animé

**Charts :** Chart.js - `slide-04.js`

---

### Partie 5 — Pourquoi KMeans + elbow (1 min 30, 2 slides)

**Objectif :** justifier le modele non supervisé et le choix de k.

**Choix et justifications :**

| Choix | Pourquoi |
|---|---|
| Apprentissage non supervisé | Pas d'étiquettes "profil de risque" disponibles |
| KMeans | Vu en TD2, simple et interprétable sur 2 features numériques |
| k=3 (elbow) plutot que k=2 (silhouette) | Silhouette maximisée a k=2 (0.835) mais sur-simplifie ; elbow montre un coude net a k=3 |

**Résultats - 3 clusters :**

| Cluster | CVSS moyen | EPSS moyen | Profil | Priorité |
|---|---|---|---|---|
| 0 | 4.9 | 0.003 | Failles modérées, non exploitées | Surveiller |
| 1 | 7.8 | 0.010 | Failles graves, non exploitées | Patcher |
| 2 | 8.4 | 0.754 | Failles graves ET exploitées | Urgence |

**Slides :** double courbe silhouette/elbow animée / scatter plot log 3 clusters animé

**Charts :** Chart.js - `slide-05.js` (scatter), `slide-06.js` (elbow + silhouette)

---

### Partie 6 — Pourquoi KNN + cross-val stratifiée (1 min 30, 2 slides)

**Objectif :** prédire la sévérité sans le score CVSS, justifier les choix méthodologiques.

**Problème :** estimer la sévérité d'une CVE avant que MITRE attribue un score CVSS - utile pour les 51 % sans score.

**Choix et justifications :**

| Choix | Pourquoi |
|---|---|
| KNN | Vu en TD3, interprétable, pas de boite noire |
| Cross-val stratifiée 5 folds | Données déséquilibrées (54 % HIGH, 37 % MEDIUM) - KFold simple concentrerait les CRITICAL dans un seul fold |
| K=15 retenu | Courbe K=1->15 : progression réguliere, pic a K=15 (accuracy 0.611) |
| Features : EPSS + CWE encodé | Seules features disponibles sans le CVSS |

**Résultats honnetes :**
- Accuracy : 60.5 %
- HIGH (F1=0.67) et MEDIUM (F1=0.60) : bien prédits
- CRITICAL (F1=0.17) et LOW (F1=0.06) : mal prédits - signal insuffisant avec 2 features

**Slides :** courbe K vs accuracy animée / classification report visuel

**Charts :** Chart.js - `slide-07.js`

---

### Partie 7 — Alertes & conclusion (1 min, 2 slides)

**Objectif :** montrer le débouché concret et conclure.

**Alertes :**
- `alerting.py` envoie des mails personnalisés par produit suivi
- Déclencheur : `CVSS >= 9` OU `EPSS >= 0.5`
- Lien avec KMeans : ces seuils isolent exactement le cluster 2 (EPSS moyen 0.754) - le clustering valide rétrospectivement les seuils

**Conclusion - 3 chiffres clés :**
- **37 287 CVE** traitées sur 4 103 bulletins ANSSI
- **k=3 clusters** dont un cluster urgence (EPSS 0.754)
- **60.5 % accuracy** KNN - utile comme premier filtre avant attribution CVSS officielle

**Ouverture :** avec davantage de features (type_bulletin, éditeur, historique CVE), les modeles gagneraient significativement en précision.

**Slides :** slide alertes + slide conclusion 3 chiffres

---

## Résumé timing

| # | Partie | Durée | Slides | Charts |
|---|---|---|---|---|
| 1 | Contexte & probleme | 1 min | 1 | - |
| 2 | Architecture pipeline | 1 min 30 | 2 | - |
| 3 | Filtrage des données | 1 min 30 | 2 | - |
| 4 | Ce que les données révèlent | 2 min | 3 | slide-04.js |
| 5 | KMeans + elbow | 1 min 30 | 2 | slide-05.js + slide-06.js |
| 6 | KNN + cross-val stratifiée | 1 min 30 | 2 | slide-07.js |
| 7 | Alertes & conclusion | 1 min | 2 | - |
| **Total** | | **10 min** | **14 slides** | **4 fichiers JS** |
