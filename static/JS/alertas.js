window.addEventListener("DOMContentLoaded", () => {
    cargarAlertasStock();
});

async function cargarAlertasStock() {
    try {
        const response = await fetch("/productos/bajo_stock");
        if (!response.ok) throw new Error("Error al cargar bajo stock");
        const productos = await response.json();

        const contenedor = document.getElementById("alertas-stock");
        contenedor.innerHTML = "";

        if (productos.length === 0) {
            contenedor.innerHTML = `
        <div class="alerta alerta-ok">
            <img src="/static/IMG/si.png">
            No hay alertas de stock bajo
        </div>`;
            return;
        }

        productos.forEach(p => {
            const alerta = document.createElement("div");
            alerta.classList.add("alerta");

            if (p.stock_actual === 0) {
                alerta.classList.add("alerta-agotado");
                alerta.innerHTML = `
        <img src="/static/IMG/alerta.png">
        Producto <strong>${p.nombre}</strong> está <strong>AGOTADO</strong>.`;
            } else {
                alerta.classList.add("alerta-bajo");
                alerta.innerHTML = `
        <img src="/static/IMG/bajostock.png">
        Producto <strong>${p.nombre}</strong> bajo stock.
        (Actual: <strong>${p.stock_actual}</strong> / Mínimo: ${p.stock_minimo})`;
            }

            contenedor.appendChild(alerta);
        });
    } catch (error) {
        console.error("Error cargando alertas:", error);
    }
}
