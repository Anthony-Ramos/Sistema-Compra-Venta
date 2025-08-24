document.addEventListener("DOMContentLoaded", () => {
    cargarComboCategoria();
    cargarComboFiltro();
    cargarProveedores();
    cargarProductos();

    const selectFiltro = document.getElementById("filtro");
    selectFiltro.addEventListener("change", () => {
        const categoria = selectFiltro.value;
        cargarProductos(categoria);
    });
});

function cargarComboCategoria() {
    fetch("http://localhost:5000/categorias")
        .then(response => response.json())
        .then(data => {
            const selectCategoria = document.getElementById("categoria");
            selectCategoria.innerHTML = '<option value="">Categoria</option>';

            data.forEach(cat => {
                const option = document.createElement("option");
                option.value = cat.id;
                option.textContent = cat.nombre;
                selectCategoria.appendChild(option);
            });
        })
        .catch(error => console.error("Error cargando categorías para el primer combo:", error));
}
// Función para llenar el segundo combo
function cargarComboFiltro() {
    fetch("http://localhost:5000/categorias")
        .then(response => response.json())
        .then(data => {
            const selectFiltro = document.getElementById("filtro");
            selectFiltro.innerHTML = '<option value="">Filtro</option>';

            data.forEach(cat => {
                const option = document.createElement("option");
                option.value = cat.id;
                option.textContent = cat.nombre;
                selectFiltro.appendChild(option);
            });
        })
        .catch(error => console.error("Error cargando categorías para el filtro:", error));
}
function cargarProveedores() {
    fetch("http://localhost:5000/proveedores")
        .then(response => response.json())
        .then(data => {
            const selectProveedor = document.getElementById("proveedor");
            selectProveedor.innerHTML = '<option value="">Proveedor</option>';

            data.forEach(prov => {
                const option = document.createElement("option");
                option.value = prov.id;
                option.textContent = prov.nombre;
                selectProveedor.appendChild(option);
            });
        })
        .catch(error => console.error("Error cargando proveedores:", error));
}
function cargarProductos(categoria = "") {
    let url = "http://localhost:5000/productos_filtro";
    if (categoria) {
        url += `?categoria=${encodeURIComponent(categoria)}`;
    }

    fetch(url)
        .then(response => response.json())
        .then(productos => {
            console.log(productos);
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

            // BTN-editar
            document.querySelectorAll(".btn-editar").forEach(btn => {
                btn.addEventListener("click", (e) => {
                    const id = e.target.getAttribute("data-id");
                    const producto = productos.find(p => p.id_producto == id);

                    document.getElementById("id_producto").value = producto.id_producto;
                    document.getElementById("nombre").value = producto.nombre;
                    document.getElementById("categoria").value = producto.id_categoria;
                    document.getElementById("proveedor").value = producto.id_proveedor;
                    document.getElementById("precio_compra").value = producto.precio_compra;
                    document.getElementById("precio_venta").value = producto.precio_venta;
                    document.getElementById("stock_minimo").value = producto.stock_minimo;
                    document.getElementById("descripcion").value = producto.descripcion;

                    console.log("Editando producto:", producto);
                });
            });

            // BTN-eliminar
            document.querySelectorAll(".btn-eliminar").forEach(btn => {
                btn.addEventListener("click", (e) => {
                    const id = e.target.getAttribute("data-id");
                    if (confirm("¿Seguro que quieres eliminar este producto?")) {
                        fetch(`http://localhost:5000/eliminar_producto/${id}`, {
                            method: "DELETE"
                        })
                        .then(response => {
                            if (response.ok) {
                                alert("Producto eliminado correctamente");
                                cargarProductos();
                            } else {
                                alert("Error al eliminar el producto");
                            }
                        })
                        .catch(error => console.error("Error al eliminar producto:", error));
                    }
                });
            });

        })
        .catch(error => console.error("Error cargando productos:", error));
}
const selectFiltro = document.getElementById("filtro");

selectFiltro.addEventListener("change", () => {
    const categoria = selectFiltro.value;
    let url = `http://localhost:5000/productos_filtro`;
    if (categoria) {
        url += `?categoria=${encodeURIComponent(categoria)}`;
    }

    fetch(url)
        .then(response => response.json())
        .then(data => {
            console.log(data);
        })
        .catch(error => console.error("Error:", error));
});

//Guardar producto
document.getElementById("guardar").addEventListener("click", function () {
    const id_producto = document.getElementById("id_producto").value; // campo oculto o input

    const data = {
        nombre: document.getElementById("nombre").value,
        categoria: document.getElementById("categoria").value,
        proveedor: document.getElementById("proveedor").value,
        precio_compra: document.getElementById("precio_compra").value,
        precio_venta: document.getElementById("precio_venta").value,
        stock_minimo: document.getElementById("stock_minimo").value,
        descripcion: document.getElementById("descripcion").value
    };

    let url = "http://localhost:5000/agregar_producto";
    let method = "POST";

    if (id_producto) {
        // Si existe ID, hacemos un PUT para actualizar
        url = `http://localhost:5000/editar_producto/${id_producto}`;
        method = "PUT";
    }

    fetch(url, {
        method: method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    })
        .then(response => {
            if (response.ok) {
                if (id_producto) {
                    alert("Producto actualizado correctamente");
                } else {
                    alert("Producto agregado correctamente");
                }
                // Limpiar formulario y recargar tabla
                document.getElementById("id_producto").value = "";
                document.getElementById("nombre").value = "";
                document.getElementById("categoria").value = "";
                document.getElementById("proveedor").value = "";
                document.getElementById("precio_compra").value = "";
                document.getElementById("precio_venta").value = "";
                document.getElementById("stock_minimo").value = "";
                document.getElementById("descripcion").value = "";
                
                cargarProductos();
            } else {
                alert("Error al guardar el producto");
            }
        })
        .catch(error => console.error("Error al enviar producto:", error));
});
// 🔹 Cancelar formulario
document.getElementById("cancelar").addEventListener("click", function () {
    document.getElementById("nombre").value = "";
    document.getElementById("categoria").value = "";
    document.getElementById("proveedor").value = "";
    document.getElementById("precio_compra").value = "";
    document.getElementById("precio_venta").value = "";
    document.getElementById("stock_minimo").value = "";
    document.getElementById("descripcion").value = "";
});