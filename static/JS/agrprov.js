  document.addEventListener("DOMContentLoaded", cargarProveedores);

async function cargarProveedores() {
    try {
        const response = await fetch("/list-proveedores");
        if (!response.ok) throw new Error("Error en la petición HTTP");
        const proveedores = await response.json();

        console.log(proveedores);
        const tbody = document.querySelector("#tabla-proveedores tbody");
        tbody.innerHTML = "";

        proveedores.forEach(prov => {
            const row = document.createElement("tr");

            row.innerHTML = `
                <td class="id-prov">${prov.id}</td>
                <td>${prov.nombre}</td>
                <td>${prov.telefono}</td>
                <td>${prov.email}</td>
                <td>${prov.direccion}</td>
                <td>
                    <button class="btn-editar" data-id="${prov.id}">Editar</button>
                    <button class="btn-eliminar" data-id="${prov.id}">Eliminar</button>
                </td>
            `;
            tbody.appendChild(row);
        });
        asignarEventos(proveedores);

    } catch (error) {
        console.error("Error cargando proveedores:", error);
        alert("Error al cargar los proveedores");
    }
}

// Función para asignar eventos de editar y eliminar
function asignarEventos(proveedores) {
    const inputNombre = document.getElementById("nombre");
    const inputTelefono = document.getElementById("telefono");
    const inputEmail = document.getElementById("email");
    const inputDireccion = document.getElementById("direccion");
    const inputId = document.getElementById("id_prov");

    // Eventos Editar
    document.querySelectorAll(".btn-editar").forEach(btn => {
        btn.addEventListener("click", e => {
            const id = e.target.dataset.id;
            const prov = proveedores.find(p => p.id == id);

            inputNombre.value = prov.nombre;
            inputTelefono.value = prov.telefono;
            inputEmail.value = prov.email;
            inputDireccion.value = prov.direccion;
            inputId.value = prov.id;
        });
    });

    // Eventos Eliminar
    document.querySelectorAll(".btn-eliminar").forEach(btn => {
        btn.addEventListener("click", e => {
            const id = e.target.dataset.id;

            mostrarConfirmToast(
                "¿Seguro que quieres eliminar este proveedor?",
                async () => {
                    try {
                        const res = await fetch(`/eliminar_proveedor/${id}`, { method: "DELETE" });
                        const data = await res.json();

                        if (res.ok && data.status === "ok") {
                            mostrarToast("/static/IMG/iconos/check.png", "Proveedor eliminado", "success");
                            cargarProveedores();
                        } else if (data.mensaje) {
                            mostrarToast("/static/IMG/iconos/informacion.png", data.mensaje, "informacion");
                        } else {
                            mostrarToast("/static/IMG/iconos/error.png", "Error al eliminar proveedor", "error");
                        }
                    } catch (err) {
                        mostrarToast("/static/IMG/iconos/error.png", "Error de conexión", "error");
                    }
                },
                () => {
                    mostrarToast("/static/IMG/iconos/informacion.png", "Eliminación cancelada", "informacion");
                }
            );
        });
    });
}

// Seleccionar botones e inputs
const btnGuardar = document.getElementById("guardar");
const btnCancelar = document.getElementById("cancelar");
const inputNombre = document.getElementById("nombre");
const inputTelefono = document.getElementById("telefono");
const inputEmail = document.getElementById("email");
const inputDireccion = document.getElementById("direccion");
const inputId = document.getElementById("id_prov");

// Botón Guardar
btnGuardar.addEventListener("click", async () => {
    const nombre = inputNombre.value.trim();
    const telefono = inputTelefono.value.trim();
    const email = inputEmail.value.trim();
    const direccion = inputDireccion.value.trim();
    const id = inputId.value;

    if (!nombre) {
        mostrarToast("/static/IMG/iconos/advertencia.png", "El nombre no debe quedar vacío", "warning");
        return;
    }

    try {
        let url = "/agregar_proveedor";
        let method = "POST";

        if (id) {
            url = `/editar_proveedor/${id}`;
            method = "PUT";
        }

        const response = await fetch(url, {
            method: method,
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ nombre, telefono, email, direccion })
        });

        const result = await response.json();

        if (result.status === "ok") {
            mostrarToast(
                "/static/IMG/iconos/check.png",
                id ? "Proveedor editado correctamente" : "Proveedor agregado correctamente",
                "success"
            );
            inputNombre.value = "";
            inputTelefono.value = "";
            inputEmail.value = "";
            inputDireccion.value = "";
            inputId.value = "";
            cargarProveedores();
        } else if (result.mensaje) {
            mostrarToast("/static/IMG/iconos/informacion.png", result.mensaje, "informacion");
        } else {
            mostrarToast("/static/IMG/iconos/error.png", "Error al guardar proveedor", "error");
        }
    } catch (error) {
        console.error("Error en la petición:", error);
        mostrarToast("/static/IMG/iconos/error.png", "Error de conexión", "error");
    }
});

btnCancelar.addEventListener("click", () => {
    inputNombre.value = "";
    inputTelefono.value = "";
    inputEmail.value = "";
    inputDireccion.value = "";
    inputId.value = "";
});