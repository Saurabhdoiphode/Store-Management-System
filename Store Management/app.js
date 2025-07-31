let currentCustomer = null;
let cart = [];
let selectedProduct = null;

function openTab(evt, tabName) {
    const tabcontent = document.getElementsByClassName("tabcontent");
    for (let i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }

    const tablinks = document.getElementsByClassName("tablinks");
    for (let i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }

    document.getElementById(tabName).style.display = "block";
    evt.currentTarget.className += " active";
}

function loadProducts() {
    const category = document.getElementById("productCategory").value;
    if (!category) return;

    fetch('http://localhost:8000/api/products', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ category: category })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        const container = document.getElementById("productsContainer");
        container.innerHTML = '';

        if (data.error) {
            showStatus('customerStatus', data.error, 'error');
            return;
        }

        if (!data.products || data.products.length === 0) {
            container.innerHTML = '<p>No products found in this category</p>';
            return;
        }

        data.products.forEach(product => {
            const productCard = document.createElement("div");
            productCard.className = "product-card";
            productCard.innerHTML = `
                <h3>${product.name}</h3>
                <p>Price: ₹${product.price.toFixed(2)}/${product.unit}</p>
                <p>Stock: ${product.stock_quantity} ${product.unit}</p>
                <button onclick="selectProduct(${product.product_id})">Select</button>
            `;
            container.appendChild(productCard);
        });
    })
    .catch(error => {
        showStatus('customerStatus', 'Error loading products: ' + error.message, 'error');
        console.error('Error:', error);
    });
}

function selectProduct(productId) {
    fetch('http://localhost:8000/api/product', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ product_id: productId })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        if (data.error) {
            showStatus('productStatus', data.error, 'error');
            return;
        }

        if (!data.product) {
            showStatus('productStatus', 'Product not found', 'error');
            return;
        }

        selectedProduct = data.product;
        document.getElementById("productDetails").innerHTML = `
            <p><strong>${data.product.name}</strong></p>
            <p>Price: ₹${data.product.price.toFixed(2)} per ${data.product.unit}</p>
            <p>Available: ${data.product.stock_quantity} ${data.product.unit}</p>
        `;

        const quantityInput = document.getElementById("productQuantity");
        if (data.product.unit === 'kg') {
            quantityInput.step = "0.1";
        } else {
            quantityInput.step = "1";
        }
        quantityInput.max = data.product.stock_quantity;
        quantityInput.value = "1";

        document.getElementById("productDetailsCard").classList.remove("hidden");
    })
    .catch(error => {
        showStatus('productStatus', 'Error loading product: ' + error.message, 'error');
        console.error('Error:', error);
    });
}

// ... [rest of the app.js code remains the same] ...

// Customer registration
document.getElementById("customerName").addEventListener("change", function() {
    const name = this.value.trim();
    const phone = document.getElementById("customerPhone").value.trim();

    if (name && phone) {
        registerCustomer(name, phone);
    }
});

document.getElementById("customerPhone").addEventListener("change", function() {
    const phone = this.value.trim();
    const name = document.getElementById("customerName").value.trim();

    if (name && phone) {
        registerCustomer(name, phone);
    }
});

function registerCustomer(name, phone) {
    fetch('http://localhost:8000/api/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name, phone })
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(err => { throw new Error(err.error || 'Registration failed'); });
        }
        return response.json();
    })
    .then(data => {
        currentCustomer = {
            user_id: data.user_id,
            name: name,
            phone: phone
        };

        showStatus('customerStatus', `Customer registered (ID: ${data.user_id})`, 'success');
    })
    .catch(error => {
        showStatus('customerStatus', 'Error registering customer: ' + error.message, 'error');
        console.error('Error:', error);
    });
}

// ... [rest of the app.js code remains the same] ...