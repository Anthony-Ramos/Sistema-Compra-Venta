// static/js/compras.js
(function () {
  // =======================
  // Estado y utilidades
  // =======================
  let comprasCache = [];        // Últimos datos cargados desde el backend
  let comprasFiltradas = [];    // Vista filtrada para la tabla

  const $  = (sel) => document.querySelector(sel);
  const $$ = (sel) => document.querySelectorAll(sel);

  const money = (v) => {
    const n = parseFloat(v);
    return Number.isFinite(n) ? `$${n.toFixed(2)}` : '$0.00';
  };

  const parseYYYYMM = (isoDate) => {
    // isoDate esperado "YYYY-MM-DD" o "YYYY-MM-DDTHH:mm:ss"
    if (!isoDate) return '';
    const d = new Date(isoDate);
    if (isNaN(d)) {
      // fallback si viene "YYYY-MM-DD"
      return String(isoDate).slice(0, 7);
    }
    const y = d.getFullYear();
    const m = String(d.getMonth() + 1).padStart(2, '0');
    return `${y}-${m}`;
  };

  // =======================
  // Carga inicial
  // =======================
  document.addEventListener("DOMContentLoaded", () => {
    const tbody = $('#tabla-compras'); // <tbody id="tabla-compras" data-endpoint="/api/compras">
    const endpoint = tbody?.dataset.endpoint || "/api/compras";

    cargarCompras(endpoint);
    prepararFiltros();
  });

  // =======================
  // Fetch + Render tabla
  // =======================
  function cargarCompras(endpoint) {
    fetch(endpoint)
      .then(r => {
        if (!r.ok) throw new Error(`Error HTTP: ${r.status}`);
        return r.json();
      })
      .then(data => {
        if (!Array.isArray(data)) data = [];
        comprasCache = data;
        comprasFiltradas = [...comprasCache];

        renderTabla(comprasFiltradas);
        actualizarTotalesLocales(comprasFiltradas);  // total general (si existe el span)
        actualizarTotalMesActual();                  // total del mes (si existe el span)
      })
      .catch(err => {
        console.error("Error cargando compras:", err);
        const tbody = $('#tabla-compras');
        if (tbody) {
          tbody.innerHTML = '<tr><td colspan="7">Error cargando datos. Revisa la consola.</td></tr>';
        }
      });
  }

  function renderTabla(lista) {
    const tbody = $('#tabla-compras');
    if (!tbody) {
      console.error('No se encontró #tabla-compras');
      return;
    }

    tbody.innerHTML = "";

    if (!Array.isArray(lista) || lista.length === 0) {
      tbody.innerHTML = '<tr><td colspan="7">No hay compras registradas</td></tr>';
      return;
    }

    lista.forEach(c => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${safe(c.proveedor)}</td>
        <td>${safe(c.fecha)}</td>
        <td>${safe(c.producto)}</td>
        <td>${safe(c.cantidad)}</td>
        <td>${money(c.precio_unitario)}</td>
        <td>${safe(c.estado)}</td>
        <td>${money(c.total)}</td>
      `;
      tbody.appendChild(tr);
    });
  }

  function safe(v) {
    if (v === null || v === undefined) return '';
    return String(v);
  }

  // =======================
  // Totales (cálculo local)
  // =======================
  function actualizarTotalesLocales(lista) {
    const spanGeneral = $('#total-general-compras');
    if (!spanGeneral) return;

    const total = lista.reduce((acc, c) => acc + (parseFloat(c.total) || 0), 0);
    spanGeneral.textContent = money(total);
  }

  function actualizarTotalMesActual() {
    const spanMes = $('#total-mes-compras');
    const inputMes = $('#filtro-mes-compras');
    if (!spanMes || !inputMes) return;

    const mesSel = inputMes.value; // "YYYY-MM"
    if (!mesSel) {
      spanMes.textContent = '$0.00';
      return;
    }

    const delMes = comprasFiltradas.filter(c => parseYYYYMM(c.fecha) === mesSel);
    const totalMes = delMes.reduce((acc, c) => acc + (parseFloat(c.total) || 0), 0);
    spanMes.textContent = money(totalMes);
  }

  // =======================
  // Filtros (cliente)
  // =======================
  function prepararFiltros() {
    // Filtro por mes (input type="month" id="filtro-mes-compras")
    const inputMes = $('#filtro-mes-compras');
    if (inputMes) {
      // Inicializar al mes actual
      const hoy = new Date();
      const yyyy = hoy.getFullYear();
      const mm = String(hoy.getMonth() + 1).padStart(2, '0');
      inputMes.value = `${yyyy}-${mm}`;

      inputMes.addEventListener('change', () => {
        aplicarFiltros();
        actualizarTotalMesActual();
      });
    }

    // Filtro por proveedor (input text id="filtro-proveedor")
    const inputProv = $('#filtro-proveedor');
    if (inputProv) {
      inputProv.addEventListener('input', () => {
        aplicarFiltros();
        actualizarTotalMesActual();
      });
    }

    // Botón limpiar filtros (opcional)
    const btnLimpiar = $('#btn-limpiar-filtros-compras');
    if (btnLimpiar) {
      btnLimpiar.addEventListener('click', () => {
        if (inputMes) {
          const hoy = new Date();
          const yyyy = hoy.getFullYear();
          const mm = String(hoy.getMonth() + 1).padStart(2, '0');
          inputMes.value = `${yyyy}-${mm}`;
        }
        if (inputProv) inputProv.value = '';
        comprasFiltradas = [...comprasCache];
        renderTabla(comprasFiltradas);
        actualizarTotalesLocales(comprasFiltradas);
        actualizarTotalMesActual();
      });
    }
  }

  function aplicarFiltros() {
    const inputMes = $('#filtro-mes-compras');
    const inputProv = $('#filtro-proveedor');

    const mesSel = inputMes ? inputMes.value : '';
    const provTxt = (inputProv ? inputProv.value : '').trim().toLowerCase();

    comprasFiltradas = comprasCache.filter(c => {
      const matchMes = mesSel ? (parseYYYYMM(c.fecha) === mesSel) : true;
      const matchProv = provTxt ? String(c.proveedor).toLowerCase().includes(provTxt) : true;
      return matchMes && matchProv;
    });

    renderTabla(comprasFiltradas);
    actualizarTotalesLocales(comprasFiltradas);
  }
})();