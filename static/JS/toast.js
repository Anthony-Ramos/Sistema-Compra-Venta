// toast.js
function mostrarToast(icono, mensaje, tipo) {
    const contenedor = document.getElementById("toast-container");
    
    if (!contenedor) {
        console.error("No se encontró el contenedor de toasts");
        return;
    }
    // Crear toast
    const toast = document.createElement("div");
    toast.classList.add("toast", tipo); // asigna color por tipo
    toast.innerHTML = `<img src="${icono}" alt="icono"> <span>${mensaje}</span>`;
    contenedor.appendChild(toast);

    // Mostrar con animación
    setTimeout(() => toast.classList.add("show"), 100);

    // Ocultar después de 3s
    setTimeout(() => {
        toast.classList.remove("show");
        setTimeout(() => toast.remove(), 400);
    }, 3000);
}

//Toast de verificacion
function mostrarConfirmToast(mensaje, callbackAceptar, callbackCancelar) {
    const contenedor = document.getElementById("toast-container");
    if (!contenedor) return;

    // Crear toast
    const toast = document.createElement("div");
    toast.classList.add("confirm-toast");
    toast.innerHTML = `
        <span>${mensaje}</span>
        <div class="buttons">
            <button class="accept">Aceptar</button>
            <button class="cancel">Cancelar</button>
        </div>
    `;
    contenedor.appendChild(toast);

    // Mostrar con animación
    setTimeout(() => toast.classList.add("show"), 100);

    // Manejo de botones
    toast.querySelector(".accept").addEventListener("click", () => {
        if (callbackAceptar) callbackAceptar();
        cerrarToast(toast);
    });

    toast.querySelector(".cancel").addEventListener("click", () => {
        if (callbackCancelar) callbackCancelar();
        cerrarToast(toast);
    });
}

function cerrarToast(toast) {
    toast.classList.remove("show");
    setTimeout(() => toast.remove(), 400);
}