window.initSlide06 = function () {
  const kmeans = window.presentationData?.kmeans;
  if (!kmeans?.silhouette?.length || !kmeans?.elbow?.length) return;

  // ===== Silhouette =====
  const ctxS = document.getElementById('chart-silhouette');
  if (ctxS && !ctxS._chartInstance) {
    ctxS._chartInstance = new Chart(ctxS, {
      type: 'line',
      data: {
        labels: kmeans.silhouette.map((row) => row.k),
        datasets: [{
          label: 'Score de silhouette',
          data: kmeans.silhouette.map((row) => row.score),
          borderColor: DATA_THEME.blue,
          backgroundColor: 'rgba(37, 99, 235, 0.14)',
          tension: 0.3,
          pointRadius: 6,
          pointBackgroundColor: DATA_THEME.blue,
          fill: true,
        }]
      },
      options: {
        maintainAspectRatio: false,
        animation: { duration: 1000 },
        plugins: {
          legend: { display: false },
          tooltip: { callbacks: { label: ctx => `Silhouette : ${ctx.raw}` } }
        },
        scales: {
          x: {
            ticks: { color: DATA_THEME.muted, font: { weight: 600 } },
            grid: { color: DATA_THEME.grid },
            title: { display: true, text: 'Nombre de clusters k', color: DATA_THEME.muted, font: { weight: 700 } }
          },
          y: {
            min: 0.5,
            max: 0.9,
            ticks: { color: DATA_THEME.muted, font: { weight: 600 } },
            grid: { color: DATA_THEME.grid },
            title: { display: true, text: 'Score silhouette', color: DATA_THEME.muted, font: { weight: 700 } }
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
        labels: kmeans.elbow.map((row) => row.k),
        datasets: [{
          label: 'Inertie (WCSS)',
          data: kmeans.elbow.map((row) => row.inertia),
          borderColor: DATA_THEME.yellow,
          backgroundColor: 'rgba(245, 158, 11, 0.16)',
          tension: 0.3,
          pointRadius: 6,
          pointBackgroundColor: (ctx) => ctx.dataIndex === 1 ? DATA_THEME.green : DATA_THEME.yellow,
          pointRadius: (ctx) => ctx.dataIndex === 1 ? 9 : 6,
          fill: true,
        }]
      },
      options: {
        maintainAspectRatio: false,
        animation: { duration: 1000 },
        plugins: {
          legend: { display: false },
          tooltip: { callbacks: { label: ctx => `Inertie : ${ctx.raw.toLocaleString()}` } }
        },
        scales: {
          x: {
            ticks: { color: DATA_THEME.muted, font: { weight: 600 } },
            grid: { color: DATA_THEME.grid },
            title: { display: true, text: 'Nombre de clusters k', color: DATA_THEME.muted, font: { weight: 700 } }
          },
          y: {
            ticks: { color: DATA_THEME.muted, font: { weight: 600 } },
            grid: { color: DATA_THEME.grid },
            title: { display: true, text: 'Inertie (WCSS)', color: DATA_THEME.muted, font: { weight: 700 } }
          }
        }
      }
    });
  }
};
