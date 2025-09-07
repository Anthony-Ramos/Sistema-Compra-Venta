document.addEventListener("DOMContentLoaded", cargarUsuarios);

const tbody = document.querySelector(".tabla-user");
const inputNombre = document.getElementById("nombre");
const inputCorreo = document.getElementById("correo");
const inputContrasena = document.getElementById("contrasena");
const inputContrasenaRep = document.getElementById("contrasenarep");
const inputId = document.getElementById("id_usuario");
const btnGuardar = document.getElementById("guardar");
const btnCancelar = document.getElementById("cancelar");

// Cargar usuarios en la tabla
async function cargarUsuarios() {
    try {
        const res = await fetch("/usuarios/todos");
        const usuarios = await res.json();

        tbody.innerHTML = "";
        usuarios.forEach(u => {
            const row = document.createElement("tr");
            row.innerHTML = `
                <td>${u.id_usuario}</td>
                <td>${u.nom_usuario}</td>
                <td>${u.nom_rol}</td>
                <td>
                    <button class="editar" data-id="${u.id_usuario}">Editar</button>
                    <button class="eliminar" data-id="${u.id_usuario}">Eliminar</button>
                </td>
            `;
            tbody.appendChild(row);
        });
        asignarEventos();
    } catch (err) {
        console.error("Error cargando usuarios:", err);
    }
}

// Asignar eventos de editar y eliminar
function asignarEventos() {
    document.querySelectorAll(".editar").forEach(btn => {
        btn.addEventListener("click", async e => {
            const id = e.target.dataset.id;
            const row = e.target.closest("tr");
            inputId.value = id;
            inputNombre.value = row.children[1].innerText;
            // Aquí puedes agregar más campos si los quieres editar
        });
    });

    document.querySelectorAll(".eliminar").forEach(btn => {
        btn.addEventListener("click", async e => {
            const id = e.target.dataset.id;
            if (!confirm("¿Deseas eliminar este usuario?")) return;
            try {
                const res = await fetch(`/usuarios/eliminar/${id}`, { method: "DELETE" });
                const data = await res.json();
                if (data.status === "ok") cargarUsuarios();
                else alert(data.mensaje || "Error al eliminar");
            } catch (err) {
                console.error(err);
            }
        });
    });
}

// Guardar usuario (nuevo o editar)
btnGuardar.addEventListener("click", async () => {
    const nombre = inputNombre.value.trim();
    const correo = inputCorreo.value.trim();
    const contrasena = inputContrasena.value.trim();
    const contrasenaRep = inputContrasenaRep.value.trim();
    const id = inputId.value;

    if (!nombre || !correo || !contrasena || !contrasenaRep) {
        alert("Todos los campos son obligatorios");
        return;
    }
    if (contrasena !== contrasenaRep) {
        alert("Las contraseñas no coinciden");
        return;
    }

    try {
        let url = "/usuarios/agregar";
        let method = "POST";
        if (id) {
            url = `/usuarios/editar/${id}`;
            method = "PUT";
        }

        const res = await fetch(url, {
            method: method,
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ nombre, correo, contrasena })
        });
        const data = await res.json();
        if (data.status === "ok") {
            cargarUsuarios();
            inputId.value = "";
            inputNombre.value = "";
            inputCorreo.value = "";
            inputContrasena.value = "";
            inputContrasenaRep.value = "";
        } else {
            alert(data.mensaje || "Error al guardar");
        }
    } catch (err) {
        console.error(err);
    }
});

btnCancelar.addEventListener("click", () => {
    inputId.value = "";
    inputNombre.value = "";
    inputCorreo.value = "";
    inputContrasena.value = "";
    inputContrasenaRep.value = "";
});