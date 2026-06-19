// Slides qui ont des charts et leur fonction d'init
// La clé est l'index de la slide (0-based)
const CHART_SLIDES = {
  5:  () => window.initSlide04_filterPies?.(),
  6:  () => window.initSlide04_cvss?.(),
  7:  () => window.initSlide04_epss?.(),
  8:  () => window.initSlide04_vendors?.(),
  9:  () => window.initSlide06?.(),
  10: () => window.initSlide05?.(),
  11: () => window.initSlide07?.(),
};

// Set pour ne déclencher chaque chart qu'une seule fois
const initialized = new Set();

window.presentationDataReady = fetch('data/charts.json')
  .then((response) => {
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    return response.json();
  })
  .then((data) => {
    window.presentationData = data;
    return data;
  })
  .catch((error) => {
    console.error('Impossible de charger data/charts.json', error);
    window.presentationData = null;
    return null;
  });

function refreshIcons() {
  window.lucide?.createIcons({
    attrs: {
      'stroke-width': 2,
      'aria-hidden': 'true',
    },
  });
}

async function initializeChartForSlide(idx) {
  if (!CHART_SLIDES[idx] || initialized.has(idx)) return;
  await window.presentationDataReady;
  if (!window.presentationData) return;
  CHART_SLIDES[idx]();
  initialized.add(idx);
}

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
  refreshIcons();
  const idx = event.indexh;
  // Léger délai pour laisser la transition Reveal se terminer
  setTimeout(() => initializeChartForSlide(idx), 200);
});

// Déclencher aussi au chargement si on arrive directement sur une slide avec chart
Reveal.on('ready', (event) => {
  refreshIcons();
  const idx = event.indexh;
  setTimeout(() => initializeChartForSlide(idx), 200);
});
