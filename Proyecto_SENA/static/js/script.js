// Menu
let menu = document.querySelector('#menu-icon');
let navlist = document.querySelector('.items-navbar');
let cerrarBtn = document.querySelector('.cerrar-icono');

menu.onclick = () => {
    navlist.classList.toggle('open');
}

cerrarBtn.onclick = () => {
    navlist.classList.remove('open');
}

window.onscroll = () => {
    navlist.classList.remove('open');
}

// Función para manejar el dropdown
document.addEventListener('DOMContentLoaded', function() {
    const userIcon = document.querySelector('.nav-user-dropdown .ri-user-line');
    const dropdownContent = document.querySelector('.dropdown-content');
    
    // Función para cerrar el dropdown cuando se hace clic fuera
    document.addEventListener('click', function(event) {
        if (!event.target.closest('.nav-user-dropdown')) {
            dropdownContent.classList.remove('active');
        }
    });

    // Toggle del dropdown al hacer clic en el icono
    userIcon.addEventListener('click', function(event) {
        event.stopPropagation();
        dropdownContent.classList.toggle('active');
    });
});