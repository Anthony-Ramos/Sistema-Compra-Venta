const modalRol = document.getElementById("modal-rol");
const btnAbrirRol = document.getElementById("abrir-modal-rol");
const btnCerrarRol = document.getElementById("cerrar-modal-rol");
const btnCancelarRol = document.getElementById("cancelar_rol_modal");
const tablaRoles = document.getElementById("tablaRoles");
const inputIdRol = document.getElementById("id_rol_modal");
const inputNombreRol = document.getElementById("nombre_rol_modal");

btnAbrirRol.addEventListener("click", () => {
    modalRol.style.display = "block";
    cargarRolesTabla();
});

btnCerrarRol.addEventListener("click", () => modalRol.style.display = "none");
btnCancelarRol.addEventListener("click", () => modalRol.style.display = "none");
window.addEventListener("click", e => { if (e.target === modalRol) modalRol.style.display = "none"; });

// Guardar rol (agregar o editar)
document.getElementById("guardar_rol_modal").addEventListener("click", async () => {
    const nombreRol = inputNombreRol.value.trim();
    const idRol = inputIdRol.value;

    if (!nombreRol) {
        mostrarToast("/static/IMG/iconos/error.png", "Ingrese un nombre de rol", "error");
        return;
    }

    try {
        const url = idRol ? `/editar_rol/${idRol}` : "/agregar_rol";
        const method = idRol ? "PUT" : "POST";

        const response = await fetch(url, {
            method,
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ nombre: nombreRol })
        });

        const data = await response.json();

        if (data.status === "ok") {
            mostrarToast("/static/IMG/iconos/check.png", data.mensaje, "success");
            inputIdRol.value = "";
            inputNombreRol.value = "";
            cargarRolesTabla();
            cargarRoles(); // actualizar select de usuarios
        } else {
            mostrarToast("/static/IMG/iconos/error.png", data.mensaje, "error");
        }
    } catch (error) {
        mostrarToast("/static/IMG/iconos/error.png", "Error al guardar el rol", "error");
        console.error(error);
    }
});

// Cargar roles en la tabla
async function cargarRolesTabla() {
    try {
        const response = await fetch("/obtener_roles");
        if (!response.ok) throw new Error("Error al obtener roles");
        const roles = await response.json();
        tablaRoles.innerHTML = "";

        roles.forEach(r => {
            const fila = document.createElement("tr");
            fila.innerHTML = `
        <td>${r.id}</td>
        <td>${r.nombre}</td>
        <td>${r.activo ? "Activo" : "Inactivo"}</td>
        <td>
          <button class="editar-rol" data-id="${r.id}" data-nombre="${r.nombre}">Editar</button>
          <button class="baja-rol" data-id="${r.id}" data-activo="${r.activo}">
            ${r.activo ? "Dar de baja" : "Activar"}
          </button>
        </td>
      `;
            tablaRoles.appendChild(fila);
        });

        // Editar rol
        document.querySelectorAll(".editar-rol").forEach(btn => {
            btn.addEventListener("click", e => {
                inputIdRol.value = e.target.dataset.id;
                inputNombreRol.value = e.target.dataset.nombre;
            });
        });

        // Dar de baja / activar rol
        document.querySelectorAll(".baja-rol").forEach(btn => {
            btn.addEventListener("click", async e => {
                const id = e.target.dataset.id;
                try {
                    const response = await fetch(`/cambiar_estado_rol/${id}`, { method: "PUT" });
                    const data = await response.json();
                    if (data.status === "ok") {
                        mostrarToast("/static/IMG/iconos/check.png", data.mensaje, "success");
                        cargarRolesTabla();
                        cargarRoles(); // actualizar select de usuarios
                    } else {
                        // Aquí mostramos el mensaje de error si hay usuarios activos asociados
                        mostrarToast("/static/IMG/iconos/error.png", data.mensaje, "error");
                    }
                } catch (error) {
                    mostrarToast("/static/IMG/iconos/error.png", "Usuarios activos impiden baja", "error");
                    console.error(error);
                }
            });
        });

    } catch (error) {
        mostrarToast("/static/IMG/iconos/error.png", "Error al cargar la tabla de roles", "error");
        console.error(error);
    }
}