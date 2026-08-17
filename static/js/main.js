// sweepKart Interactive JS & Asynchronous Cart Updates

document.addEventListener('DOMContentLoaded', function () {
    // Intercept all Add-to-Cart form submissions for seamless AJAX execution
    const addToCartForms = document.querySelectorAll('form[action*="/cart/add/"]');

    addToCartForms.forEach(function (form) {
        form.addEventListener('submit', function (e) {
            e.preventDefault();

            const actionUrl = form.action;
            const formData = new FormData(form);

            fetch(actionUrl, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Accept': 'application/json'
                }
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // 1. Trigger Floating Glassmorphic Toast Notification
                        showGlassToast(data.message || '✓ Added to cart!');

                        // 2. Update Navbar Cart Badge dynamically & trigger bounce animation
                        updateCartBadge(data.cart_item_count);
                    } else {
                        showGlassToast(data.message || 'Could not add item to cart', 'error');
                    }
                })
                .catch(error => {
                    console.error('Cart submission error:', error);
                    // Fallback to normal form submission if fetch fails
                    form.submit();
                });
        });
    });
});

/**
 * Updates the navbar cart count badge and plays a bounce keyframe animation
 */
function updateCartBadge(count) {
    const badgeElement = document.querySelector('.navbar .badge');
    const cartLink = document.querySelector('a[href*="/cart/"]');

    if (badgeElement) {
        badgeElement.textContent = count;
        badgeElement.classList.add('cart-badge-bounce');
        setTimeout(() => badgeElement.classList.remove('cart-badge-bounce'), 600);
    } else if (cartLink && count > 0) {
        const newBadge = document.createElement('span');
        newBadge.className = 'position-absolute top-0 start-100 translate-middle badge rounded-pill bg-warning text-dark fw-bold cart-badge-bounce';
        newBadge.textContent = count;
        cartLink.appendChild(newBadge);
        setTimeout(() => newBadge.classList.remove('cart-badge-bounce'), 600);
    }
}

/**
 * Renders a floating glassmorphic toast in bottom-right corner
 */
function showGlassToast(message, type = 'success') {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'position-fixed bottom-0 end-0 p-3';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    const bgClass = type === 'error' ? 'bg-danger text-white' : 'bg-success text-white';
    toast.className = `glass-toast p-3 rounded-3 shadow-lg ${bgClass} d-flex align-items-center gap-2 mb-2 fade-in`;
    toast.style.minWidth = '260px';
    toast.innerHTML = `
        <i class="bi ${type === 'error' ? 'bi-exclamation-triangle-fill' : 'bi-check-circle-fill'} fs-5"></i>
        <div class="fw-semibold small flex-grow-1">${message}</div>
        <button type="button" class="btn-close btn-close-white small ms-2" onclick="this.parentElement.remove()"></button>
    `;

    container.appendChild(toast);

    // Auto remove after 3.5 seconds
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transition = 'opacity 0.4s ease';
        setTimeout(() => toast.remove(), 400);
    }, 3500);
}
