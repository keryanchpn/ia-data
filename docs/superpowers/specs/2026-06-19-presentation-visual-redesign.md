# Spec - Refonte graphique Data Editorial

Date: 2026-06-19
Scope: refonte visuelle du site de présentation Reveal.js existant, sans changer le contenu ni la structure technique globale.

## Direction validée

Le style retenu est "Data Editorial": une présentation claire, premium et moderne, proche d'un rapport exécutif interactif. Le rendu doit être plus sophistiqué que le thème sombre initial, avec une forte lisibilité en soutenance.

## Contraintes

- Garder Reveal.js et Chart.js via CDN.
- Ne pas introduire de bundler ni de dépendance npm.
- Remplacer les icônes emoji par Lucide Icons via CDN (`lucide.dev`).
- Conserver les 14 slides et le contenu existant.
- Recolorer les graphiques pour correspondre au nouveau thème clair.
- Garder une navigation Reveal fonctionnelle et des graphiques initialisés à l'arrivée sur chaque slide.

## Design cible

- Fond clair gris bleuté, texte bleu nuit, surfaces blanches, bordures fines.
- Accents principaux: vert pétrole pour les éléments de données, jaune signal pour les points d'attention, rouge net pour les risques.
- Titres plus grands et plus structurés, avec une hiérarchie typographique éditoriale.
- Cartes et tableaux plus légers, avec ombres subtiles et angles contrôlés.
- Slide d'ouverture plus forte: pipeline, chiffres clés et problème central visibles immédiatement.
- Slides techniques plus aérées: pipeline en modules, badges propres, tableaux lisibles.
- Charts Chart.js cohérents avec la palette claire et lisibles sur projecteur.

## Acceptation

- Aucune icône emoji ne doit rester dans le pipeline.
- `lucide.createIcons()` doit être appelé après le chargement de la page.
- Les slides avec graphiques doivent continuer à s'afficher quand on navigue.
- La page doit s'ouvrir localement via un serveur statique.
