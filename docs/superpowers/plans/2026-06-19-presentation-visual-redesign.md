# Presentation Visual Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refonte graphique Data Editorial de la présentation ANSSI/CVE, avec icônes Lucide et graphiques Chart.js recolorés.

**Architecture:** Garder le site statique Reveal.js existant. Modifier `index.html` pour charger les polices et Lucide, remplacer les emojis par des icônes `data-lucide`, refondre `theme.css`, puis ajuster les couleurs Chart.js dans les fichiers de charts.

**Tech Stack:** Reveal.js 4.6 CDN, Chart.js 4.4 CDN, Lucide Icons CDN, HTML/CSS/vanilla JS.

---

### Task 1: HTML Shell And Icons

**Files:**
- Modify: `presentation/index.html`
- Modify: `presentation/js/main.js`

- [ ] Add Inter and JetBrains Mono font links.
- [ ] Add Lucide UMD CDN before `main.js`.
- [ ] Replace emoji icon nodes in the pipeline slide with `<i data-lucide="..."></i>`.
- [ ] Call `lucide.createIcons()` on Reveal ready and after slide changes.

### Task 2: Data Editorial Theme

**Files:**
- Modify: `presentation/css/theme.css`

- [ ] Replace the dark theme variables with a light editorial palette.
- [ ] Restyle Reveal slides, headings, subtitles, tables, badges, charts, pipeline blocks, alert blocks and conclusion cards.
- [ ] Add responsive guards for small viewports.
- [ ] Keep card radii at 8px or below for presentation components where possible.

### Task 3: Chart Palette

**Files:**
- Modify: `presentation/js/slide-04.js`
- Modify: `presentation/js/slide-05.js`
- Modify: `presentation/js/slide-06.js`
- Modify: `presentation/js/slide-07.js`

- [ ] Replace dark axis/grid colors with the Data Editorial palette.
- [ ] Use green, yellow, red and blue accents consistently.
- [ ] Keep existing datasets, labels and lazy initialization behavior.

### Task 4: Verification

**Files:**
- Verify: `presentation/index.html`

- [ ] Serve `presentation/` locally with `python3 -m http.server`.
- [ ] Open the presentation and verify the first slide, a pipeline slide, and chart slides.
- [ ] Confirm no emoji icons remain in the HTML.
- [ ] Confirm Lucide icons render.
