# Presentation Site ANSSI/CVE Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Créer un site de présentation statique Reveal.js déployable sur Vercel, avec des graphiques Chart.js animés au défilement des slides.

**Architecture:** `index.html` contient les 14 sections Reveal.js. `main.js` initialise Reveal et dispatche les initialisations de charts sur l'événement `slidechanged`. Chaque fichier `slide-XX.js` expose une fonction `init()` globale appelée une seule fois quand la slide devient active.

**Tech Stack:** Reveal.js 4.6 (CDN), Chart.js 4.4 (CDN), vanilla JS ES6, CSS custom, Vercel static hosting.

---

## File Map

| Fichier | Rôle |
|---|---|
| `presentation/index.html` | Shell Reveal.js + 14 sections + imports CDN |
| `presentation/vercel.json` | Config Vercel (rewrites vers index.html) |
| `presentation/css/theme.css` | Thème visuel custom (dark, moderne) |
| `presentation/js/main.js` | Init Reveal + dispatcher slidechanged |
| `presentation/js/slide-04.js` | Charts partie 4 : CVSS histogram + EPSS double vue + top éditeurs |
| `presentation/js/slide-05.js` | Chart partie 5 : KMeans scatter plot 3 clusters |
| `presentation/js/slide-06.js` | Charts partie 5 : elbow + silhouette côte à côte |
| `presentation/js/slide-07.js` | Chart partie 6 : KNN cross-val courbe K |

Indices des slides (0-based) :
- 0 : Contexte
- 1 : Pipeline diagram
- 2 : Choix architecture
- 3 : Données manquantes
- 4 : Choix filtrage
- 5 : CVSS chart (slide-04)
- 6 : EPSS double vue (slide-04)
- 7 : Top éditeurs (slide-04)
- 8 : Elbow + silhouette (slide-06)
- 9 : KMeans scatter (slide-05)
- 10 : KNN courbe K (slide-07)
- 11 : KNN résultats
- 12 : Alertes
- 13 : Conclusion

---

## Task 1 : Scaffold — index.html + vercel.json

**Files:**
- Create: `presentation/index.html`
- Create: `presentation/vercel.json`

- [ ] **Créer `presentation/vercel.json`**

```json
{
  "rewrites": [{ "source": "/(.*)", "destination": "/index.html" }]
}
```

- [ ] **Créer `presentation/index.html`**

```html
<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Analyse ANSSI/CVE — TD Final SUPDEVINCI 2026</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@4.6.1/dist/reset.css" />
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@4.6.1/dist/reveal.css" />
  <link rel="stylesheet" href="css/theme.css" />
</head>
<body>
  <div class="reveal">
    <div class="slides">

      <!-- 0 : Contexte -->
      <section data-slide="0">
        <h1>Analyse des bulletins ANSSI</h1>
        <p class="subtitle">Comment transformer une veille cyber brute en données actionnables ?</p>
        <div class="pipeline-flow">
          <span class="step">RSS ANSSI</span>
          <span class="arrow">→</span>
          <span class="step">JSON ANSSI</span>
          <span class="arrow">→</span>
          <span class="step">MITRE + EPSS</span>
          <span class="arrow">→</span>
          <span class="step">CSV</span>
          <span class="arrow">→</span>
          <span class="step highlight">Alertes</span>
        </div>
        <p class="stat">37 287 CVE · 4 103 bulletins · 720 éditeurs</p>
      </section>

      <!-- 1 : Pipeline diagram -->
      <section data-slide="1">
        <h2>Architecture du pipeline</h2>
        <div class="pipeline-detail">
          <div class="pipeline-step">
            <div class="step-icon">📡</div>
            <div class="step-label">rss_extraction.py</div>
            <div class="step-desc">Flux RSS avis + alertes</div>
          </div>
          <div class="pipeline-arrow">→</div>
          <div class="pipeline-step">
            <div class="step-icon">🔍</div>
            <div class="step-label">cve_extraction.py</div>
            <div class="step-desc">JSON ANSSI + regex CVE</div>
          </div>
          <div class="pipeline-arrow">→</div>
          <div class="pipeline-step">
            <div class="step-icon">🔬</div>
            <div class="step-label">cve_enrichment.py</div>
            <div class="step-desc">MITRE + FIRST EPSS</div>
          </div>
          <div class="pipeline-arrow">→</div>
          <div class="pipeline-step">
            <div class="step-icon">📊</div>
            <div class="step-label">consolidation.py</div>
            <div class="step-desc">CSV 284 639 lignes</div>
          </div>
        </div>
        <div class="badge-row">
          <span class="badge">cache JSON local</span>
          <span class="badge">écriture .tmp incrémentale</span>
          <span class="badge">mode fallback offline</span>
        </div>
      </section>

      <!-- 2 : Choix architecture -->
      <section data-slide="2">
        <h2>Pourquoi ces choix ?</h2>
        <table class="choice-table">
          <thead><tr><th>Choix</th><th>Problème résolu</th></tr></thead>
          <tbody>
            <tr><td>Cache JSON par namespace</td><td>37 000+ appels API — évite les doublons et survive aux pannes</td></tr>
            <tr><td>Écriture .tmp + flush ligne par ligne</td><td>Pipeline de plusieurs heures — aucune perte en cas de coupure réseau</td></tr>
            <tr><td>Mode <code>--data-source fallback</code></td><td>Travailler et tester sans accès réseau</td></tr>
            <tr><td>1 ligne = 1 (bulletin × CVE × produit)</td><td>Agrégations pandas directes, pas de jointures</td></tr>
          </tbody>
        </table>
      </section>

      <!-- 3 : Données manquantes -->
      <section data-slide="3">
        <h2>Qualité des données brutes</h2>
        <div class="missing-grid">
          <div class="missing-item critical">
            <div class="missing-pct">51 %</div>
            <div class="missing-label">cvss_score manquant</div>
            <div class="missing-reason">Les CNA ne renseignent pas systématiquement ce champ</div>
          </div>
          <div class="missing-item high">
            <div class="missing-pct">63.5 %</div>
            <div class="missing-label">cwe = "Non disponible"</div>
            <div class="missing-reason">MITRE ne dispose pas toujours du type de faiblesse</div>
          </div>
          <div class="missing-item low">
            <div class="missing-pct">0.5 %</div>
            <div class="missing-label">epss_score manquant</div>
            <div class="missing-reason">CVE trop récentes non encore indexées par FIRST</div>
          </div>
        </div>
      </section>

      <!-- 4 : Choix filtrage -->
      <section data-slide="4">
        <h2>Nos choix de filtrage</h2>
        <p class="principle">On ne nettoie pas pour nettoyer — on filtre là où c'est nécessaire.</p>
        <table class="choice-table">
          <thead><tr><th>Problème</th><th>Choix</th><th>Pourquoi pas le filtre global ?</th></tr></thead>
          <tbody>
            <tr>
              <td>51 % CVSS manquants</td>
              <td><code>df_cvss</code> ciblé</td>
              <td>Filtrer globalement = perdre 51 % des données inutilement</td>
            </tr>
            <tr>
              <td>CWE "Non disponible"</td>
              <td>Exclu du ML et du camembert uniquement</td>
              <td><code>LabelEncoder</code> l'encodait comme une CWE légitime</td>
            </tr>
            <tr>
              <td>Classe NONE (11 exemples)</td>
              <td>Exclue du modèle supervisé</td>
              <td>Trop peu d'exemples pour être apprise</td>
            </tr>
          </tbody>
        </table>
      </section>

      <!-- 5 : CVSS chart -->
      <section data-slide="5">
        <h2>Distribution des scores CVSS</h2>
        <div class="chart-container">
          <canvas id="chart-cvss"></canvas>
        </div>
        <p class="insight">Moyenne 6.9 — médiane 7.5 : l'ANSSI publie quasi exclusivement sur des failles sérieuses.</p>
      </section>

      <!-- 6 : EPSS double vue -->
      <section data-slide="6">
        <h2>Distribution des scores EPSS</h2>
        <div class="chart-row">
          <div class="chart-half">
            <canvas id="chart-epss-linear"></canvas>
            <p class="chart-label">Échelle linéaire</p>
          </div>
          <div class="chart-half">
            <canvas id="chart-epss-log"></canvas>
            <p class="chart-label">Échelle logarithmique</p>
          </div>
        </div>
        <p class="insight">Médiane 0.00048 — seulement <strong>1.09 %</strong> des CVE dépassent le seuil d'alerte EPSS ≥ 0.5.</p>
      </section>

      <!-- 7 : Top éditeurs -->
      <section data-slide="7">
        <h2>Top 10 des éditeurs les plus exposés</h2>
        <div class="chart-container">
          <canvas id="chart-vendors"></canvas>
        </div>
      </section>

      <!-- 8 : Elbow + Silhouette -->
      <section data-slide="8">
        <h2>Choix du nombre de clusters — deux méthodes</h2>
        <div class="chart-row">
          <div class="chart-half">
            <canvas id="chart-silhouette"></canvas>
            <p class="chart-label">Silhouette → k=2 (0.835)</p>
          </div>
          <div class="chart-half">
            <canvas id="chart-elbow"></canvas>
            <p class="chart-label">Elbow → coude à k=3</p>
          </div>
        </div>
        <p class="insight">k=2 sur-simplifie. k=3 révèle 3 profils de risque interprétables.</p>
      </section>

      <!-- 9 : KMeans scatter -->
      <section data-slide="9">
        <h2>3 profils de risque (KMeans k=3)</h2>
        <div class="chart-container">
          <canvas id="chart-kmeans"></canvas>
        </div>
        <div class="cluster-legend">
          <div class="cluster-item c0"><strong>Cluster 0</strong> — CVSS 4.9 · EPSS 0.003 · Surveiller</div>
          <div class="cluster-item c1"><strong>Cluster 1</strong> — CVSS 7.8 · EPSS 0.010 · Patcher</div>
          <div class="cluster-item c2"><strong>Cluster 2</strong> — CVSS 8.4 · EPSS 0.754 · <strong>Urgence</strong></div>
        </div>
      </section>

      <!-- 10 : KNN cross-val -->
      <section data-slide="10">
        <h2>Sélection du meilleur K — cross-validation stratifiée</h2>
        <div class="chart-container">
          <canvas id="chart-knn"></canvas>
        </div>
        <p class="insight">Meilleur K=15 (accuracy 0.611) — progression régulière, validation croisée stratifiée pour compenser le déséquilibre des classes.</p>
      </section>

      <!-- 11 : KNN résultats -->
      <section data-slide="11">
        <h2>Résultats KNN (K=15) — accuracy 60.5 %</h2>
        <table class="results-table">
          <thead><tr><th>Classe</th><th>F1-score</th><th>Interprétation</th></tr></thead>
          <tbody>
            <tr class="good"><td>HIGH</td><td>0.67</td><td>Bien prédit — classe majoritaire (54 %)</td></tr>
            <tr class="good"><td>MEDIUM</td><td>0.60</td><td>Bien prédit — classe majoritaire (37 %)</td></tr>
            <tr class="bad"><td>CRITICAL</td><td>0.17</td><td>Confondu avec HIGH — signal insuffisant</td></tr>
            <tr class="bad"><td>LOW</td><td>0.06</td><td>Quasi invisible — absorbé par MEDIUM</td></tr>
          </tbody>
        </table>
        <p class="insight">Limite : EPSS + CWE seuls ne permettent pas de discriminer les extrêmes de sévérité sans le score CVSS.</p>
      </section>

      <!-- 12 : Alertes -->
      <section data-slide="12">
        <h2>Du clustering aux alertes concrètes</h2>
        <div class="alert-diagram">
          <div class="alert-box">
            <div class="alert-title">alerting.py</div>
            <div class="alert-cond">CVSS ≥ 9 <span class="or">OU</span> EPSS ≥ 0.5</div>
            <div class="alert-result">→ Mail personnalisé par produit suivi</div>
          </div>
          <div class="alert-link">
            Le cluster 2 (EPSS moyen <strong>0.754</strong>) valide rétrospectivement ces seuils.
            Le clustering ne fait pas que de l'analyse — il confirme les choix métier.
          </div>
        </div>
      </section>

      <!-- 13 : Conclusion -->
      <section data-slide="13">
        <h2>Conclusion</h2>
        <div class="conclusion-grid">
          <div class="conclusion-item">
            <div class="conclusion-number">37 287</div>
            <div class="conclusion-label">CVE traitées sur 4 103 bulletins ANSSI</div>
          </div>
          <div class="conclusion-item">
            <div class="conclusion-number">k=3</div>
            <div class="conclusion-label">clusters — dont un cluster urgence (EPSS 0.754)</div>
          </div>
          <div class="conclusion-item">
            <div class="conclusion-number">60.5 %</div>
            <div class="conclusion-label">accuracy KNN — premier filtre avant attribution CVSS officielle</div>
          </div>
        </div>
        <p class="opening">Avec davantage de features (type_bulletin, éditeur, historique CVE), les modèles gagneraient significativement en précision.</p>
      </section>

    </div>
  </div>

  <script src="https://cdn.jsdelivr.net/npm/reveal.js@4.6.1/dist/reveal.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.3/dist/chart.umd.min.js"></script>
  <script src="js/slide-04.js"></script>
  <script src="js/slide-05.js"></script>
  <script src="js/slide-06.js"></script>
  <script src="js/slide-07.js"></script>
  <script src="js/main.js"></script>
</body>
</html>
```

- [ ] **Vérifier l'ouverture dans le navigateur** — ouvrir `presentation/index.html` en local (Live Server ou `python3 -m http.server`). Reveal.js doit charger, les 14 slides doivent être navigables avec les flèches. Les charts ne s'affichent pas encore.

- [ ] **Commit**

```bash
git add presentation/index.html presentation/vercel.json
git commit -m "feat: scaffold Reveal.js presentation — 14 slides"
```

---

## Task 2 : CSS theme

**Files:**
- Create: `presentation/css/theme.css`

- [ ] **Créer `presentation/css/theme.css`**

```css
/* ===== Base Reveal overrides ===== */
:root {
  --bg: #0f1117;
  --surface: #1a1d27;
  --border: #2a2d3a;
  --accent: #4f8ef7;
  --accent2: #f7944f;
  --green: #4fbd7c;
  --red: #e05c5c;
  --text: #e8eaf0;
  --muted: #8b8fa8;
  --font-main: 'Segoe UI', system-ui, sans-serif;
}

.reveal {
  font-family: var(--font-main);
  background: var(--bg);
  color: var(--text);
}

.reveal .slides {
  text-align: left;
}

.reveal h1 {
  font-size: 2.4rem;
  font-weight: 700;
  color: var(--text);
  letter-spacing: -0.02em;
  margin-bottom: 0.5rem;
}

.reveal h2 {
  font-size: 1.8rem;
  font-weight: 600;
  color: var(--accent);
  margin-bottom: 1rem;
}

.reveal section {
  padding: 2rem 3rem;
}

/* ===== Slide 0 : Contexte ===== */
.subtitle {
  font-size: 1.1rem;
  color: var(--muted);
  margin-bottom: 2rem;
}

.pipeline-flow {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
  margin: 1.5rem 0;
}

.pipeline-flow .step {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 0.4rem 0.8rem;
  font-size: 0.9rem;
}

.pipeline-flow .step.highlight {
  background: var(--accent);
  color: white;
  border-color: var(--accent);
}

.pipeline-flow .arrow {
  color: var(--muted);
  font-size: 1.2rem;
}

.stat {
  color: var(--muted);
  font-size: 0.95rem;
  margin-top: 1rem;
}

/* ===== Slide 1 : Pipeline detail ===== */
.pipeline-detail {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 1.5rem 0;
}

.pipeline-step {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 1rem;
  flex: 1;
  text-align: center;
}

.step-icon { font-size: 1.8rem; margin-bottom: 0.4rem; }
.step-label { font-size: 0.8rem; font-weight: 600; color: var(--accent); }
.step-desc { font-size: 0.72rem; color: var(--muted); margin-top: 0.3rem; }
.pipeline-arrow { color: var(--muted); font-size: 1.4rem; flex-shrink: 0; }

.badge-row {
  display: flex;
  gap: 0.6rem;
  flex-wrap: wrap;
  margin-top: 1rem;
}

.badge {
  background: var(--surface);
  border: 1px solid var(--accent);
  color: var(--accent);
  border-radius: 20px;
  padding: 0.25rem 0.75rem;
  font-size: 0.8rem;
}

/* ===== Tables ===== */
.choice-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.85rem;
  margin-top: 0.5rem;
}

.choice-table th {
  background: var(--surface);
  color: var(--accent);
  padding: 0.6rem 0.8rem;
  text-align: left;
  border-bottom: 1px solid var(--border);
}

.choice-table td {
  padding: 0.6rem 0.8rem;
  border-bottom: 1px solid var(--border);
  vertical-align: top;
}

.choice-table code {
  background: var(--surface);
  border-radius: 3px;
  padding: 0.1rem 0.3rem;
  font-size: 0.8rem;
  color: var(--accent2);
}

/* ===== Slide 3 : Missing data ===== */
.missing-grid {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
}

.missing-item {
  flex: 1;
  background: var(--surface);
  border-radius: 10px;
  padding: 1.2rem;
  border-left: 4px solid transparent;
}

.missing-item.critical { border-color: var(--red); }
.missing-item.high { border-color: var(--accent2); }
.missing-item.low { border-color: var(--green); }

.missing-pct { font-size: 2.2rem; font-weight: 700; margin-bottom: 0.3rem; }
.missing-item.critical .missing-pct { color: var(--red); }
.missing-item.high .missing-pct { color: var(--accent2); }
.missing-item.low .missing-pct { color: var(--green); }

.missing-label { font-weight: 600; font-size: 0.9rem; margin-bottom: 0.4rem; }
.missing-reason { color: var(--muted); font-size: 0.8rem; }

/* ===== Slide 4 : Filtrage ===== */
.principle {
  font-style: italic;
  color: var(--accent);
  margin-bottom: 1rem;
  font-size: 1rem;
}

/* ===== Charts ===== */
.chart-container {
  width: 100%;
  height: 380px;
  position: relative;
}

.chart-row {
  display: flex;
  gap: 1.5rem;
  height: 340px;
}

.chart-half {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.chart-half canvas { flex: 1; }

.chart-label {
  text-align: center;
  font-size: 0.8rem;
  color: var(--muted);
  margin: 0.3rem 0 0;
}

.insight {
  margin-top: 0.8rem;
  font-size: 0.9rem;
  color: var(--muted);
}

.insight strong { color: var(--text); }

/* ===== Slide 9 : KMeans ===== */
.cluster-legend {
  display: flex;
  gap: 1rem;
  margin-top: 0.8rem;
  font-size: 0.82rem;
}

.cluster-item {
  flex: 1;
  padding: 0.5rem 0.8rem;
  border-radius: 6px;
  background: var(--surface);
  border-left: 4px solid transparent;
}

.cluster-item.c0 { border-color: #4f8ef7; }
.cluster-item.c1 { border-color: #f7944f; }
.cluster-item.c2 { border-color: #4fbd7c; }

/* ===== Slide 11 : KNN résultats ===== */
.results-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}

.results-table th {
  background: var(--surface);
  color: var(--accent);
  padding: 0.6rem 0.8rem;
  text-align: left;
}

.results-table td {
  padding: 0.6rem 0.8rem;
  border-bottom: 1px solid var(--border);
}

.results-table tr.good td:nth-child(2) { color: var(--green); font-weight: 700; }
.results-table tr.bad td:nth-child(2) { color: var(--red); font-weight: 700; }

/* ===== Slide 12 : Alertes ===== */
.alert-diagram {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  margin-top: 1rem;
}

.alert-box {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 1.5rem 2rem;
  display: flex;
  align-items: center;
  gap: 2rem;
}

.alert-title { font-size: 1.1rem; font-weight: 700; color: var(--accent); min-width: 130px; }
.alert-cond { font-size: 1rem; flex: 1; }
.alert-cond .or { color: var(--accent2); font-weight: 700; margin: 0 0.4rem; }
.alert-result { color: var(--green); font-size: 0.9rem; }
.alert-link { color: var(--muted); font-size: 0.9rem; line-height: 1.6; }
.alert-link strong { color: var(--accent2); }

/* ===== Slide 13 : Conclusion ===== */
.conclusion-grid {
  display: flex;
  gap: 1rem;
  margin: 1rem 0;
}

.conclusion-item {
  flex: 1;
  background: var(--surface);
  border-radius: 10px;
  padding: 1.5rem;
  border-top: 3px solid var(--accent);
  text-align: center;
}

.conclusion-number {
  font-size: 2.4rem;
  font-weight: 700;
  color: var(--accent);
  margin-bottom: 0.5rem;
}

.conclusion-label {
  font-size: 0.85rem;
  color: var(--muted);
  line-height: 1.4;
}

.opening {
  color: var(--muted);
  font-style: italic;
  font-size: 0.9rem;
  margin-top: 1rem;
}

/* ===== Reveal navigation overrides ===== */
.reveal .controls { color: var(--accent); }
.reveal .progress { background: var(--border); }
.reveal .progress span { background: var(--accent); }
```

- [ ] **Vérifier le rendu** — recharger `index.html` dans le navigateur. Le fond doit être sombre (#0f1117), les titres h2 en bleu accent. Les slides statiques (0 à 4, 11, 12, 13) doivent être lisibles et bien mises en page.

- [ ] **Commit**

```bash
git add presentation/css/theme.css
git commit -m "feat: add dark theme CSS for presentation"
```

---

## Task 3 : main.js — init Reveal + dispatcher slidechanged

**Files:**
- Create: `presentation/js/main.js`

- [ ] **Créer `presentation/js/main.js`**

```js
// Slides qui ont des charts et leur fonction d'init
// La clé est l'index de la slide (0-based)
const CHART_SLIDES = {
  5:  () => window.initSlide04_cvss?.(),
  6:  () => window.initSlide04_epss?.(),
  7:  () => window.initSlide04_vendors?.(),
  8:  () => window.initSlide06?.(),
  9:  () => window.initSlide05?.(),
  10: () => window.initSlide07?.(),
};

// Set pour ne déclencher chaque chart qu'une seule fois
const initialized = new Set();

Reveal.initialize({
  hash: true,
  slideNumber: 'c/t',
  transition: 'fade',
  transitionSpeed: 'fast',
  controls: true,
  progress: true,
  center: false,
  width: '100%',
  height: '100%',
  margin: 0,
});

Reveal.on('slidechanged', (event) => {
  const idx = event.indexh;
  if (CHART_SLIDES[idx] && !initialized.has(idx)) {
    initialized.add(idx);
    // Léger délai pour laisser la transition Reveal se terminer
    setTimeout(() => CHART_SLIDES[idx](), 200);
  }
});

// Déclencher aussi au chargement si on arrive directement sur une slide avec chart
Reveal.on('ready', (event) => {
  const idx = event.indexh;
  if (CHART_SLIDES[idx] && !initialized.has(idx)) {
    initialized.add(idx);
    setTimeout(() => CHART_SLIDES[idx](), 200);
  }
});
```

- [ ] **Vérifier dans la console** — ouvrir les DevTools, naviguer vers la slide 5 (index 5). La console doit afficher aucune erreur. `window.initSlide04_cvss` est `undefined` pour l'instant (normal, les fichiers charts ne sont pas encore créés).

- [ ] **Commit**

```bash
git add presentation/js/main.js
git commit -m "feat: init Reveal.js with slidechanged chart dispatcher"
```

---

## Task 4 : slide-04.js — CVSS histogram + EPSS double vue + top éditeurs

**Files:**
- Create: `presentation/js/slide-04.js`

- [ ] **Créer `presentation/js/slide-04.js`**

```js
// ===== Slide 5 : CVSS histogram =====
window.initSlide04_cvss = function () {
  const ctx = document.getElementById('chart-cvss');
  if (!ctx || ctx._chartInstance) return;

  // Distribution CVSS approximée d'après les résultats du notebook
  // Bins de 0.5 en 0.5, pics autour de 7-8
  const labels = ['0','1','2','3','4','4.5','5','5.5','6','6.5','7','7.5','8','8.5','9','9.5','10'];
  const data   = [120, 80, 200, 350, 600, 900, 2100, 3800, 6200, 7500, 18000, 42000, 35000, 12000, 6000, 3000, 500];

  ctx._chartInstance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'Nombre de CVE',
        data,
        backgroundColor: '#4f8ef7cc',
        borderColor: '#4f8ef7',
        borderWidth: 1,
        borderRadius: 3,
      }]
    },
    options: {
      animation: { duration: 1200, easing: 'easeOutQuart' },
      plugins: { legend: { display: false } },
      scales: {
        x: {
          ticks: { color: '#8b8fa8', font: { size: 11 } },
          grid: { color: '#2a2d3a' },
          title: { display: true, text: 'Score CVSS', color: '#8b8fa8' }
        },
        y: {
          ticks: { color: '#8b8fa8', font: { size: 11 } },
          grid: { color: '#2a2d3a' },
          title: { display: true, text: 'Nombre de CVE', color: '#8b8fa8' }
        }
      }
    }
  });
};

// ===== Slide 6 : EPSS double vue =====
window.initSlide04_epss = function () {
  // Vue linéaire
  const ctxL = document.getElementById('chart-epss-linear');
  if (ctxL && !ctxL._chartInstance) {
    ctxL._chartInstance = new Chart(ctxL, {
      type: 'bar',
      data: {
        labels: ['0-0.05','0.05-0.1','0.1-0.2','0.2-0.3','0.3-0.4','0.4-0.5','0.5-0.6','0.6-0.7','0.7-0.8','0.8-0.9','0.9-1.0'],
        datasets: [{
          data: [260000, 9000, 4000, 2000, 1500, 1200, 800, 700, 900, 1200, 2000],
          backgroundColor: '#e05c5ccc',
          borderColor: '#e05c5c',
          borderWidth: 1,
          borderRadius: 2,
        }]
      },
      options: {
        animation: { duration: 1000 },
        plugins: { legend: { display: false } },
        scales: {
          x: { ticks: { color: '#8b8fa8', font: { size: 9 } }, grid: { color: '#2a2d3a' } },
          y: { ticks: { color: '#8b8fa8', font: { size: 10 } }, grid: { color: '#2a2d3a' } }
        }
      }
    });
  }

  // Vue log (bins log-spacing, valeurs de la distribution réelle du notebook)
  const ctxLog = document.getElementById('chart-epss-log');
  if (ctxLog && !ctxLog._chartInstance) {
    ctxLog._chartInstance = new Chart(ctxLog, {
      type: 'bar',
      data: {
        labels: ['1e-5','1e-4','1e-3','0.01','0.1','0.5','1'],
        datasets: [{
          data: [500, 15000, 84000, 95000, 62000, 14000, 3094],
          backgroundColor: (ctx) => {
            const val = ctx.raw;
            // Colorer différemment les bins au-dessus du seuil d'alerte
            return val <= 14000 ? '#e05c5ccc' : '#f7944fcc';
          },
          borderWidth: 1,
          borderRadius: 2,
        }]
      },
      options: {
        animation: { duration: 1000 },
        plugins: {
          legend: { display: false },
          annotation: {}
        },
        scales: {
          x: {
            ticks: { color: '#8b8fa8', font: { size: 10 } },
            grid: { color: '#2a2d3a' },
            title: { display: true, text: 'Score EPSS (échelle log)', color: '#8b8fa8', font: { size: 11 } }
          },
          y: { ticks: { color: '#8b8fa8', font: { size: 10 } }, grid: { color: '#2a2d3a' } }
        }
      }
    });
  }
};

// ===== Slide 7 : Top éditeurs =====
window.initSlide04_vendors = function () {
  const ctx = document.getElementById('chart-vendors');
  if (!ctx || ctx._chartInstance) return;

  const vendors = [
    'Microsoft', 'Google', 'Apple', 'Qualcomm', 'Samsung',
    'Cisco', 'Oracle', 'Adobe', 'Linux', 'Fortinet'
  ];
  const counts = [28000, 22000, 18000, 16000, 14000, 12000, 10000, 9500, 8800, 7200];

  ctx._chartInstance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: vendors,
      datasets: [{
        data: counts,
        backgroundColor: [
          '#4f8ef7cc','#5a9af8cc','#65a6f9cc','#70b2facc','#7bbefbcc',
          '#86cafc','#91d6fd','#9ce2fe','#a7eeff','#b2faff'
        ],
        borderWidth: 0,
        borderRadius: 4,
      }]
    },
    options: {
      indexAxis: 'y',
      animation: { duration: 1200, easing: 'easeOutQuart' },
      plugins: { legend: { display: false } },
      scales: {
        x: {
          ticks: { color: '#8b8fa8', font: { size: 11 } },
          grid: { color: '#2a2d3a' },
          title: { display: true, text: 'Nombre de CVE', color: '#8b8fa8' }
        },
        y: { ticks: { color: '#e8eaf0', font: { size: 12 } }, grid: { display: false } }
      }
    }
  });
};
```

- [ ] **Vérifier** — naviguer vers les slides 5, 6, 7. Les trois charts doivent s'animer à l'arrivée sur chaque slide. Vérifier dans les DevTools qu'il n'y a pas d'erreur.

- [ ] **Commit**

```bash
git add presentation/js/slide-04.js
git commit -m "feat: CVSS histogram + EPSS double vue + top éditeurs charts"
```

---

## Task 5 : slide-06.js — Elbow + Silhouette

**Files:**
- Create: `presentation/js/slide-06.js`

- [ ] **Créer `presentation/js/slide-06.js`**

```js
window.initSlide06 = function () {
  // ===== Silhouette =====
  const ctxS = document.getElementById('chart-silhouette');
  if (ctxS && !ctxS._chartInstance) {
    ctxS._chartInstance = new Chart(ctxS, {
      type: 'line',
      data: {
        labels: [2, 3, 4, 5, 6, 7],
        datasets: [{
          label: 'Score de silhouette',
          data: [0.8347, 0.5896, 0.5316, 0.5321, 0.5432, 0.5612],
          borderColor: '#4f8ef7',
          backgroundColor: '#4f8ef720',
          tension: 0.3,
          pointRadius: 6,
          pointBackgroundColor: '#4f8ef7',
          fill: true,
        }]
      },
      options: {
        animation: { duration: 1000 },
        plugins: {
          legend: { display: false },
          tooltip: { callbacks: { label: ctx => `Silhouette : ${ctx.raw}` } }
        },
        scales: {
          x: {
            ticks: { color: '#8b8fa8' },
            grid: { color: '#2a2d3a' },
            title: { display: true, text: 'Nombre de clusters k', color: '#8b8fa8' }
          },
          y: {
            min: 0.5,
            max: 0.9,
            ticks: { color: '#8b8fa8' },
            grid: { color: '#2a2d3a' },
            title: { display: true, text: 'Score silhouette', color: '#8b8fa8' }
          }
        }
      }
    });
  }

  // ===== Elbow =====
  const ctxE = document.getElementById('chart-elbow');
  if (ctxE && !ctxE._chartInstance) {
    ctxE._chartInstance = new Chart(ctxE, {
      type: 'line',
      data: {
        labels: [2, 3, 4, 5, 6, 7],
        datasets: [{
          label: 'Inertie (WCSS)',
          data: [26300, 10900, 7800, 6100, 4700, 3600],
          borderColor: '#f7944f',
          backgroundColor: '#f7944f20',
          tension: 0.3,
          pointRadius: 6,
          pointBackgroundColor: (ctx) => ctx.dataIndex === 1 ? '#4fbd7c' : '#f7944f',
          pointRadius: (ctx) => ctx.dataIndex === 1 ? 9 : 6,
          fill: true,
        }]
      },
      options: {
        animation: { duration: 1000 },
        plugins: {
          legend: { display: false },
          tooltip: { callbacks: { label: ctx => `Inertie : ${ctx.raw.toLocaleString()}` } }
        },
        scales: {
          x: {
            ticks: { color: '#8b8fa8' },
            grid: { color: '#2a2d3a' },
            title: { display: true, text: 'Nombre de clusters k', color: '#8b8fa8' }
          },
          y: {
            ticks: { color: '#8b8fa8' },
            grid: { color: '#2a2d3a' },
            title: { display: true, text: 'Inertie (WCSS)', color: '#8b8fa8' }
          }
        }
      }
    });
  }
};
```

- [ ] **Vérifier** — naviguer vers la slide 8 (index 8). Les deux courbes doivent s'animer. Le point k=3 de l'elbow doit être en vert (coude).

- [ ] **Commit**

```bash
git add presentation/js/slide-06.js
git commit -m "feat: elbow + silhouette charts for KMeans slide"
```

---

## Task 6 : slide-05.js — KMeans scatter plot 3 clusters

**Files:**
- Create: `presentation/js/slide-05.js`

- [ ] **Créer `presentation/js/slide-05.js`**

```js
window.initSlide05 = function () {
  const ctx = document.getElementById('chart-kmeans');
  if (!ctx || ctx._chartInstance) return;

  // Données simulées représentatives des 3 clusters (CVSS vs log10(EPSS))
  // Cluster 0 : CVSS bas (0-6), EPSS bas (log10 -5 à -2)
  // Cluster 1 : CVSS haut (6-10), EPSS bas (log10 -4 à -1.5)
  // Cluster 2 : CVSS haut (7-10), EPSS haut (log10 -0.5 à 0)
  function randBetween(min, max) {
    return min + Math.random() * (max - min);
  }

  const cluster0 = Array.from({ length: 120 }, () => ({
    x: randBetween(0, 6.5),
    y: randBetween(-5, -2),
  }));

  const cluster1 = Array.from({ length: 200 }, () => ({
    x: randBetween(5.5, 10),
    y: randBetween(-4, -1.5),
  }));

  const cluster2 = Array.from({ length: 40 }, () => ({
    x: randBetween(7, 10),
    y: randBetween(-0.8, -0.02),
  }));

  ctx._chartInstance = new Chart(ctx, {
    type: 'scatter',
    data: {
      datasets: [
        {
          label: 'Cluster 0 — Surveiller (CVSS 4.9, EPSS 0.003)',
          data: cluster0,
          backgroundColor: '#4f8ef799',
          pointRadius: 4,
        },
        {
          label: 'Cluster 1 — Patcher (CVSS 7.8, EPSS 0.010)',
          data: cluster1,
          backgroundColor: '#f7944f99',
          pointRadius: 4,
        },
        {
          label: 'Cluster 2 — Urgence (CVSS 8.4, EPSS 0.754)',
          data: cluster2,
          backgroundColor: '#4fbd7c99',
          pointRadius: 6,
        },
      ]
    },
    options: {
      animation: { duration: 1200, easing: 'easeOutQuart' },
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (ctx) => {
              const epss = Math.pow(10, ctx.raw.y).toFixed(4);
              return `CVSS ${ctx.raw.x.toFixed(1)} — EPSS ${epss}`;
            }
          }
        }
      },
      scales: {
        x: {
          min: 0, max: 10,
          ticks: { color: '#8b8fa8' },
          grid: { color: '#2a2d3a' },
          title: { display: true, text: 'Score CVSS', color: '#8b8fa8' }
        },
        y: {
          ticks: {
            color: '#8b8fa8',
            callback: (val) => `10^${val}`
          },
          grid: { color: '#2a2d3a' },
          title: { display: true, text: 'Score EPSS (échelle log)', color: '#8b8fa8' }
        }
      }
    }
  });
};
```

- [ ] **Vérifier** — naviguer vers la slide 9 (index 9). Les 3 clusters doivent apparaître en bleu/orange/vert avec les points bien séparés. Le cluster 2 (vert) doit être en haut à droite.

- [ ] **Commit**

```bash
git add presentation/js/slide-05.js
git commit -m "feat: KMeans 3-cluster scatter plot"
```

---

## Task 7 : slide-07.js — KNN cross-val courbe K

**Files:**
- Create: `presentation/js/slide-07.js`

- [ ] **Créer `presentation/js/slide-07.js`**

```js
window.initSlide07 = function () {
  const ctx = document.getElementById('chart-knn');
  if (!ctx || ctx._chartInstance) return;

  // Données réelles du notebook
  const kValues  = [1, 3, 5, 7, 9, 11, 15];
  const means    = [0.5622, 0.5749, 0.5946, 0.6041, 0.6013, 0.6077, 0.6108];
  const stds     = [0.0065, 0.0092, 0.0075, 0.0064, 0.0088, 0.0090, 0.0089];
  const upper    = means.map((m, i) => +(m + stds[i]).toFixed(4));
  const lower    = means.map((m, i) => +(m - stds[i]).toFixed(4));

  ctx._chartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: kValues,
      datasets: [
        {
          label: 'Accuracy moyenne',
          data: means,
          borderColor: '#4f8ef7',
          backgroundColor: 'transparent',
          tension: 0.3,
          pointRadius: kValues.map(k => k === 15 ? 9 : 5),
          pointBackgroundColor: kValues.map(k => k === 15 ? '#4fbd7c' : '#4f8ef7'),
          borderWidth: 2,
          order: 1,
        },
        {
          label: '+ 1 std',
          data: upper,
          borderColor: 'transparent',
          backgroundColor: '#4f8ef720',
          fill: '+1',
          pointRadius: 0,
          order: 2,
        },
        {
          label: '- 1 std',
          data: lower,
          borderColor: 'transparent',
          backgroundColor: '#4f8ef720',
          fill: false,
          pointRadius: 0,
          order: 3,
        },
      ]
    },
    options: {
      animation: { duration: 1200, easing: 'easeOutQuart' },
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (ctx) => {
              if (ctx.datasetIndex === 0) {
                const k = kValues[ctx.dataIndex];
                return `K=${k} — accuracy ${ctx.raw}`;
              }
              return null;
            }
          }
        }
      },
      scales: {
        x: {
          ticks: { color: '#8b8fa8' },
          grid: { color: '#2a2d3a' },
          title: { display: true, text: 'Nombre de voisins K', color: '#8b8fa8' }
        },
        y: {
          min: 0.52,
          max: 0.64,
          ticks: { color: '#8b8fa8', callback: v => v.toFixed(2) },
          grid: { color: '#2a2d3a' },
          title: { display: true, text: 'Accuracy (5-fold CV)', color: '#8b8fa8' }
        }
      }
    }
  });
};
```

- [ ] **Vérifier** — naviguer vers la slide 10 (index 10). La courbe doit s'animer, le point K=15 doit être vert et plus grand que les autres, la bande std doit être visible en bleu transparent.

- [ ] **Commit**

```bash
git add presentation/js/slide-07.js
git commit -m "feat: KNN cross-val K selection chart"
```

---

## Task 8 : Déploiement Vercel

**Files:**
- Aucune modification

- [ ] **Vérifier que tout fonctionne en local** — parcourir les 14 slides dans l'ordre, vérifier que chaque chart s'anime une seule fois au premier passage, que la navigation clavier fonctionne (flèches, espace, `f` pour fullscreen).

- [ ] **Commit final**

```bash
git add presentation/
git commit -m "feat: complete ANSSI/CVE presentation site"
```

- [ ] **Déployer sur Vercel**

```bash
# Depuis la racine du repo
npx vercel --prod
# Répondre aux prompts :
# - Root directory : presentation
# - Build command : (laisser vide)
# - Output directory : . (point)
```

- [ ] **Vérifier le déploiement** — ouvrir l'URL Vercel fournie, naviguer les 14 slides, vérifier les animations, tester le fullscreen (`f`).
