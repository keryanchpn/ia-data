# Presentation Data Export Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Generer un JSON statique depuis le CSV consolide et l'utiliser comme source unique des graphiques de presentation.

**Architecture:** `scripts/export_presentation_data.py` calcule les agregats avec pandas/scikit-learn puis ecrit `presentation/data/charts.json`. `presentation/js/main.js` charge ce JSON au demarrage et les fichiers `slide-XX.js` lisent `window.presentationData`.

**Tech Stack:** Python, pandas, scikit-learn, Reveal.js, Chart.js, vanilla JS.

---

### Task 1: Export Contract Test

**Files:**
- Create: `tests/test_presentation_data_export.py`

- [ ] Tester qu'un petit CSV produit un JSON avec les cles necessaires et des donnees derivees du CSV.

### Task 2: Export Script

**Files:**
- Create: `scripts/export_presentation_data.py`

- [ ] Implementer le calcul des distributions, top editeurs, KMeans et KNN.
- [ ] Ajouter une CLI avec chemins input/output configurables.

### Task 3: Presentation Runtime

**Files:**
- Modify: `presentation/js/main.js`
- Modify: `presentation/js/slide-04.js`
- Modify: `presentation/js/slide-05.js`
- Modify: `presentation/js/slide-06.js`
- Modify: `presentation/js/slide-07.js`

- [ ] Charger `data/charts.json` avant d'initialiser les charts.
- [ ] Remplacer les datasets hardcodes par les donnees JSON.

### Task 4: Generate And Verify

**Files:**
- Create: `presentation/data/charts.json`

- [ ] Generer le JSON depuis `data/vulnerabilites_anssi.csv`.
- [ ] Verifier tests, syntaxe JS et rendu navigateur.
