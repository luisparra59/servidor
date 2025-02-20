document.addEventListener("DOMContentLoaded", function () {
    const ITEMS_PER_PAGE = 12;
    let currentPage = 1;
    let currentCategory = "todos";
    let productos = [];
    let carrito = JSON.parse(localStorage.getItem("carrito")) || [];

    async function fetchProducts() {
        try {
            const response = await fetch("/api/productos/");
            productos = await response.json();
            updateDisplay();
        } catch (error) {
            console.error("Error al cargar productos:", error);
        }
    }

    function filterProducts(category) {
        console.log('Filtering by category:', category); // Para debugging
        if (category === "todos") {
            return productos;
        }
        return productos.filter(p => p.categoria === category);
    }

    function displayProducts(products, page) {
        const start = (page - 1) * ITEMS_PER_PAGE;
        const paginatedProducts = products.slice(start, start + ITEMS_PER_PAGE);
        const container = document.getElementById("productos-container");
        container.innerHTML = "";
    
        paginatedProducts.forEach(product => {
            // Verificar disponibilidad
            const stockAvailable = product.available_units > 0;
            const stockText = stockAvailable ? 
                `<span class="text-success">${product.available_units} unidades disponibles</span>` : 
                '<span class="text-danger">Agotado</span>';
    
            container.innerHTML += `
                <div class="producto" data-categoria="${product.categoria}">
                    <img src="/media/${product.imagen}" alt="${product.nombre}">
                    <h2>${product.nombre}</h2>
                    <p>${product.descripcion}</p>
                    <div class="precio">
                        <p>$${product.precio} ${stockText}</p>
                        <button class="btn-comprar btn ${stockAvailable ? 'btn-success' : 'btn-secondary'}" 
                            ${stockAvailable ? `
                                data-bs-toggle="modal" 
                                data-bs-target="#productModal"
                            ` : 'disabled'}
                            data-id="${product.id}"
                            data-title="${product.nombre}"
                            data-description="${product.descripcion}"
                            data-price="${product.precio}"
                            data-stock="${product.available_units}"
                            data-image="/media/${product.imagen}">
                            ${stockAvailable ? 'Comprar' : 'Agotado'}
                        </button>
                    </div>
                </div>
            `;
        });
    }

    function updatePagination(products) {
        const totalPages = Math.ceil(products.length / ITEMS_PER_PAGE);
        const paginationContainer = document.getElementById("pagination");
        paginationContainer.innerHTML = "";

        // Botón "Anterior"
        const prevButton = document.createElement("li");
        prevButton.className = `page-item ${currentPage === 1 ? 'disabled' : ''}`;
        prevButton.innerHTML = `
            <a class="page-link" href="#" aria-label="Previous">
                <span aria-hidden="true">&laquo;</span>
            </a>
        `;
        prevButton.addEventListener('click', (e) => {
            e.preventDefault();
            if (currentPage > 1) {
                currentPage--;
                updateDisplay();
            }
        });
        paginationContainer.appendChild(prevButton);

        // Números de página
        for (let i = 1; i <= totalPages; i++) {
            const pageItem = document.createElement("li");
            pageItem.className = `page-item ${currentPage === i ? 'active' : ''}`;
            pageItem.innerHTML = `<a class="page-link" href="#">${i}</a>`;
            pageItem.addEventListener('click', (e) => {
                e.preventDefault();
                currentPage = i;
                updateDisplay();
            });
            paginationContainer.appendChild(pageItem);
        }

        // Botón "Siguiente"
        const nextButton = document.createElement("li");
        nextButton.className = `page-item ${currentPage === totalPages ? 'disabled' : ''}`;
        nextButton.innerHTML = `
            <a class="page-link" href="#" aria-label="Next">
                <span aria-hidden="true">&raquo;</span>
            </a>
        `;
        nextButton.addEventListener('click', (e) => {
            e.preventDefault();
            if (currentPage < totalPages) {
                currentPage++;
                updateDisplay();
            }
        });
        paginationContainer.appendChild(nextButton);
    }

    function updateDisplay() {
        const filteredProducts = filterProducts(currentCategory);
        displayProducts(filteredProducts, currentPage);
        updatePagination(filteredProducts);
    }

    const modal = document.getElementById("productModal");
    const quantityInput = document.getElementById("quantity");
    const addToCartBtn = document.getElementById("addToCartBtn");

    function resetModalAndScroll() {
        document.body.classList.remove('modal-open');
        document.body.style.overflow = '';
        document.body.style.paddingRight = '';
        const backdrops = document.querySelectorAll('.modal-backdrop');
        backdrops.forEach(backdrop => backdrop.remove());
    }

    modal.addEventListener("show.bs.modal", function (event) {
        const button = event.relatedTarget;
        const stock = parseInt(button.getAttribute("data-stock"));
        
        modal.querySelector("#productTitle").textContent = button.getAttribute("data-title");
        modal.querySelector("#productDescription").textContent = button.getAttribute("data-description");
        modal.querySelector("#productPrice").textContent = `$${button.getAttribute("data-price")}`;
        modal.querySelector("#productImage").src = button.getAttribute("data-image");
        modal.setAttribute("data-product-id", button.getAttribute("data-id"));
        modal.setAttribute("data-stock", stock);

        // Mostrar stock disponible en el modal
        const stockInfo = document.getElementById("stockInfo");
        if (stockInfo) {
            stockInfo.textContent = `Stock disponible: ${stock} unidades`;
        }

        // Resetear cantidad a 1
        quantityInput.value = 1;
        quantityInput.max = stock; // Establecer máximo según el stock
    });

    modal.addEventListener('hidden.bs.modal', function () {
        resetModalAndScroll();
    });

    if (addToCartBtn) {
        addToCartBtn.addEventListener("click", function () {
            const id = modal.getAttribute("data-product-id");
            const stock = parseInt(modal.getAttribute("data-stock"));
            const cantidad = parseInt(quantityInput.value);

            // Verificar si hay suficiente stock
            if (cantidad > stock) {
                alert(`Lo sentimos, solo hay ${stock} unidades disponibles.`);
                return;
            }

            // Verificar si ya hay productos en el carrito
            const existingProduct = carrito.find(p => p.id === id);
            const cantidadTotal = existingProduct ? 
                existingProduct.cantidad + cantidad : 
                cantidad;

            if (cantidadTotal > stock) {
                alert(`Lo sentimos, no hay suficiente stock. Ya tienes ${existingProduct.cantidad} unidades en el carrito.`);
                return;
            }

            const producto = {
                id: id,
                nombre: modal.querySelector("#productTitle").textContent,
                precio: parseFloat(modal.querySelector("#productPrice").textContent.replace("$", "")),
                imagen: modal.querySelector("#productImage").src,
                cantidad: cantidad,
                stock: stock
            };

            if (existingProduct) {
                existingProduct.cantidad = cantidadTotal;
            } else {
                carrito.push(producto);
            }

            localStorage.setItem("carrito", JSON.stringify(carrito));
            
            // Actualizar el contador del carrito directamente
            const contador = document.getElementById('contador-carrito');
            if (contador) {
                const totalItems = carrito.reduce((total, producto) => total + producto.cantidad, 0);
                if (totalItems > 0) {
                    contador.textContent = totalItems;
                    contador.style.display = 'flex';
                    // Añadir clase para la animación
                    contador.classList.remove('notification-pulse');
                    void contador.offsetWidth; // Forzar reflow
                    contador.classList.add('notification-pulse');
                } else {
                    contador.style.display = 'none';
                }
            }

            const modalInstance = bootstrap.Modal.getInstance(modal);
            if (modalInstance) {
                modalInstance.hide();
                setTimeout(() => {
                    resetModalAndScroll();
                }, 150);
            }

            const alert = document.createElement('div');
            // Establecemos todos los estilos directamente para mayor control
            alert.className = 'alert alert-success';
            alert.style.position = 'fixed';
            alert.style.top = '80px';
            alert.style.right = '20px';
            alert.style.zIndex = '9999';
            alert.style.padding = '10px 15px';
            alert.style.borderRadius = '4px';
            alert.textContent = 'Producto agregado al carrito';
            document.body.appendChild(alert);
            
            setTimeout(() => {
                alert.remove();
            }, 1500);
        });
    }

    document.getElementById("decrementBtn").addEventListener("click", () => {
        const currentVal = parseInt(quantityInput.value);
        if (currentVal > 1) {
            quantityInput.value = currentVal - 1;
        }
    });

    document.getElementById("incrementBtn").addEventListener("click", () => {
        const currentVal = parseInt(quantityInput.value);
        const stock = parseInt(modal.getAttribute("data-stock"));
        if (currentVal < stock) {
            quantityInput.value = currentVal + 1;
        } else {
            alert(`No puedes agregar más unidades. Stock disponible: ${stock}`);
        }
    });

    // Nueva implementación del manejo de categorías
    document.querySelectorAll(".btn-verde").forEach(button => {
        button.addEventListener("click", function() {
            document.querySelectorAll(".btn-verde").forEach(btn => btn.classList.remove("active"));
            this.classList.add("active");
            
            // Nueva forma de obtener la categoría
            const classes = this.className.split(' ');
            const categoryClass = classes.find(cls => 
                ['todos', 'aseo', 'comestibles', 'canastafamiliar', 'papeleria'].includes(cls)
            );
            
            // Mapear las clases a las categorías del modelo
            const categoryMap = {
                'todos': 'todos',
                'aseo': 'aseo',
                'comestibles': 'comestibles',
                'canastafamiliar': 'canasta_familiar',
                'papeleria': 'papeleria'
            };
            
            currentCategory = categoryMap[categoryClass] || 'todos';
            currentPage = 1;
            updateDisplay();
        });
    });

    fetchProducts();
});