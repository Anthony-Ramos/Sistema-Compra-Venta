document.addEventListener("DOMContentLoaded", () => {
    cargarComboCategoria();
    cargarComboFiltro();
    cargarProveedores();
    cargarProductos();
    
    const selectFiltro = document.getElementById("filtro");
    selectFiltro.addEventListener("change", () => {
        const categoria = selectFiltro.value;
        cargarProductos(categoria); // llama con filtro
    });
});

function cargarComboCategoria() {
    fetch("http://localhost:5000/categorias")
        .then(response => response.json())
        .then(data => {
            const selectCategoria = document.getElementById("categoria");
            selectCategoria.innerHTML = '<option value="">Seleccione una categoría</option>';

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
            selectProveedor.innerHTML = '<option value="">Seleccione un proveedor</option>';

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
            const tbody = document.querySelector('#tabla-produc');
            tbody.innerHTML = "";

            productos.forEach(p => {
                const row = document.createElement("tr");
                row.innerHTML = `
                    <td>${p.nombre}</td>
                    <td>${p.categoria}</td>
                    <td>${p.proveedor}</td>
                    <td>${p.precio_compra}</td>
                    <td>${p.precio_venta}</td>
                    <td>${p.stock_actual}</td>
                `;
                tbody.appendChild(row);
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
            console.log(data); // Aquí puedes actualizar la tabla
        })
        .catch(error => console.error("Error:", error));
});

// 🔹 Guardar producto
document.getElementById("guardar").addEventListener("click", function() {
    const data = {
        nombre: document.getElementById("nombre").value,
        categoria: document.getElementById("categoria").value,
        proveedor: document.getElementById("proveedor").value,
        precio_compra: document.getElementById("precio_compra").value,
        precio_venta: document.getElementById("precio_venta").value,
        stock_minimo: document.getElementById("stock_minimo").value,
        descripcion: document.getElementById("descripcion").value
    };

    fetch("http://localhost:5000/agregar_producto", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(data)
    })
    .then(response => {
        if(response.ok){
            alert("Producto agregado correctamente");
            cargarProductos(); // 🔹 recargar la tabla dinámicamente
        } else {
            alert("Error al agregar el producto");
        }
    })
    .catch(error => console.error("Error al enviar producto:", error));
});

// 🔹 Cancelar formulario
document.getElementById("cancelar").addEventListener("click", function(){
    document.getElementById("nombre").value = "";
    document.getElementById("categoria").value = "";
    document.getElementById("proveedor").value = "";
    document.getElementById("precio_compra").value = "";
    document.getElementById("precio_venta").value = "";
    document.getElementById("stock_minimo").value = "";
    document.getElementById("descripcion").value = "";
});