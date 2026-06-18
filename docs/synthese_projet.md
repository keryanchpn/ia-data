# Synthese du projet - Analyse des avis et alertes ANSSI avec enrichissement des CVE

## 1. Nature du projet

Le projet consiste a construire une chaine de traitement de donnees de cybersecurite a partir des bulletins publies par le CERT-FR/ANSSI. L'objectif est de collecter les avis et alertes, d'en extraire les CVE, d'enrichir ces vulnerabilites avec des informations externes, puis de produire des analyses, visualisations, modeles de Machine Learning et alertes personnalisees.

Le depot actuel contient principalement le sujet source sous forme de PDF (`Projet_Data_IA_2026_V0.pdf`) et un `README.md` minimal. Il n'existe pas encore de code applicatif, de donnees consolidees, de notebook ou de structure technique.

## 2. Contexte

L'ANSSI publie des bulletins de securite via le CERT-FR afin d'informer les organisations sur les vulnerabilites et les risques en cours. Deux types de bulletins sont au centre du projet :

- Avis de securite : bulletins preventifs contenant des vulnerabilites connues et des recommandations.
- Alertes : bulletins critiques concernant des vulnerabilites activement exploitees et necessitant une reaction rapide.

Ces bulletins mentionnent des identifiants CVE qui permettent de referencer precisement chaque vulnerabilite. Contrairement au NIST/NVD, l'ANSSI ne fournit pas une API analytique complete. Le projet vise donc a automatiser l'extraction, l'enrichissement et l'exploitation de ces donnees.

## 3. Objectifs principaux

Le projet attend la realisation d'un pipeline complet couvrant :

- l'extraction des flux RSS ANSSI pour les avis et les alertes ;
- la recuperation des bulletins detailles au format JSON ;
- l'identification des CVE mentionnees ;
- l'enrichissement des CVE via des API externes, notamment MITRE et FIRST EPSS ;
- la consolidation des donnees dans un DataFrame pandas puis dans un fichier CSV ;
- l'analyse exploratoire et la visualisation des vulnerabilites ;
- l'integration d'une phase de Machine Learning supervisee et non supervisee ;
- la generation d'alertes personnalisees, avec construction de mails de notification ;
- la production de livrables clairs : code, README, CSV, notebook Jupyter et export HTML.

## 4. Donnees et sources attendues

Les sources principales sont :

- flux RSS ANSSI avis : `https://www.cert.ssi.gouv.fr/avis/feed/` ;
- flux RSS ANSSI alertes : `https://www.cert.ssi.gouv.fr/alerte/feed/` ;
- JSON detaille ANSSI, accessible en ajoutant `/json/` a l'URL du bulletin ;
- API MITRE CVE : donnees descriptives, metriques CVSS, types CWE, produits et versions affectes ;
- API FIRST EPSS : probabilite d'exploitation des CVE.

Le sujet precise aussi que des copies locales de donnees pourront etre fournies pour eviter de surcharger les services externes. Le code doit donc idealement supporter deux modes :

- mode en ligne : appels aux flux RSS et API publiques ;
- mode local : lecture de fichiers pre-telecharges dans des repertoires comme `avis/`, `alertes/`, `mitre/` et `first/`.

## 5. Donnees a consolider

- description de la vulnerabilite ;
- score CVSS ;
- severite CVSS ;
- type CWE ;
- score EPSS ;
- editeur/vendor ;
- produit affecte ;
- versions affectees.

Une ligne peut correspondre a une combinaison bulletin/CVE/produit/version. Un meme bulletin peut donc produire plusieurs lignes, parfois des centaines.

## 6. Analyses et visualisations attendues

Le notebook final doit charger le CSV consolide et produire une analyse exploitable. Les visualisations suggerees incluent :

- distribution des scores CVSS ;
- repartition des severites ;
- repartition des types CWE ;
- evolution temporelle du nombre de vulnerabilites ;
- classement des editeurs et produits les plus affectes ;
- relation entre CVSS et EPSS ;
- heatmap de correlation ;
- boxplots des scores par editeur ;
- focus sur certains types CWE ou certains produits ;
- visualisations liees aux modeles de Machine Learning.

L'analyse ne doit pas seulement afficher des graphiques : elle doit formuler des constats, 
Le fichier consolide doit contenir au minimum les champs suivants :

- identifiant du bulletin ANSSI ;
- titre du bulletin ;
- type de bulletin : avis ou alerte ;
- date de publication ;
- lien du bulletin ;
- identifiant CVE ;
- description de la vulnerabilite ;
- score CVSS ;
- severite CVSS ;
- type CWE ;
- score EPSS ;
- editeur/vendor ;
- produit affecte ;
- versions affectees.

Une ligne peut correspondre a une combinaison bulletin/CVE/produit/version. Un meme bulletin peut donc produire plusieurs lignes, parfois des centaines.

## 6. Analyses et visualisations attendues

Le notebook final doit charger le CSV consolide et produire une analyse exploitable. Les visualisations suggerees incluent :

- distribution des scores CVSS ;
- repartition des severites ;
- repartition des types CWE ;
- evolution temporelle du nombre de vulnerabilites ;
- classement des editeurs et produits les plus affectes ;
- relation entre CVSS et EPSS ;
- heatmap de correlation ;
- boxplots des scores par editeur ;
- focus sur certains types CWE ou certains produits ;
- visualisations liees aux modeles de Machine Learning.

L'analyse ne doit pas seulement afficher des graphiques : elle doit formuler des constats, prioriser les risques et expliquer les implications operationnelles.

## 7. Machine Learning

Le projet impose au moins :

- un modele non supervise ;
- un modele supervise ;
- une justification des choix de variables, cibles et algorithmes ;
- une validation des modeles.

Exemples de pistes :

- clustering de vulnerabilites selon CVSS, EPSS, CWE, type de bulletin et produits ;
- reduction de dimension pour visualiser les groupes ;
- classification de la severite ;
- prediction d'un niveau de risque ;
- prediction ou categorisation de l'EPSS.

La partie ML doit etre integree au notebook final et accompagnee de nouvelles visualisations.

## 8. Alertes et notifications

Le projet demande la generation d'alertes personnalisees lorsqu'une vulnerabilite critique concerne des produits suivis. L'envoi reel d'email est optionnel, mais le sujet, le corps du message et la logique de notification doivent etre produits.

Une alerte pertinente peut etre basee sur :

- score CVSS superieur ou egal a 9 ;
- severite critique ;
- score EPSS eleve ;
- bulletin de type alerte ;
- produit ou editeur present dans une liste de surveillance ;
- combinaison de plusieurs criteres de risque.

## 9. Livrables attendus

Les livrables mentionnes dans le sujet sont :

- code Python fonctionnel ;
- README clair et precis ;
- extraction ANSSI ;
- enrichissement via API ;
- consolidation pandas ;
- generation d'alertes ;
- fichier CSV consolide ;
- notebook Jupyter ;
- export HTML du notebook ;
- support de presentation ;
- feuille indiquant les membres de l'equipe et leur ratio de participation.

## 10. Contraintes importantes

- Le travail se fait en equipe de trois personnes.
- Les binomes et travaux solos ne sont pas acceptes.
- Les appels aux ressources externes doivent etre responsables : delais entre requetes, limitation du trafic, usage des donnees locales fournies si disponible.
- Les erreurs et cas incomplets doivent etre geres : CVE sans CVSS, EPSS absent, JSON incomplet, API indisponible, produits multiples.
- Le plagiat ou le partage direct de code entre equipes est explicitement interdit.

## 11. Dates importantes

- Publication du sujet : jeudi 18 juin 2026.
- Constitution des equipes : jeudi 18 juin 2026.
- Depot des livrables : vendredi 19 juin 2026 a 14h30.
- Evaluation par les pairs des presentations : vendredi 19 juin 2026 pendant les presentations.
- Debut de l'evaluation des livrables par les pairs : vendredi 19 juin 2026 a 18h.
- Fin de l'evaluation par les pairs : mardi 23 juin 2026 a 23h.

## 12. Synthese executive

Le projet est un pipeline data complet applique a la cybersecurite. Il combine collecte de donnees, nettoyage, enrichissement, analyse exploratoire, visualisation, Machine Learning et alerting. La difficulte principale n'est pas seulement technique : elle reside dans la robustesse de l'extraction, la qualite du modele de donnees, la gestion des cas incomplets, la pertinence des analyses et la capacite a transformer des donnees de vulnerabilites en priorites actionnables.

Le depot doit maintenant etre structure autour d'un code Python reproductible, d'un CSV consolide, d'un notebook analytique et d'une documentation claire.
