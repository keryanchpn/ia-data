window.initSlide05 = function () {
  const ctx = document.getElementById('chart-kmeans');
  if (!ctx || ctx._chartInstance) return;
  const kmeans = window.presentationData?.kmeans;
  if (!kmeans?.points?.length) return;

  function pointsForCluster(cluster) {
    return kmeans.points
      .filter((point) => point.cluster === cluster)
      .map((point) => ({ x: point.x, y: point.y, epss: point.epss }));
  }

  const meanByCluster = new Map((kmeans.clusterMeans || []).map((item) => [item.cluster, item]));
  const labels = [
    'Cluster 0 : Surveiller',
    'Cluster 1 : Patcher',
    'Cluster 2 : Urgence',
  ].map((label, cluster) => {
    const mean = meanByCluster.get(cluster);
    return mean ? `${label} (CVSS ${mean.cvss}, EPSS ${mean.epss})` : label;
  });

  ctx._chartInstance = new Chart(ctx, {
    type: 'scatter',
    data: {
      datasets: [
        {
          label: labels[0],
          data: pointsForCluster(0),
          backgroundColor: 'rgba(37, 99, 235, 0.62)',
          pointRadius: 4,
        },
        {
          label: labels[1],
          data: pointsForCluster(1),
          backgroundColor: 'rgba(245, 158, 11, 0.66)',
          pointRadius: 4,
        },
        {
          label: labels[2],
          data: pointsForCluster(2),
          backgroundColor: 'rgba(220, 38, 38, 0.68)',
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
              const epss = Number(ctx.raw.epss ?? Math.pow(10, ctx.raw.y)).toFixed(4);
              return `CVSS ${ctx.raw.x.toFixed(1)} : EPSS ${epss}`;
            }
          }
        }
      },
      scales: {
        x: {
          min: 0, max: 10,
          ticks: { color: DATA_THEME.muted, font: { weight: 600 } },
          grid: { color: DATA_THEME.grid },
          title: { display: true, text: 'Score CVSS', color: DATA_THEME.muted, font: { weight: 700 } }
        },
        y: {
          ticks: {
            color: DATA_THEME.muted,
            font: { weight: 600 },
            callback: (val) => `10^${val}`
          },
          grid: { color: DATA_THEME.grid },
          title: { display: true, text: 'Score EPSS (échelle log)', color: DATA_THEME.muted, font: { weight: 700 } }
        }
      }
    }
  });
};
