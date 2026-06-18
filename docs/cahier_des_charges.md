# Cahier des charges - Projet Data IA ANSSI/CVE

## 1. Objet du cahier des charges

Ce cahier des charges definit les besoins fonctionnels, techniques et organisationnels pour realiser le projet "Analyse des Avis et Alertes ANSSI avec Enrichissement des CVE".

Le produit attendu est une solution Python capable de collecter les bulletins ANSSI/CERT-FR, d'extraire les CVE, d'enrichir les donnees, de produire un jeu de donnees consolide, de realiser des analyses et visualisations, d'integrer des modeles de Machine Learning et de generer des alertes personnalisees.

## 2. Perimetre du projet

### 2.1 Inclus dans le perimetre

- Extraction des flux RSS ANSSI pour les avis et les alertes.
- Recuperation des bulletins detailles au format JSON.
- Extraction des CVE depuis les donnees ANSSI.
- Enrichissement des CVE via MITRE et FIRST EPSS.
- Gestion des donnees manquantes ou heterogenes.
- Consolidation dans un DataFrame pandas.
- Export du jeu de donnees en CSV.
- Analyse exploratoire dans un notebook Jupyter.
- Visualisations pertinentes.
- Modele de Machine Learning supervise.
- Modele de Machine Learning non supervise.
- Validation des modeles.
- Generation d'alertes personnalisees.
- Construction du sujet et du corps d'un email de notification.
- Documentation du projet.

### 2.2 Hors perimetre ou optionnel

- Interface web Django : optionnelle, pour aller plus loin.
- Envoi effectif d'emails : optionnel, mais la generation du contenu d'email est attendue.
- Deploiement en production : non demande.
- Authentification utilisateur : non demandee sauf extension Django.

## 3. Parties prenantes

- Equipe projet : trois etudiant.e.s.
- Enseignant evaluateur.
- Etudiants evaluateurs dans le cadre du peer review.
- Utilisateur cible theorique : analyste cybersecurite ou responsable de veille vulnerabilites.

## 4. Objectifs fonctionnels

### 4.1 Collecter les bulletins ANSSI

La solution doit lire les flux RSS des avis et alertes ANSSI.

Exigences :

- recuperer le titre du bulletin ;
- recuperer la description ;
- recuperer la date de publication ;
- recuperer le lien du bulletin ;
- identifier le type du bulletin : avis ou alerte ;
- conserver l'identifiant ANSSI lorsque disponible dans l'URL ou le contenu.

Critere d'acceptation :

- un script ou module permet de produire une liste structuree de bulletins ANSSI avec les champs minimaux requis.

### 4.2 Recuperer les details JSON des bulletins

La solution doit acceder au JSON detaille d'un bulletin en ajoutant `/json/` a son URL.

Exigences :

- gerer les erreurs HTTP ;
- gerer les JSON incomplets ou invalides ;
- eviter les interruptions globales lorsqu'un bulletin echoue ;
- journaliser les echecs ou les stocker dans une liste d'erreurs.

Critere d'acceptation :

- chaque bulletin valide peut etre associe a son contenu JSON ou a une erreur explicite.

### 4.3 Extraire les CVE

La solution doit identifier les CVE associees a chaque bulletin.

Exigences :

- utiliser prioritairement la cle `cves` du JSON ANSSI lorsqu'elle existe ;
- completer si necessaire par une extraction regex du type `CVE-YYYY-NNNN`;
- dedoublonner les CVE ;
- conserver le lien entre bulletin et CVE.

Critere d'acceptation :

- pour chaque bulletin, la liste des CVE est extraite sans doublons.

### 4.4 Enrichir les CVE via MITRE

La solution doit interroger ou lire les donnees MITRE associees aux CVE.

Champs attendus :

- description ;
- score CVSS si disponible ;
- version de metrique CVSS utilisee si disponible ;
- severite ;
- CWE ;
- description CWE ;
- editeur/vendor ;
- produit ;
- versions affectees.

Exigences :

- gerer les variations de structure : `cvssV3_1`, `cvssV3_0`, autres versions ou absence de score ;
- gerer les CVE sans CWE ;
- gerer les CVE avec plusieurs produits affectes ;
- ne pas bloquer le pipeline sur une CVE incomplete.

Critere d'acceptation :

- les donnees MITRE disponibles sont integrees au DataFrame, les champs absents sont explicites (`Non disponible`, `NaN` ou valeur equivalente documentee).

### 4.5 Enrichir les CVE via FIRST EPSS

La solution doit recuperer le score EPSS d'une CVE.

Exigences :

- stocker le score EPSS ;
- stocker la date EPSS si fournie ;
- gerer l'absence de resultat ;
- convertir le score en valeur numerique exploitable.

Critere d'acceptation :

- les CVE enrichies contiennent un score EPSS numerique lorsque l'information existe.

### 4.6 Consolider les donnees

La solution doit produire un DataFrame pandas consolidant bulletins, CVE et enrichissements.

Colonnes minimales :

- `id_anssi`
- `titre_anssi`
- `type_bulletin`
- `date_publication`
- `lien_bulletin`
- `cve_id`
- `description_cve`
- `cvss_score`
- `cvss_version`
- `base_severity`
- `cwe_id`
- `cwe_description`
- `epss_score`
- `vendor`
- `product`
- `versions_affectees`

Colonnes recommandees :

- `source_mode` : API ou local ;
- `date_collecte` ;
- `is_critical` ;
- `risk_score` ;
- `has_exploit_probability_high` ;
- `extraction_errors`.

Critere d'acceptation :

- un fichier CSV final est genere et peut etre recharge sans perte majeure dans pandas.

### 4.7 Analyser et visualiser

Le notebook doit exploiter le CSV consolide pour produire une analyse claire.

Visualisations minimales recommandees :

- distribution des scores CVSS ;
- repartition des severites ;
- top editeurs les plus affectes ;
- top produits les plus affectes ;
- repartition des CWE ;
- relation CVSS/EPSS en nuage de points ;
- evolution temporelle des bulletins ou CVE ;
- comparaison avis/alertes.

Critere d'acceptation :

- chaque visualisation importante est accompagnee d'une interpretation courte.

### 4.8 Integrer du Machine Learning

La solution doit inclure au moins un modele supervise et un modele non supervise.

Modele supervise possible :

- classification de la severite ;
- prediction d'un niveau de risque ;
- classification critique/non critique.

Modele non supervise possible :

- clustering de CVE ;
- regroupement de produits ou vulnerabilites ;
- reduction de dimension pour visualisation.

Exigences :

- justifier les variables utilisees ;
- separer les donnees d'entrainement et de test lorsque pertinent ;
- utiliser des metriques de validation ;
- expliquer les limites des modeles.

Critere d'acceptation :

- le notebook contient un modele supervise valide et un modele non supervise interprete.

### 4.9 Generer des alertes personnalisees

La solution doit identifier les vulnerabilites prioritaires selon des regles configurables.

Regles possibles :

- `cvss_score >= 9` ;
- `base_severity == "CRITICAL"` ;
- `epss_score >= 0.7` ;
- `type_bulletin == "alerte"` ;
- produit surveille ;
- editeur surveille.

Exigences :

- produire une liste d'alertes ;
- construire un sujet d'email ;
- construire un corps d'email lisible ;
- inclure les informations utiles : CVE, produit, severite, EPSS, lien ANSSI, recommandation.

Critere d'acceptation :

- une fonction retourne des messages d'alerte prets a etre envoyes, meme si l'envoi SMTP reel n'est pas active.

## 5. Exigences techniques

### 5.1 Langage et environnement

- Langage principal : Python.
- Environnement recommande : Python 3.10 ou superieur.
- Execution reproductible via scripts et notebook.

### 5.2 Bibliotheques recommandees

- `feedparser` pour les flux RSS.
- `requests` pour les appels HTTP.
- `pandas` pour la consolidation.
- `numpy` pour les traitements numeriques.
- `matplotlib`, `seaborn` ou `plotly` pour les visualisations.
- `scikit-learn` pour le Machine Learning.
- `jupyter` pour le notebook.

### 5.3 Structure de projet recommandee

```text
.
├── README.md
├── data/
│   ├── raw/
│   │   ├── avis/
│   │   ├── alertes/
│   │   ├── mitre/
│   │   └── first/
│   ├── interim/
│   └── processed/
│       └── cve_anssi_consolide.csv
├── notebooks/
│   └── analyse_anssi_cve.ipynb
├── reports/
│   └── analyse_anssi_cve.html
├── src/
│   ├── collect_anssi.py
│   ├── extract_cves.py
│   ├── enrich_mitre.py
│   ├── enrich_epss.py
│   ├── build_dataset.py
│   ├── alerts.py
│   └── utils.py
├── docs/
│   ├── synthese_projet.md
│   └── cahier_des_charges.md
└── requirements.txt
```

### 5.4 Mode local et mode API

La solution doit si possible separer :

- la logique metier d'extraction et transformation ;
- la source des donnees : fichiers locaux ou API.

Cette separation permet de travailler sur les donnees pre-telechargees sans changer l'approche generale.

### 5.5 Robustesse

La solution doit gerer :

- indisponibilite reseau ;
- timeout HTTP ;
- code HTTP non 200 ;
- CVE absente ou mal formee ;
- champs MITRE manquants ;
- EPSS absent ;
- bulletins sans CVE ;
- multiples produits pour une CVE ;
- doublons.

### 5.6 Usage responsable des API

Exigences :

- ajouter un delai entre requetes, par exemple 2 secondes ;
- eviter de relancer inutilement les memes appels ;
- mettre en cache les reponses lorsque possible ;
- privilegier les donnees locales fournies pour les tests massifs.

## 6. Exigences de qualite

### 6.1 Qualite du code

- code organise en modules ;
- fonctions courtes et nommees clairement ;
- gestion explicite des erreurs ;
- commentaires utiles mais non excessifs ;
- README permettant l'installation et l'execution ;
- absence de secrets dans le depot.

### 6.2 Qualite des donnees

- colonnes documentees ;
- types coherents ;
- doublons controles ;
- valeurs manquantes identifiees ;
- dates parsees ;
- scores numeriques convertis.

### 6.3 Qualite analytique

- graphiques lisibles ;
- titres et axes explicites ;
- interpretation des resultats ;
- choix ML justifies ;
- limites expliquees.

## 7. Livrables

### 7.1 Livrables obligatoires

- Code Python fonctionnel.
- README clair.
- Fichier CSV consolide.
- Notebook Jupyter.
- Export HTML du notebook.
- Partie Machine Learning supervisee.
- Partie Machine Learning non supervisee.
- Generation d'alertes personnalisees.
- Presentation orale.
- Feuille de repartition des contributions de l'equipe.

### 7.2 Livrables recommandes

- Fichier `requirements.txt`.
- Dossier `docs/` avec synthese et cahier des charges.
- Fichier de configuration pour les seuils d'alertes.
- Cache local des appels API.
- Rapport court listant les principaux constats cyber.

## 8. Planning recommande

Compte tenu de l'echeance tres courte du sujet, le planning doit privilegier un livrable fonctionnel avant les extensions.

| Phase | Objectif | Sortie attendue |
|---|---|---|
| 1 | Structurer le depot | dossiers, README, requirements |
| 2 | Collecter avis et alertes | liste de bulletins |
| 3 | Extraire les CVE | table bulletin/CVE |
| 4 | Enrichir MITRE et EPSS | donnees CVE completes |
| 5 | Consolider | CSV final |
| 6 | Analyser | notebook avec visualisations |
| 7 | Modeliser | ML supervise et non supervise |
| 8 | Alerter | messages personnalises |
| 9 | Finaliser | HTML, presentation, verification |

## 9. Repartition d'equipe recommandee

Pour une equipe de trois personnes :

- Membre 1 : collecte ANSSI, extraction CVE, gestion local/API.
- Membre 2 : enrichissement MITRE/EPSS, consolidation CSV, qualite des donnees.
- Membre 3 : notebook, visualisations, Machine Learning, alertes et presentation.

La repartition doit rester collaborative : chaque membre doit pouvoir expliquer le pipeline complet.

## 10. Criteres d'acceptation globaux

Le projet peut etre considere conforme si :

- le code s'execute de bout en bout ;
- le CSV consolide est produit ;
- les CVE sont correctement reliees aux bulletins ANSSI ;
- les champs CVSS, CWE, EPSS et produits sont enrichis lorsque disponibles ;
- les erreurs et donnees manquantes sont gerees ;
- le notebook recharge le CSV et presente des analyses pertinentes ;
- au moins un modele supervise et un modele non supervise sont presents et valides ;
- les alertes personnalisees sont generees ;
- le README explique clairement comment installer et lancer le projet ;
- les livrables demandes sont fournis dans les formats attendus.

## 11. Risques projet

| Risque | Impact | Mesure de reduction |
|---|---|---|
| APIs externes indisponibles | pipeline bloque | mode local et cache |
| Structures JSON variables | erreurs d'extraction | fonctions defensives et tests sur plusieurs cas |
| CVE sans CVSS ou EPSS | donnees incompletes | valeurs manquantes explicites |
| Trop grand nombre de CVE | temps d'execution long | cache, rate limiting, echantillons pour tests |
| Visualisations peu interpretees | perte de points | ajouter commentaires et constats |
| ML artificiel ou non justifie | perte de credibilite | choisir une cible simple et expliquer les limites |
| Envoi email avec secrets | risque securite | ne pas commiter de mot de passe, generation du mail sans envoi obligatoire |

## 12. Definition du succes

Le succes du projet repose sur la capacite a transformer des bulletins ANSSI bruts en un outil analytique exploitable. Le livrable final doit montrer une chaine complete : collecte, enrichissement, consolidation, analyse, Machine Learning et alerting. La priorite doit etre donnee a la fiabilite du pipeline, a la lisibilite du code et a la pertinence des conclusions.
