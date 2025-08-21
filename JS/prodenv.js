document.addEventListener("DOMContentLoaded", () => {
    cargarCategorias();
    cargarProveedores();
});

function cargarCategorias() {
    
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
        .catch(error => console.error("Error cargando categorías:", error));
}

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
            window.location.reload();
        } else {
            alert("Error al agregar el producto");
        }
    })
    .catch(error => console.error("Error al enviar producto:", error));
});
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
document.getElementById("cancelar").addEventListener("click", function(){
    window.location.reload();
});