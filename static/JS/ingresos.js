document.addEventListener("DOMContentLoaded", () => {
  const tbody = document.querySelector('#tabla-ventas');
  const endpoint = tbody?.dataset.endpoint || "/api/ventas"; // fallback

  cargarVentas(endpoint);
  cargarTotalGeneral();
  prepararFiltroMes();
});

// =======================
// Render de la tabla
// =======================
function cargarVentas(endpoint) {
  fetch(endpoint)
    .then(response => {
      if (!response.ok) throw new Error(`Error HTTP: ${response.status}`);
      return response.json();
    })
    .then(ventas => {
      console.log('Ventas cargadas:', ventas);
      const tbody = document.querySelector('#tabla-ventas');
      if (!tbody) return console.error('No se encontró #tabla-ventas');

      tbody.innerHTML = "";

      if (!Array.isArray(ventas) || ventas.length === 0) {
        tbody.innerHTML = '<tr><td colspan="9">No hay ventas registradas</td></tr>';
        return;
      }

      const safeMoney = v => Number.isFinite(parseFloat(v)) ? parseFloat(v).toFixed(2) : '0.00';

      ventas.forEach(v => {
        const row = document.createElement("tr");
        row.innerHTML = `
          <td>${v.id_venta}</td>
          <td>${v.fecha}</td>
          <td>${v.usuario}</td>
          <td>${v.producto}</td>
          <td>${v.cantidad}</td>
          <td>$${safeMoney(v.precio_unitario)}</td>
          <td>$${safeMoney(v.subtotal)}</td>
          <td>$${safeMoney(v.total_venta)}</td>
          <td>${v.metodo_pago}</td>
        `;
        tbody.appendChild(row);
      });
    })
    .catch(error => {
      console.error("Error cargando ventas:", error);
      const tbody = document.querySelector('#tabla-ventas');
      if (tbody) {
        tbody.innerHTML = '<tr><td colspan="9">Error cargando datos. Revisa la consola.</td></tr>';
      }
    });
}

// =======================
// Totales
// =======================
const money = v =>
  Number.isFinite(parseFloat(v)) ? `$${parseFloat(v).toFixed(2)}` : '$0.00';

function cargarTotalGeneral() {
  fetch("/api/ventas/total")
    .then(r => { if (!r.ok) throw new Error(`HTTP ${r.status}`); return r.json(); })
    .then(({ total }) => {
      document.getElementById("total-general").textContent = money(total);
    })
    .catch(err => console.error("Error total general:", err));
}

function cargarTotalPorMes(mesYYYYMM) {
  if (!mesYYYYMM) {
    document.getElementById("total-mes").textContent = '$0.00';
    return;
  }
  const url = `/api/ventas/total?mes=${encodeURIComponent(mesYYYYMM)}`;
  fetch(url)
    .then(r => { if (!r.ok) throw new Error(`HTTP ${r.status}`); return r.json(); })
    .then(({ total }) => {
      document.getElementById("total-mes").textContent = money(total);
    })
    .catch(err => console.error("Error total por mes:", err));
}

function prepararFiltroMes() {
  const inputMes = document.getElementById("filtro-mes");
  if (!inputMes) return;

  // Cuando el usuario cambie el mes, recalculamos el total del mes
  inputMes.addEventListener("change", () => {
    const mes = inputMes.value; // formato "YYYY-MM"
    cargarTotalPorMes(mes);
  });

  // (Opcional) Inicializa al mes actual:
  const hoy = new Date();
  const yyyy = hoy.getFullYear();
  const mm = String(hoy.getMonth() + 1).padStart(2, '0');
  inputMes.value = `${yyyy}-${mm}`;
  cargarTotalPorMes(inputMes.value);
}