// ===== Slide 5 : CVSS histogram =====
const DATA_THEME = {
  ink: '#102033',
  muted: '#64748b',
  grid: '#d8e0ea',
  blue: '#2563eb',
  blueFill: 'rgba(37, 99, 235, 0.78)',
  teal: '#0f766e',
  tealFill: 'rgba(15, 118, 110, 0.78)',
  yellow: '#f59e0b',
  yellowFill: 'rgba(245, 158, 11, 0.78)',
  red: '#dc2626',
  redFill: 'rgba(220, 38, 38, 0.78)',
  green: '#16a34a',
};

const PIE_COLORS = [
  '#0f766e',
  '#2563eb',
  '#f59e0b',
  '#dc2626',
  '#7c3aed',
  '#16a34a',
  '#0891b2',
  '#e44b4b',
  '#64748b',
];

function createDoughnutChart(ctx, chartData, title) {
  return new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: chartData.labels,
      datasets: [{
        data: chartData.values,
        backgroundColor: PIE_COLORS,
        borderColor: '#ffffff',
        borderWidth: 2,
        hoverOffset: 8,
      }]
    },
    options: {
      maintainAspectRatio: false,
      cutout: '58%',
      animation: { duration: 1000, easing: 'easeOutQuart' },
      plugins: {
        title: {
          display: true,
          text: title,
          color: DATA_THEME.ink,
          font: { size: 13, weight: 700 },
          padding: { bottom: 10 },
        },
        legend: {
          position: 'right',
          labels: {
            color: DATA_THEME.muted,
            boxWidth: 12,
            boxHeight: 12,
            font: { size: 11, weight: 600 },
          }
        },
        tooltip: {
          callbacks: {
            label: (context) => {
              const total = context.dataset.data.reduce((sum, value) => sum + value, 0);
              const value = context.raw;
              const pct = total ? ((value / total) * 100).toFixed(1) : '0.0';
              return `${context.label} : ${value.toLocaleString('fr-FR')} (${pct} %)`;
            }
          }
        }
      }
    }
  });
}

window.initSlide04_filterPies = function () {
  const data = window.presentationData;
  if (!data?.severityDistribution || !data?.cweDistribution) return;

  const severityCtx = document.getElementById('chart-severity-pie');
  if (severityCtx && !severityCtx._chartInstance) {
    severityCtx._chartInstance = createDoughnutChart(
      severityCtx,
      data.severityDistribution,
      'Répartition CVSS'
    );
  }

  const cweCtx = document.getElementById('chart-cwe-pie');
  if (cweCtx && !cweCtx._chartInstance) {
    cweCtx._chartInstance = createDoughnutChart(
      cweCtx,
      data.cweDistribution,
      'Répartition CWE'
    );
  }
};

window.initSlide04_cvss = function () {
  const ctx = document.getElementById('chart-cvss');
  if (!ctx || ctx._chartInstance) return;
  const chartData = window.presentationData?.cvssDistribution;
  if (!chartData) return;

  ctx._chartInstance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: chartData.labels,
      datasets: [{
        label: 'Nombre de CVE',
        data: chartData.values,
        backgroundColor: DATA_THEME.blueFill,
        borderColor: DATA_THEME.blue,
        borderWidth: 1,
        borderRadius: 5,
      }]
    },
    options: {
      animation: { duration: 1200, easing: 'easeOutQuart' },
      plugins: { legend: { display: false } },
      scales: {
        x: {
          ticks: { color: DATA_THEME.muted, font: { size: 11, weight: 600 } },
          grid: { color: DATA_THEME.grid },
          title: { display: true, text: 'Score CVSS', color: DATA_THEME.muted, font: { weight: 700 } }
        },
        y: {
          ticks: { color: DATA_THEME.muted, font: { size: 11, weight: 600 } },
          grid: { color: DATA_THEME.grid },
          title: { display: true, text: 'Nombre de CVE', color: DATA_THEME.muted, font: { weight: 700 } }
        }
      }
    }
  });
};

// ===== Slide 6 : EPSS double vue =====
window.initSlide04_epss = function () {
  const data = window.presentationData;
  if (!data?.epssLinear || !data?.epssLog) return;

  // Vue linéaire
  const ctxL = document.getElementById('chart-epss-linear');
  if (ctxL && !ctxL._chartInstance) {
    ctxL._chartInstance = new Chart(ctxL, {
      type: 'bar',
      data: {
        labels: data.epssLinear.labels,
        datasets: [{
          data: data.epssLinear.values,
          backgroundColor: DATA_THEME.tealFill,
          borderColor: DATA_THEME.teal,
          borderWidth: 1,
          borderRadius: 5,
        }]
      },
      options: {
        maintainAspectRatio: false,
        animation: { duration: 1000 },
        plugins: { legend: { display: false } },
        scales: {
          x: { ticks: { color: DATA_THEME.muted, font: { size: 9, weight: 600 } }, grid: { color: DATA_THEME.grid } },
          y: { ticks: { color: DATA_THEME.muted, font: { size: 10, weight: 600 } }, grid: { color: DATA_THEME.grid } }
        }
      }
    });
  }

  // Vue log (bins log-spacing exportés depuis le CSV consolidé)
  const ctxLog = document.getElementById('chart-epss-log');
  if (ctxLog && !ctxLog._chartInstance) {
    ctxLog._chartInstance = new Chart(ctxLog, {
      type: 'bar',
      data: {
        labels: data.epssLog.labels,
        datasets: [{
          data: data.epssLog.values,
          backgroundColor: (ctx) => {
            // Colorer différemment les bins au-dessus du seuil d'alerte
            return ctx.dataIndex >= data.epssLog.values.length - 1 ? DATA_THEME.redFill : DATA_THEME.yellowFill;
          },
          borderWidth: 1,
          borderRadius: 5,
        }]
      },
      options: {
        maintainAspectRatio: false,
        animation: { duration: 1000 },
        plugins: {
          legend: { display: false },
          annotation: {}
        },
        scales: {
          x: {
            ticks: { color: DATA_THEME.muted, font: { size: 10, weight: 600 } },
            grid: { color: DATA_THEME.grid },
            title: { display: true, text: 'Score EPSS (échelle log)', color: DATA_THEME.muted, font: { size: 11, weight: 700 } }
          },
          y: { ticks: { color: DATA_THEME.muted, font: { size: 10, weight: 600 } }, grid: { color: DATA_THEME.grid } }
        }
      }
    });
  }
};

// ===== Slide 7 : Top éditeurs =====
window.initSlide04_vendors = function () {
  const ctx = document.getElementById('chart-vendors');
  if (!ctx || ctx._chartInstance) return;
  const chartData = window.presentationData?.topVendors;
  if (!chartData) return;

  ctx._chartInstance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: chartData.labels,
      datasets: [{
        data: chartData.values,
        backgroundColor: [
          '#0f766e', '#16877f', '#2563eb', '#3b74ee', '#f59e0b',
          '#f7ad2d', '#dc2626', '#e44b4b', '#7c3aed', '#8b5cf6'
        ],
        borderWidth: 0,
        borderRadius: 6,
      }]
    },
    options: {
      indexAxis: 'y',
      animation: { duration: 1200, easing: 'easeOutQuart' },
      plugins: { legend: { display: false } },
      scales: {
        x: {
          ticks: { color: DATA_THEME.muted, font: { size: 11, weight: 600 } },
          grid: { color: DATA_THEME.grid },
          title: { display: true, text: 'Nombre de CVE', color: DATA_THEME.muted, font: { weight: 700 } }
        },
        y: { ticks: { color: DATA_THEME.ink, font: { size: 12, weight: 700 } }, grid: { display: false } }
      }
    }
  });
};
