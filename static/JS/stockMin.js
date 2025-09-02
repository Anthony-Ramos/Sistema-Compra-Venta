


// static/js/stokMin.js
document.addEventListener("DOMContentLoaded", () => {
  const tbody = document.querySelector("#tabla-stockmin");
  if (!tbody) return console.error("No se encontró #tabla-stockmin en el DOM");

  cargarStockMinimo();
});

function cargarStockMinimo() {
  fetch("/api/stock_minimo")
    .then(response => {
      if (!response.ok) throw new Error(`Error HTTP: ${response.status}`);
      return response.json();
    })
    .then(productos => {
      console.log("📦 Productos con stock bajo:", productos);
      const tbody = document.querySelector("#tabla-stockmin");
      if (!tbody) return;

      tbody.innerHTML = "";

      if (!Array.isArray(productos) || productos.length === 0) {
        tbody.innerHTML = `<tr><td colspan="4">No hay productos con stock bajo</td></tr>`;
        return;
      }

      productos.forEach(p => {
        const row = document.createElement("tr");
        const badge = badgeFor(p.stock_minimo);

        row.innerHTML = `
          <td>${p.id_producto}</td>
          <td>${p.nombre}</td>
          <td>${p.descripcion || "Sin descripción"}</td>
          <td>
            ${p.stock_minimo}
            ${badge ? ` <span class="badge ${badge.className}">${badge.text}</span>` : ""}
          </td>
        `;
        tbody.appendChild(row);
      });
    })
    .catch(err => {
      console.error("❌ Error al cargar stock mínimo:", err);
      const tbody = document.querySelector("#tabla-stockmin");
      if (tbody) {
        tbody.innerHTML = `<tr><td colspan="4">Error al cargar los datos</td></tr>`;
      }
    });
}

/**
 * Devuelve el texto y la clase de la badge según el stock.
 * - 30 a 20  => "Stock nivel casi crítico" (ámbar)
 * - < 10     => "Stock crítico" (rojo)
 * - = 0      => "Agotado" (gris oscuro)
 */
function badgeFor(stock) {
  if (stock === 0) {
    return { text: "Agotado", className: "badge-gray" };
  }
  if (stock < 10) {
    return { text: "Stock crítico", className: "badge-red" };
  }
  if (stock >= 20 && stock <= 30) {
    return { text: "Stock nivel casi crítico", className: "badge-amber" };
  }
  return null;
}