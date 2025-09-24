window.addEventListener("DOMContentLoaded", async () => {
    await cargarRoles();
    cargarTusuarios();
});
async function cargarRoles() {
    try {
        const response = await fetch("/obtener_roles");
        if (!response.ok) throw new Error("Error en la petición HTTP");
        const categorias = await response.json();

        const selectForm = document.getElementById("roles");
        selectForm.innerHTML = '<option value="">Seleccione un rol</option>';
        categorias.forEach(cat => {
            const option = document.createElement("option");
            option.value = cat.id;
            option.textContent = cat.nombre;
            selectForm.appendChild(option);
        });
        mostrarToast("/static/IMG/iconos/check.png", "Categorias cargadas exitosamente", "success");
    } catch (error) {
        mostrarToast("/static/IMG/iconos/error.png", "Error al cargar las Categorias", "error");
    }
}
async function cargarTusuarios() {
    try {
        const response = await fetch("/obtener_usuarios");
        if (!response.ok) throw new Error("Error en la petición HTTP");

        const usuarios = await response.json();

        const tablaBody = document.querySelector("#tablaUsuarios");
        tablaBody.innerHTML = "";

        usuarios.forEach(u => {
            const fila = document.createElement("tr");

            fila.innerHTML = `
        <td class='id-general'>${u.id_usuario}</td>
        <td>${u.nom_usuario}</td>
        <td>${u.correo}</td>
        <td>${u.telefono}</td>
        <td>${u.rol}</td>
        <td>
                <button class="btn-editar" data-id="${u.id_usuario}">Editar</button>
                <button class="btn-eliminar" data-id="${u.id_usuario}">Eliminar</button>
         </td>
      `;
            tablaBody.appendChild(fila);
        });

        document.querySelectorAll(".btn-editar").forEach(btn => {
            btn.addEventListener("click", e => {
                const id = e.target.dataset.id;
                const usuario = usuarios.find(u => u.id_usuario == id);

                if (!usuario) return;

                document.getElementById("id_usuario").value = usuario.id_usuario;
                document.getElementById("nombre").value = usuario.nom_usuario;
                document.getElementById("correo").value = usuario.correo;
                document.getElementById("telefono").value = usuario.telefono;
                document.getElementById("roles").value = usuario.id_rol;
            });
        });


    } catch (error) {
        console.error("Error cargando usuarios:", error);
    }
}