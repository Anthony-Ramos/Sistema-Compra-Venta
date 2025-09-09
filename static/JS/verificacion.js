const form = document.getElementById('loginForm');

    form.addEventListener('submit', function(e) {
        e.preventDefault(); // evita enviar el formulario si hay errores

        const usuario = document.getElementById('usuario').value.trim();
        const contrasena = document.getElementById('contrasena').value.trim();

        // Validación básica
        if(usuario.length < 3) {
            alert("El usuario debe tener al menos 3 caracteres.");
            return;
        }
        if(contrasena.length < 6) {
            alert("La contraseña debe tener al menos 6 caracteres.");
            return;
        }

        // Aquí iría la lógica para enviar el formulario
        alert("Formulario válido. Enviando...");
        form.submit(); // si quieres enviarlo realmente
    });