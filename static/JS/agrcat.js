document.addEventListener("DOMContentLoaded", cargarCategorias);

// Función para cargar categorías en la tabla
async function cargarCategorias() {
    try {
        const response = await fetch("/categorias");
        if (!response.ok) throw new Error("Error en la petición HTTP");
        const categorias = await response.json();

        const tbody = document.getElementById("tabla-cate");
        tbody.innerHTML = ""; // limpiar antes de llenar

        categorias.forEach(cat => {
            const row = document.createElement("tr");

            row.innerHTML = `
                <td class="id-general">${cat.id}</td>
                <td>${cat.nombre}</td>
                <td>
                    <button class="btn-editar" data-id="${cat.id}">Editar</button>
                    <button class="btn-eliminar" data-id="${cat.id}">Eliminar</button>
                </td>
            `;

            tbody.appendChild(row);
        });

        // Agregar eventos a los botones
        asignarEventos(categorias);

    } catch (error) {
        console.error("Error cargando categorías:", error);
        alert("Error al cargar las categorías");
    }
}

// Función para asignar eventos de editar y eliminar
// Eventos Eliminar con toast personalizado
function asignarEventos(categorias) {
    const inputNombre = document.getElementById("nombre-categoria");
    const inputId = document.getElementById("id_cate");

    // Eventos Editar
    document.querySelectorAll(".btn-editar").forEach(btn => {
        btn.addEventListener("click", e => {
            const id = e.target.dataset.id;
            const categoria = categorias.find(c => c.id == id);
            inputNombre.value = categoria.nombre;
            inputId.value = categoria.id;
        });
    });

    // Eventos Eliminar
    document.querySelectorAll(".btn-eliminar").forEach(btn => {
        btn.addEventListener("click", e => {
            const id = e.target.dataset.id;

            mostrarConfirmToast("¿Seguro que quieres eliminar esta categoría?", async () => {
                try {
                    const res = await fetch(`/eliminar_categoria/${id}`, { method: "DELETE" });
                    const data = await res.json();

                    if (res.ok && data.status === "ok") {
                        mostrarToast("/static/IMG/iconos/check.png", "Categoría eliminada", "success");
                        cargarCategorias(); // recargar tabla
                    } else if (data.mensaje) {
                        mostrarToast("/static/IMG/iconos/informacion.png", data.mensaje, "informacion");
                    } else {
                        mostrarToast("/static/IMG/iconos/error.png", "Error al eliminar categoría", "error");
                    }
                } catch (err) {
                    mostrarToast("/static/IMG/iconos/error.png", "Error de conexión", "error");
                }
            }, () => {
                mostrarToast("/static/IMG/iconos/informacion.png", "Eliminación cancelada", "informacion");
            });
        });
    });
}
// Seleccionar botones e input
const btnGuardar = document.getElementById("cate_guardar");
const btnCancelar = document.getElementById("cate_cancelar");
const inputNombre = document.getElementById("nombre-categoria");
const inputId = document.getElementById("id_cate");

// Botón Guardar
btnGuardar.addEventListener("click", async () => {
    const nombre = inputNombre.value.trim();
    const id = inputId.value;

    if (!nombre) {
        mostrarToast("/static/IMG/iconos/advertencia.png", "El nombre no debe quedar vacío", "warning");
        return;
    }

    try {
        let url = "/agregar_categoria";
        let method = "POST";

        if (id) {
            url = `/editar_categoria/${id}`;
            method = "PUT";
        }

        const response = await fetch(url, {
            method: method,
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ nombre })
        });

        const result = await response.json();

        if (result.status === "ok") {
            mostrarToast(
                "/static/IMG/iconos/check.png",
                id ? "Categoría editada correctamente" : "Categoría agregada correctamente",
                "success"
            );
            inputNombre.value = "";
            inputId.value = "";
            cargarCategorias();
        } else if (result.mensaje) {
            // Mensaje específico del backend, ej. "La categoría ya existe"
            mostrarToast("/static/IMG/iconos/informacion.png", result.mensaje, "informacion");
        } else {
            mostrarToast("/static/IMG/iconos/error.png", "Error al guardar categoría", "error");
        }
    } catch (error) {
        console.error("Error en la petición:", error);
        mostrarToast("/static/IMG/iconos/error.png", "Error de conexión", "error");
    }
});
btnCancelar.addEventListener("click", () => {
    inputNombre.value = "";
    inputId.value = "";
});