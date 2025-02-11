document.addEventListener('DOMContentLoaded', function() {
    // Cargar datos de usuario
    fetch('/usuario-info/')
        .then(response => response.json())
        .then(data => {
            if (data.usuario) {
                document.getElementById('id_nombre').value = data.usuario.first_name;
                document.getElementById('id_apellido').value = data.usuario.last_name;
                document.getElementById('id_email').value = data.usuario.email;
                document.getElementById('id_telefono').value = data.usuario.numero;
                document.getElementById('id_direccion').value = data.usuario.direccion;
            }
        })
        .catch(error => console.error('Error:', error));
    
    const carrito = JSON.parse(localStorage.getItem('carrito') || '[]');
    actualizarResumenPedido(carrito);
    
    // Actualizar el input hidden con los datos del carrito
    document.getElementById('carrito_data').value = JSON.stringify(carrito);
    
    document.getElementById('form-pasarela').addEventListener('submit', async function(e) {
        e.preventDefault();
        
        if (carrito.length === 0) {
            alert('Tu carrito está vacío');
            return;
        }
        
        const municipio = document.getElementById('id_municipio').value;
        const metodoPago = document.querySelector('input[name="metodo_pago"]:checked');
        
        if (!municipio || municipio === '') {
            alert('Por favor selecciona un municipio');
            return;
        }
        
        if (!metodoPago) {
            alert('Por favor selecciona un método de pago');
            return;
        }

        const formData = new FormData(this);
        
        try {
            const response = await fetch('/pasarela/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                localStorage.removeItem('carrito');
                alert('Pedido realizado con éxito, espere confirmación por correo electrónico');
                window.location.href = '/perfil/';
            } else {
                alert(data.message || 'Error al procesar la orden');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error al procesar tu pedido');
        }
    });
});

function actualizarResumenPedido(carrito) {
    const subtotal = carrito.reduce((sum, item) => sum + (item.precio * item.cantidad), 0);
    const envio = 3000;
    const total = subtotal + envio;
    
    // Crear resumen de items
    let resumenHTML = '<div class="resumen-pedido">';
    
    // Agregar cada item
    carrito.forEach(item => {
        resumenHTML += `
            <div class="item-resumen">
                <div class="item-info">
                    <span class="item-nombre">${item.nombre}</span>
                    <span class="item-cantidad">x${item.cantidad}</span>
                </div>
                <span class="item-precio">$${(item.precio * item.cantidad).toLocaleString()}</span>
            </div>
        `;
    });
    
    // Agregar subtotal y envío
    resumenHTML += `
        <div class="subtotal-row">
            <span>Subtotal</span>
            <span>$${subtotal.toLocaleString()}</span>
        </div>
        <div class="envio-row">
            <span>Envío</span>
            <span>$${envio.toLocaleString()}</span>
        </div>
    </div>`;
    
    // Encontrar el contenedor del total e insertar el resumen antes
    const totalSection = document.querySelector('.total-section');
    if (totalSection) {
        const totalSpan = document.getElementById('total');
        if (totalSpan) {
            totalSpan.textContent = `$${total.toLocaleString()}`;
        }
        
        // Remover resumen anterior si existe
        const resumenExistente = totalSection.querySelector('.resumen-pedido');
        if (resumenExistente) {
            resumenExistente.remove();
        }
        
        // Insertar nuevo resumen
        totalSection.insertAdjacentHTML('afterbegin', resumenHTML);
    }
}

document.getElementById('form-pasarela').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const carritoData = localStorage.getItem('carrito');
    if (!carritoData || JSON.parse(carritoData).length === 0) {
        alert('Tu carrito está vacío');
        return;
    }

    const municipio = document.getElementById('id_municipio').value;
    const metodoPago = document.querySelector('input[name="metodo_pago"]:checked');
    
    if (!municipio || municipio === '') {
        alert('Por favor selecciona un municipio');
        return;
    }
    
    if (!metodoPago) {
        alert('Por favor selecciona un método de pago');
        return;
    }

    // Add carrito data to form
    document.getElementById('carrito_data').value = carritoData;
    
    const formData = new FormData(this);

    try {
        const response = await fetch('/message-pasarela/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            localStorage.removeItem('carrito'); // Clear cart
            window.location.href = data.redirect;
        } else {
            alert(data.message);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Hubo un error al procesar tu pedido.');
    }
});