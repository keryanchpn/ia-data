window.initSlide07 = function () {
  const ctx = document.getElementById('chart-knn');
  if (!ctx || ctx._chartInstance) return;
  const knn = window.presentationData?.knn;
  if (!knn?.kValues?.length) return;

  const kValues  = knn.kValues;
  const means    = knn.means;
  const stds     = knn.stds;
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
          borderColor: DATA_THEME.blue,
          backgroundColor: 'transparent',
          tension: 0.3,
          pointRadius: kValues.map(k => k === 15 ? 9 : 5),
          pointBackgroundColor: kValues.map(k => k === 15 ? DATA_THEME.green : DATA_THEME.blue),
          borderWidth: 2,
          order: 1,
        },
        {
          label: '+ 1 std',
          data: upper,
          borderColor: 'transparent',
          backgroundColor: 'rgba(37, 99, 235, 0.14)',
          fill: '+1',
          pointRadius: 0,
          order: 2,
        },
        {
          label: '- 1 std',
          data: lower,
          borderColor: 'transparent',
          backgroundColor: 'rgba(37, 99, 235, 0.14)',
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
                return `K=${k} : accuracy ${ctx.raw}`;
              }
              return null;
            }
          }
        }
      },
      scales: {
        x: {
          ticks: { color: DATA_THEME.muted, font: { weight: 600 } },
          grid: { color: DATA_THEME.grid },
          title: { display: true, text: 'Nombre de voisins K', color: DATA_THEME.muted, font: { weight: 700 } }
        },
        y: {
          min: 0.52,
          max: 0.64,
          ticks: { color: DATA_THEME.muted, callback: v => v.toFixed(2), font: { weight: 600 } },
          grid: { color: DATA_THEME.grid },
          title: { display: true, text: 'Accuracy (5-fold CV)', color: DATA_THEME.muted, font: { weight: 700 } }
        }
      }
    }
  });
};
