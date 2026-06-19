# Glossaire — TD Final IA & Data (SUPDEVINCI 2026)

Mémo de tous les termes techniques rencontrés dans le projet ANSSI/CVE.

---

## Sécurité & données

### CVE — Common Vulnerabilities and Exposures
Identifiant unique et mondial d'une vulnérabilité logicielle.
Format : `CVE-ANNÉE-NUMÉRO` (ex : `CVE-2022-45143`).
Attribué par un **CNA**, maintenu par **MITRE**.

### CVSS — Common Vulnerability Scoring System
Score de **gravité intrinsèque** d'une vulnérabilité, de 0 à 10.
Mesure l'impact théorique si la faille est exploitée (vecteur d'attaque, complexité, privilèges requis, impact CIA).

| Score | Sévérité (`base_severity`) |
|---|---|
| 0.0 | NONE |
| 0.1 – 3.9 | LOW |
| 4.0 – 6.9 | MEDIUM |
| 7.0 – 8.9 | HIGH |
| 9.0 – 10.0 | CRITICAL |

Existe en plusieurs versions : CVSSv2, CVSSv3.0, CVSSv3.1, CVSSv4.0.
**Ne mesure pas** la probabilité d'exploitation réelle → voir EPSS.

### EPSS — Exploit Prediction Scoring System
Probabilité qu'une CVE soit **activement exploitée dans les 30 prochains jours**, entre 0 et 1.
Calculé par un modèle ML entraîné sur des données de threat intelligence (FIRST).
Complémentaire au CVSS : une CVE peut avoir un CVSS élevé mais un EPSS très bas.

Dans notre corpus : médiane **0.00048**, seuil d'alerte à **0.5** (1.09 % des CVE).

### CWE — Common Weakness Enumeration
Classification du **type de faiblesse** à l'origine d'une vulnérabilité.
Format : `CWE-N` (ex : `CWE-79` = Cross-site Scripting, `CWE-78` = OS Command Injection).
C'est le "pourquoi" de la faille — indépendant du produit ou de l'éditeur.

### ANSSI — Agence Nationale de la Sécurité des Systèmes d'Information
Autorité française de cybersécurité. Son CERT (CERT-FR) publie deux types de bulletins :

| Type | Signification |
|---|---|
| **Avis** | Vulnérabilité connue, correctif disponible |
| **Alerte** | Exploitation active confirmée, urgence maximale |

### MITRE
Organisation américaine qui maintient CVE, CWE et d'autres standards de sécurité.
Fournit l'API utilisée pour enrichir chaque CVE (CVSS, CWE, produits affectés).

### FIRST
Forum of Incident Response and Security Teams — consortium international de CERT.
Fournit l'API EPSS.

### CNA — CVE Numbering Authority
Organisme habilité à attribuer des numéros CVE (ex : Microsoft, Google, Qualcomm).
Quand un CNA ne renseigne pas le CVSS, la valeur est absente → explique les 51 % manquants.

### ADP — Authorized Data Publisher
Organisme tiers (ex : CISA) autorisé à enrichir un enregistrement CVE que le CNA n'a pas complété.
Le pipeline fait un fallback sur les ADP pour récupérer des scores CVSS supplémentaires.

### RSS — Really Simple Syndication
Format de flux web utilisé par l'ANSSI pour publier ses bulletins.
Le pipeline lit `https://www.cert.ssi.gouv.fr/avis/feed/` et `.../alerte/feed/`.

---

## Machine Learning

### Apprentissage supervisé
Le modèle apprend à partir d'exemples **étiquetés** (entrée + sortie connue).
Dans le projet : prédire `base_severity` (LOW/MEDIUM/HIGH/CRITICAL) à partir de EPSS + CWE.

### Apprentissage non supervisé
Le modèle découvre une structure dans des données **sans étiquettes**.
Dans le projet : regrouper les CVE par profil de risque avec KMeans.

### KNN — K-Nearest Neighbors
Algorithme de classification supervisée vu en **TD3**.
Pour classer un point, il regarde les K voisins les plus proches et vote à la majorité.
- K impair recommandé pour éviter les égalités
- Meilleur K sélectionné par **validation croisée** (K=15 dans le projet)

### KMeans
Algorithme de clustering non supervisé vu en **TD2**.
Partitionne les données en K groupes en minimisant la variance intra-cluster.
Le K optimal est choisi par le **score de silhouette**.

### Score de silhouette
Métrique de qualité d'un clustering, entre -1 et 1.
Mesure à quel point chaque point est proche de son propre cluster vs les autres.
Plus il est proche de 1, meilleure est la séparation. Dans le projet : **0.835** pour k=2.

### Validation croisée (cross-validation)
Technique d'évaluation qui découpe les données en K folds, entraîne sur K-1 et teste sur 1, en rotation.
Donne une estimation plus fiable de la performance que le simple split train/test.

### StratifiedKFold
Variante de la validation croisée qui **préserve la proportion de chaque classe** dans chaque fold.
Indispensable avec des classes déséquilibrées (comme HIGH/MEDIUM/CRITICAL/LOW).
Vu en **TD3 exercice 3**.

### Train/test split
Découpage du jeu de données en un ensemble d'entraînement et un ensemble de test.
Dans le projet : 75 % train, 25 % test, stratifié.

### LabelEncoder
Transforme des valeurs textuelles en entiers pour les rendre utilisables par un modèle ML.
Ex : `HIGH` → 1, `LOW` → 2, `MEDIUM` → 3, `CRITICAL` → 0.

### StandardScaler
Normalise les features en les centrant (moyenne = 0) et en les réduisant (std = 1).
Utilisé avant KMeans car l'algorithme est sensible aux échelles des variables.

---

## Métriques d'évaluation

### Accuracy
Proportion de prédictions correctes sur l'ensemble du jeu de test.
`accuracy = (vrais positifs + vrais négatifs) / total`
**Limite** : trompeuse sur des classes déséquilibrées (un modèle qui prédit toujours HIGH aurait ~50 % d'accuracy).

### Précision (Precision)
Parmi les exemples **prédits** comme appartenant à une classe, combien le sont vraiment.
`precision = VP / (VP + FP)`

### Rappel (Recall)
Parmi les exemples qui **appartiennent réellement** à une classe, combien sont retrouvés.
`recall = VP / (VP + FN)`

### F1-score
Moyenne harmonique de la précision et du rappel.
`F1 = 2 × (precision × recall) / (precision + recall)`
Utile quand les classes sont déséquilibrées — c'est la métrique principale du projet.

### Matrice de confusion
Tableau croisant les classes réelles et prédites.
La diagonale = prédictions correctes. Les hors-diagonale = erreurs.

### classification_report
Fonction scikit-learn qui affiche précision, rappel, F1 et support (nombre d'exemples) pour chaque classe.

---

## Python / Bibliothèques

### pandas — DataFrame
Structure de données tabulaire (lignes × colonnes), équivalent d'un tableur en Python.
Dans le projet : 284 639 lignes × 15 colonnes.

### numpy
Bibliothèque de calcul numérique. Utilisée pour les opérations sur les arrays (log10, clip, logspace...).

### scikit-learn
Bibliothèque ML Python. Fournit KNN, KMeans, StandardScaler, LabelEncoder, métriques, etc.

### seaborn / matplotlib
Bibliothèques de visualisation. seaborn = graphiques statistiques élégants, matplotlib = contrôle bas niveau.

### feedparser
Bibliothèque Python pour lire les flux RSS. Utilisée pour parser les bulletins ANSSI.

### log10 / logspace
Transformation logarithmique en base 10. Utilisée pour étaler la distribution EPSS très concentrée près de zéro.
`np.log10(0.001) = -3`, `np.log10(0.1) = -1`.

---

## Architecture du pipeline

### Cache JSON
Stockage local des réponses API pour éviter les appels réseau répétés.
Structure : `data/cache/anssi/`, `data/cache/mitre/`, `data/cache/epss/`.

### Fallback
Mode de fonctionnement hors-ligne utilisant des fichiers JSON pré-téléchargés dans `data_fallback/`.
Activé avec `--data-source fallback`.

### Pipeline incrémental
Écriture ligne par ligne dans un fichier `.tmp` pendant le traitement, avec flush immédiat.
Permet de reprendre sans tout perdre en cas d'interruption réseau.
