window.addEventListener("DOMContentLoaded", () => {
    cargarCategorias();
    cargarProveedores();
    cargarCategoriasFiltro();
    const selectFiltro = document.getElementById("filtro");
    cargarProductos(selectFiltro.value);

    selectFiltro.addEventListener("change", () => {
        cargarProductos(selectFiltro.value);
    });
});
async function cargarCategorias() {
    try {
        const response = await fetch("/categorias");
        if (!response.ok) throw new Error("Error en la petición HTTP");
        const categorias = await response.json();

        const select = document.getElementById("categoria");
        select.innerHTML = '<option value="">Categoria</option>'; // limpia antes de llenar

        categorias.forEach(cat => {
            const option = document.createElement("option");
            option.value = cat.id;
            option.textContent = cat.nombre;
            select.appendChild(option);
        });
        mostrarToast("/static/IMG/iconos/check.png", "Categorias cargadas exitosamente", "success");
    } catch (error) {
        mostrarToast("/static/IMG/iconos/error.png", "Error al cargar las Categorias", "error");
    }
}
//Cargar las categorias en el filtro
async function cargarCategoriasFiltro() {
    try {
        const response = await fetch("/categorias");
        if (!response.ok) throw new Error("Error en la petición HTTP");
        const categorias = await response.json();

        const select = document.getElementById("filtro");
        select.innerHTML = '<option value="">Filtro</option>'; // limpia antes de llenar

        categorias.forEach(cat => {
            const option = document.createElement("option");
            option.value = cat.id;
            option.textContent = cat.nombre;
            select.appendChild(option);
        });
        mostrarToast("/static/IMG/iconos/check.png", "Categorias cargadas en el filtro exitosamente", "success");
    } catch (error) {
        mostrarToast("/static/IMG/iconos/error.png", "Error al cargar las Categorias en el filtro", "error");
    }
}
//Funcion de extraer proveedores de la base de datos
async function cargarProveedores() {
    try {
        const response = await fetch("/proveedores");
        if (!response.ok) throw new Error("Error en la petición HTTP");
        const proveedores = await response.json();

        const select = document.getElementById("proveedor");
        select.innerHTML = '<option value="">Proveedor</option>';

        //prov es una abreviacion de proveedores
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
//Funcion para extraer lo productos
async function cargarProductos(categoria = "") {
    try {
        let url = "/productos_filtro";
        if (categoria) url += `?categoria=${encodeURIComponent(categoria)}`;

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
        // Eventos Editar
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

        // Eventos Eliminar
        document.querySelectorAll(".btn-eliminar").forEach(btn => {
            btn.addEventListener("click", e => {
                const id = e.target.dataset.id;
                mostrarConfirmToast(
                    "¿Seguro que quieres eliminar este producto?",
                    async () => {
                        try {
                            const res = await fetch(`/eliminar_producto/${id}`, { method: "DELETE" });
                            if (res.ok) {
                                mostrarToast("/static/IMG/iconos/check.png", "Producto Eliminado", "success");
                                cargarProductos();
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
document.getElementById("guardar").addEventListener("click", function () {
    const id_producto = document.getElementById("id_producto").value.trim(); // Campo oculto para editar

    // Obtener valores del formulario
    const nombre = document.getElementById("nombre").value.trim();
    const descripcion = document.getElementById("descripcion").value.trim();
    const categoria = document.getElementById("categoria").value.trim();
    const proveedor = document.getElementById("proveedor").value.trim();
    const precio_compra = document.getElementById("precio_compra").value.trim();
    const precio_venta = document.getElementById("precio_venta").value.trim();
    const stock_minimo = document.getElementById("stock_minimo").value.trim();

    // Validación de campos obligatorios
    if (!nombre || !descripcion || !categoria || !proveedor || !precio_compra || !precio_venta || !stock_minimo) {
        mostrarToast("/static/IMG/iconos/advertencia.png", "Todos los campos son obligatorios", "warning");
        return;
    }

    // Construcción del objeto con conversión de tipos
    const data = {
        nombre: nombre,
        descripcion: descripcion,
        categoria: parseInt(categoria),
        proveedor: parseInt(proveedor),
        precio_compra: parseFloat(precio_compra),
        precio_venta: parseFloat(precio_venta),
        stock_minimo: parseInt(stock_minimo)
    };

    // Definir URL y método según si se está editando o agregando
    let url = "/agregar_producto";
    let method = "POST";
    if (id_producto) {
        url = `/editar_producto/${id_producto}`;
        method = "PUT";
    }

    // Enviar al backend
    fetch(url, {
        method: method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    })
        .then(response => response.json())
        .then(result => {
            if (result.status === "ok") {
                mostrarToast("/static/IMG/iconos/check.png", id_producto ? "Producto actualizado" : "Producto agregado correctamente", "success");

                // Limpiar formulario
                document.getElementById("id_producto").value = "";
                document.getElementById("nombre").value = "";
                document.getElementById("descripcion").value = "";
                document.getElementById("categoria").value = "";
                document.getElementById("proveedor").value = "";
                document.getElementById("precio_compra").value = "";
                document.getElementById("precio_venta").value = "";
                document.getElementById("stock_minimo").value = "";

                // Recargar productos
                if (typeof cargarProductos === "function") cargarProductos();

            } else {
                mostrarToast("/static/IMG/iconos/error.png", "Error al guardar producto", "error");
            }
        })
        .catch(error => {
            console.error("Error en la conexión:", error);
            mostrarToast("/static/IMG/iconos/error.png", "Error en la conexión", "error");
        });
});