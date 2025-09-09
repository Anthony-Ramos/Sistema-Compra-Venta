// static/js/grafi.js
(function () {
  const API_URL = "/api/categorias_grafica";
  const $ = (sel) => document.querySelector(sel);

  let chart, currentType = "bar";
  let ctx, elLoading, elTotalInfo, elTablaWrap;

  // --------- Paleta y helpers (colores vivos para tema claro) ---------
  const PALETTE = [
    "#2563eb","#10b981","#f59e0b","#ef4444","#8b5cf6",
    "#14b8a6","#f97316","#22c55e","#e11d48","#0ea5e9",
    "#a855f7","#06b6d4","#84cc16","#fb7185","#f43f5e"
  ];
  const withAlpha = (hex, a = 0.25) => {
    const r = parseInt(hex.slice(1,3),16);
    const g = parseInt(hex.slice(3,5),16);
    const b = parseInt(hex.slice(5,7),16);
    return `rgba(${r}, ${g}, ${b}, ${a})`;
  };
  const UI = {
    text:  "#111827", // texto oscuro
    grid:  "#e5e7eb", // grilla clara
    border:"#d1d5db"  // bordes suaves
  };

  function showLoading(show) { elLoading.style.display = show ? "flex" : "none"; }

  function changeType(type) {
    currentType = type;
    if (!chart) return;
    const data = chart.data;       // conserva datos
    chart.destroy();
    chart = makeChart(currentType, data);
  }

  function makeChart(type, data) {
    // Asigna colores al dataset (barras/segmentos) desde el inicio
    const bg = data.datasets[0].data.map((_, i) => withAlpha(PALETTE[i % PALETTE.length]));
    const bd = data.datasets[0].data.map((_, i) => PALETTE[i % PALETTE.length]);

    const dataset = {
      ...data.datasets[0],
      backgroundColor: bg,
      borderColor: bd,
      borderWidth: 2,
      hoverBackgroundColor: bd,
      hoverBorderColor: bd
    };

    // Escala Y sugerida según data (evita tope fijo que “aplasta” barras)
    const maxVal = Math.max(0, ...data.datasets[0].data);
    const suggestedMax = maxVal <= 5 ? 5 : Math.ceil(maxVal * 1.2);

    const options = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { 
          display: type !== "bar",
          position: "bottom",
          labels: { color: UI.text }
        },
        tooltip: {
          titleColor: UI.text,
          bodyColor: UI.text,
          borderColor: UI.border,
          borderWidth: 1,
          backgroundColor: "rgba(255,255,255,0.95)"
        }
      },

     scales: type === "bar" ? {
  x: {
    ticks: { color: "#111827" },
    grid:  { color: "#e5e7eb", drawBorder: false }
  },
  y: {
    beginAtZero: true,
    min: 0,
    max: 500,          // 🔹 límite superior fijo
    ticks: {
      color: "#111827",
      stepSize: 100    // 🔹 saltos de 100 en 100
    },
    grid: { color: "#e5e7eb", drawBorder: false }
  }
} : {}
    };

    // Tooltip con porcentaje en dona
    if (type !== "bar") {
      const sum = data.datasets[0].data.reduce((a, b) => a + b, 0) || 1;
      options.plugins.tooltip.callbacks = {
        label: (ctx) => {
          const v = ctx.raw || 0;
          const p = (v * 100 / sum).toFixed(1);
          return `${ctx.label}: ${v} (${p}%)`;
        }
      };
    }

    return new Chart(ctx, { type, data: { labels: data.labels, datasets: [dataset] }, options });
  }

  function buildTable(ids, labels, values) {
    if (!values.length) {
      elTablaWrap.innerHTML = `<div class="empty">No hay datos para mostrar.</div>`;
      elTotalInfo.textContent = "";
      return;
    }
    const total = values.reduce((a, b) => a + b, 0);
    let rows = "";
    labels.forEach((lab, i) => {
      const v = values[i];
      const pct = total ? ((v * 100 / total).toFixed(1) + "%") : "0%";
      rows += `
        <tr>
          <td>#${ids[i]}</td>
          <td>${lab}</td>
          <td style="text-align:right">${v}</td>
          <td style="text-align:right">${pct}</td>
        </tr>`;
    });
    elTablaWrap.innerHTML = `
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Categoría</th>
            <th style="text-align:right">Productos</th>
            <th style="text-align:right">%</th>
          </tr>
        </thead>
        <tbody>${rows}</tbody>
      </table>`;
    elTotalInfo.textContent = `Total productos (todas las categorías): ${total}`;
  }

  async function loadData() {
    try {
      showLoading(true);
      const resp = await fetch(API_URL, { cache: "no-store" });
      if (!resp.ok) throw new Error("HTTP " + resp.status);
      const { ids = [], labels = [], values = [] } = await resp.json();

      const data = { labels, datasets: [{ label: "Productos", data: values }] };

      if (chart) chart.destroy();
      chart = makeChart(currentType, data);
      buildTable(ids, labels, values);
    } catch (err) {
      console.error("Error cargando datos:", err);
      if (chart) { chart.destroy(); chart = null; }
      elTablaWrap.innerHTML = `<div class="empty">Error al cargar los datos. Revisa el endpoint <code>${API_URL}</code>.</div>`;
      elTotalInfo.textContent = "";
    } finally {
      showLoading(false);
    }
  }

  document.addEventListener("DOMContentLoaded", () => {
    elLoading = $("#loading");
    elTotalInfo = $("#totalInfo");
    elTablaWrap = $("#tablaWrap");
    ctx = $("#chart").getContext("2d");

    $("#btnBar").addEventListener("click", () => changeType("bar"));
    $("#btnPie").addEventListener("click", () => changeType("doughnut"));
    $("#btnReload").addEventListener("click", loadData);

    loadData();
  });


})();