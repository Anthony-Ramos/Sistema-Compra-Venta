// ===============================
// Evento principal al cargar la página
// ===============================
window.addEventListener("DOMContentLoaded", () => {
    cargarCategorias();
    cargarProveedores();
    const selectFiltro = document.getElementById("filtro");
    const inputBuscar = document.getElementById("buscador");
    const btnBuscar   = document.querySelector(".buscador button");

    // 🔹 Cargar productos al inicio
    cargarProductos(selectFiltro.value, inputBuscar.value);

    // 🔹 Filtrar por categoría
    selectFiltro.addEventListener("change", () => {
        cargarProductos(selectFiltro.value, inputBuscar.value);
    });

    // 🔹 Buscar al dar clic en el botón
    btnBuscar.addEventListener("click", () => {
        cargarProductos(selectFiltro.value, inputBuscar.value);
    });

    // 🔹 Buscar al presionar Enter
    inputBuscar.addEventListener("keypress", (e) => {
        if (e.key === "Enter") {
            e.preventDefault();
            cargarProductos(selectFiltro.value, inputBuscar.value);
        }
    });
});

// ===============================
// Cargar categorías
// ===============================
async function cargarCategorias() {
    try {
        const response = await fetch("/categorias");
        if (!response.ok) throw new Error("Error en la petición HTTP");
        const categorias = await response.json();

        // 🔹 Combo de formulario (Agregar producto)
        const selectForm = document.getElementById("categoria");
        selectForm.innerHTML = '<option value="">Categoria</option>';
        categorias.forEach(cat => {
            const option = document.createElement("option");
            option.value = cat.id;
            option.textContent = cat.nombre;
            selectForm.appendChild(option);
        });

        // 🔹 Combo de filtro (buscador de productos)
        const selectFiltro = document.getElementById("filtro");
        selectFiltro.innerHTML = '<option value="">Todas las categorías</option>';
        categorias.forEach(cat => {
            const option = document.createElement("option");
            option.value = cat.id;
            option.textContent = cat.nombre;
            selectFiltro.appendChild(option);
        });

        mostrarToast("/static/IMG/iconos/check.png", "Categorias cargadas exitosamente", "success");
    } catch (error) {
        mostrarToast("/static/IMG/iconos/error.png", "Error al cargar las Categorias", "error");
    }
}

// ===============================
// Cargar proveedores
// ===============================
async function cargarProveedores() {
    try {
        const response = await fetch("/proveedores");
        if (!response.ok) throw new Error("Error en la petición HTTP");
        const proveedores = await response.json();

        const select = document.getElementById("proveedor");
        select.innerHTML = '<option value="">Proveedor</option>';

        proveedores.forEach(prov => {
            const option = document.createElement("option");
            option.value = prov.id;
            option.textContent = prov.nombre;
            select.appendChild(option);
        });
        mostrarToast("/static/IMG/iconos/check.png", "Proveedores cargados exitosamente", "success");
    } catch (error) {
        mostrarToast("/static/IMG/iconos/error.png", "Error al cargar los proveedores", "error");
    }
}

// ===============================
// Cargar productos (con filtros)
// ===============================
async function cargarProductos(categoria = "", query = "") {
    try {
        let url = "/productos_filtro?";
        if (categoria) url += `categoria=${encodeURIComponent(categoria)}&`;
        if (query) url += `q=${encodeURIComponent(query)}`;

        const response = await fetch(url);
        if (!response.ok) throw new Error("Error en la petición HTTP");

        const productos = await response.json();
        const tbody = document.querySelector('#tabla-produc');
        tbody.innerHTML = "";

        productos.forEach(p => {
            const row = document.createElement("tr");
            row.innerHTML = `
                <td style="display:none;">${p.id_producto}</td>
                <td>${p.nombre}</td>
                <td>${p.categoria}</td>
                <td>${p.proveedor}</td>
                <td>${p.precio_compra}</td>
                <td>${p.precio_venta}</td>
                <td>${p.stock_minimo}</td>
                <td>
                    <button class="btn-editar" data-id="${p.id_producto}">Editar</button>
                    <button class="btn-eliminar" data-id="${p.id_producto}">Eliminar</button>
                </td>
            `;
            tbody.appendChild(row);
        });

        mostrarToast("/static/IMG/iconos/check.png", "Productos cargados exitosamente", "success");

        // ===============================
        // Botón Editar
        // ===============================
        document.querySelectorAll(".btn-editar").forEach(btn => {
            btn.addEventListener("click", e => {
                const id = e.target.dataset.id;
                const producto = productos.find(p => p.id_producto == id);

                document.getElementById("id_producto").value = producto.id_producto;
                document.getElementById("nombre").value = producto.nombre;
                document.getElementById("categoria").value = producto.id_categoria;
                document.getElementById("proveedor").value = producto.id_proveedor;
                document.getElementById("precio_compra").value = producto.precio_compra;
                document.getElementById("precio_venta").value = producto.precio_venta;
                document.getElementById("stock_minimo").value = producto.stock_minimo;
                document.getElementById("descripcion").value = producto.descripcion;
            });
        });

        // ===============================
        // Botón Eliminar
        // ===============================
        document.querySelectorAll(".btn-eliminar").forEach(btn => {
            btn.addEventListener("click", e => {
                const id = e.target.dataset.id;
                mostrarConfirmToast(
                    "¿Seguro que quieres eliminar este producto?",
                    async () => {
                        try {
                            const res = await fetch(`/productos/eliminar_producto/${id}`, { method: "DELETE" });
                            if (res.ok) {
                                mostrarToast("/static/IMG/iconos/check.png", "Producto Eliminado", "success");
                                cargarProductos(categoria, query);
                            } else {
                                mostrarToast("/static/IMG/iconos/error.png", "Error al Eliminar", "error");
                            }
                        } catch {
                            mostrarToast("/static/IMG/iconos/error.png", "Error en la conexión", "error");
                        }
                    },
                    () => mostrarToast("/static/IMG/iconos/advertencia.png", "Eliminación cancelada", "warning")
                );
            });
        });

    } catch (error) {
        console.error("Error cargando productos:", error);
        mostrarToast("/static/IMG/iconos/error.png", "Error cargando productos", "error");
    }
}
