// static/JS/movi.js
(function () {
  "use strict";

  // ========= Utilidades =========
  const $  = (s) => document.querySelector(s);
  const $$ = (s) => document.querySelectorAll(s);

  const money = (v) => {
    const n = parseFloat(v);
    return Number.isFinite(n) ? `$${n.toFixed(2)}` : "$0.00";
  };

  const safe = (v) => (v === null || v === undefined ? "" : String(v));

  const yyyyMM = (isoDate) => {
    if (!isoDate) return "";
    const d = new Date(isoDate);
    if (!isNaN(d)) {
      const y = d.getFullYear();
      const m = String(d.getMonth() + 1).padStart(2, "0");
      return `${y}-${m}`;
    }
    // fallback si viene como "YYYY-MM-DD"
    return String(isoDate).slice(0, 7);
  };

  // ========= Estado =========
  let cache = [];      // movimientos crudos del backend
  let vista = [];      // movimientos filtrados para pintar

  // ========= Inicio =========
  document.addEventListener("DOMContentLoaded", () => {
    const tbody = $("#tabla-movi") || $("#tabla-movimientos");
    if (!tbody) {
      console.error("No se encontró #tabla-movi ni #tabla-movimientos");
      return;
    }
    const endpoint = tbody.dataset.endpoint || "/api/movimientos";

    cargar(endpoint);
    prepararFiltros();
  });

  // ========= Carga + Render =========
  function cargar(endpoint) {
    fetch(endpoint)
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then((data) => {
        if (!Array.isArray(data)) data = [];
        cache = data.map(normalizar);
        vista = [...cache];
        renderTabla(vista);
        actualizarTotales(vista);
        initMesActual();
      })
      .catch((err) => {
        console.error("Error cargando movimientos:", err);
        const tbody = $("#tabla-movi") || $("#tabla-movimientos");
        if (tbody) {
          tbody.innerHTML =
            '<tr><td colspan="9">Error cargando datos. Revisa la consola.</td></tr>';
        }
      });
  }

  function normalizar(m) {
    // Asegura tipos numéricos
    return {
      tipo: safe(m.tipo),                           // 'COMPRA' | 'VENTA'
      fecha: safe(m.fecha),
      id_producto: Number(m.id_producto) || 0,
      producto: safe(m.producto),
      cantidad: Number(m.cantidad) || 0,
      precio_unitario: Number(m.precio_unitario) || 0,
      total_linea: Number(m.total_linea) || 0,
      contraparte: safe(m.contraparte),            // proveedor o usuario
      id_movimiento: Number(m.id_movimiento) || 0,
    };
  }

  function renderTabla(items) {
    const tbody = $("#tabla-movi") || $("#tabla-movimientos");
    if (!tbody) return;

    if (!items.length) {
      tbody.innerHTML =
        '<tr><td colspan="9">No hay movimientos para mostrar.</td></tr>';
      return;
    }

    const frag = document.createDocumentFragment();
    items.forEach((m) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${safe(m.tipo)}</td>
        <td>${safe(m.fecha)}</td>
        <td>${safe(m.id_producto)}</td>
        <td>${safe(m.producto)}</td>
        <td>${safe(m.cantidad)}</td>
        <td>${money(m.precio_unitario)}</td>
        <td>${money(m.total_linea)}</td>
        <td>${safe(m.contraparte)}</td>
        <td>${safe(m.id_movimiento)}</td>
      `;
      frag.appendChild(tr);
    });
    tbody.innerHTML = "";
    tbody.appendChild(frag);
  }

  // ========= Filtros =========
  function prepararFiltros() {
    const mes = $("#filtro-mes-movi");          // <input type="month" id="filtro-mes-movi">
    const tipo = $("#filtro-tipo-movi");        // <select id="filtro-tipo-movi"> (vacío|COMPRA|VENTA)
    const q = $("#filtro-buscar-movi");         // <input type="text" id="filtro-buscar-movi">
    const btn = $("#btn-limpiar-filtros-movi"); // <button id="btn-limpiar-filtros-movi">

    mes && mes.addEventListener("change", aplicarFiltros);
    tipo && tipo.addEventListener("change", aplicarFiltros);
    q && q.addEventListener("input", aplicarFiltros);

    btn &&
      btn.addEventListener("click", () => {
        initMesActual();
        if (tipo) tipo.value = "";
        if (q) q.value = "";
        aplicarFiltros();
      });
  }

  function initMesActual() {
    const mes = $("#filtro-mes-movi");
    if (!mes) return;
    const now = new Date();
    const yyyy = now.getFullYear();
    const mm = String(now.getMonth() + 1).padStart(2, "0");
    mes.value = `${yyyy}-${mm}`;
  }

  function aplicarFiltros() {
    const mes = ($("#filtro-mes-movi") && $("#filtro-mes-movi").value) || "";
    const tipo = ($("#filtro-tipo-movi") && $("#filtro-tipo-movi").value) || "";
    const q = ($("#filtro-buscar-movi") && $("#filtro-buscar-movi").value.trim().toLowerCase()) || "";

    vista = cache.filter((m) => {
      const okMes = mes ? yyyyMM(m.fecha) === mes : true;
      const okTipo = tipo ? m.tipo === tipo : true;
      const txt = `${m.producto} ${m.contraparte}`.toLowerCase();
      const okQ = q ? txt.includes(q) : true;
      return okMes && okTipo && okQ;
    });

    renderTabla(vista);
    actualizarTotales(vista);
  }

  // ========= Totales =========
  function actualizarTotales(items) {
    const tg = $("#total-mes-movi");        // total general del listado filtrado
    const tc = $("#total-compras-movi");    // solo COMPRA
    const tv = $("#total-ventas-movi");     // solo VENTA
    const cnt = $("#conteo-movi");          // cantidad de filas

    const totGen = items.reduce((s, m) => s + (m.total_linea || 0), 0);
    const totCompras = items
      .filter((m) => m.tipo === "COMPRA")
      .reduce((s, m) => s + (m.total_linea || 0), 0);
    const totVentas = items
      .filter((m) => m.tipo === "VENTA")
      .reduce((s, m) => s + (m.total_linea || 0), 0);

    tg && (tg.textContent = money(totGen));
    tc && (tc.textContent = money(totCompras));
    tv && (tv.textContent = money(totVentas));
    cnt && (cnt.textContent = String(items.length));
  }
})();