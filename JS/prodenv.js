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

    fetch("/agregar_producto", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(data)
    })
    .then(response => {
        if(response.ok){
            alert("Producto agregado correctamente");
            window.location.reload();  // limpia el formulario
        } else {
            alert("Error al agregar el producto");
        }
    });
});

document.getElementById("cancelar").addEventListener("click", function(){
    window.location.reload();  // limpia el formulario
});
