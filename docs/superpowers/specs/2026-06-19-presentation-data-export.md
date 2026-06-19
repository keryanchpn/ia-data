# Spec - Export JSON des donnees de presentation

Date: 2026-06-19
Scope: remplacer les donnees hardcodees des graphiques Reveal.js par un JSON statique genere depuis le CSV consolide.

## Objectif

Les graphiques de la presentation doivent s'appuyer sur les donnees reelles du pipeline Python, pas sur des tableaux recopies a la main ni sur des points simules.

## Design valide

- Ajouter un script Python `scripts/export_presentation_data.py`.
- Lire `data/vulnerabilites_anssi.csv`.
- Ecrire `presentation/data/charts.json`.
- Exporter uniquement des agregats et echantillons utiles aux graphiques, pas le CSV complet.
- Garder le site statique: Reveal.js charge `data/charts.json` via `fetch()`.
- Garder des bornes de taille raisonnables pour le scatter KMeans en exportant un echantillon stratifie par cluster.

## Donnees exportees

- Distribution CVSS.
- Distribution EPSS lineaire.
- Distribution EPSS logarithmique.
- Top editeurs.
- Scores silhouette et elbow pour KMeans.
- Points KMeans reels echantillonnes avec cluster.
- Moyennes des clusters.
- Resultats KNN par validation croisee.

## Acceptation

- `presentation/data/charts.json` existe et contient les sections attendues.
- Les fichiers Chart.js ne contiennent plus les anciens datasets manuels.
- Le scatter KMeans utilise des points issus du CSV.
- La presentation garde un fallback clair si le JSON ne charge pas.
