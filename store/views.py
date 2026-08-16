from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from .models import Category, Product, Cart, CartItem, Order, OrderItem
from .forms import RegisterForm, LoginForm, CheckoutForm


def _get_session_key(request):
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key


def get_or_create_cart(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        # Check if there is an anonymous session cart to merge
        session_key = request.session.session_key
        if session_key:
            session_cart = Cart.objects.filter(session_key=session_key, user__isnull=True).first()
            if session_cart and session_cart != cart:
                for item in session_cart.items.all():
                    cart_item, item_created = CartItem.objects.get_or_create(
                        cart=cart,
                        product=item.product,
                        defaults={'quantity': item.quantity}
                    )
                    if not item_created:
                        cart_item.quantity += item.quantity
                        cart_item.save()
                session_cart.delete()
        return cart
    else:
        session_key = _get_session_key(request)
        cart, created = Cart.objects.get_or_create(session_key=session_key, user__isnull=True)
        return cart


def cart_context_processor(request):
    try:
        cart = get_or_create_cart(request)
        count = cart.get_total_items
    except Exception:
        count = 0
    return {'cart_item_count': count}


def home_view(request):
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.all()

    # Filtering
    selected_category_slug = request.GET.get('category')
    if selected_category_slug:
        products = products.filter(category__slug=selected_category_slug)

    # Search
    search_query = request.GET.get('q')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )

    # Price filter
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        try:
            products = products.filter(price__gte=float(min_price))
        except ValueError:
            pass
    if max_price:
        try:
            products = products.filter(price__lte=float(max_price))
        except ValueError:
            pass

    context = {
        'products': products,
        'categories': categories,
        'selected_category_slug': selected_category_slug,
        'search_query': search_query,
        'min_price': min_price,
        'max_price': max_price,
    }
    return render(request, 'store/home.html', context)


def product_detail_view(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    related_products = Product.objects.filter(category=product.category, is_active=True).exclude(id=product.id)[:4]
    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'store/product_detail.html', context)


def cart_view(request):
    cart = get_or_create_cart(request)
    cart_items = cart.items.select_related('product').all()
    context = {
        'cart': cart,
        'cart_items': cart_items,
    }
    return render(request, 'store/cart.html', context)


def add_to_cart_view(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id, is_active=True)
        quantity = int(request.POST.get('quantity', 1))

        if quantity > product.stock:
            messages.error(request, f"Sorry, only {product.stock} items in stock for {product.name}.")
            return redirect('product_detail', slug=product.slug)

        cart = get_or_create_cart(request)
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )

        if not created:
            if (cart_item.quantity + quantity) > product.stock:
                messages.warning(request, f"Cannot add more. Stock limit of {product.stock} reached.")
                return redirect('cart')
            cart_item.quantity += quantity
            cart_item.save()

        messages.success(request, f"Added {product.name} to your cart!")
        return redirect('cart')

    return redirect('home')


def update_cart_view(request, item_id):
    if request.method == 'POST':
        cart = get_or_create_cart(request)
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
        quantity = int(request.POST.get('quantity', 1))

        if quantity <= 0:
            cart_item.delete()
            messages.info(request, "Item removed from cart.")
        elif quantity > cart_item.product.stock:
            messages.warning(request, f"Only {cart_item.product.stock} available in stock.")
            cart_item.quantity = cart_item.product.stock
            cart_item.save()
        else:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, "Cart updated.")

    return redirect('cart')


def remove_from_cart_view(request, item_id):
    if request.method == 'POST':
        cart = get_or_create_cart(request)
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
        cart_item.delete()
        messages.info(request, "Item removed from your cart.")
    return redirect('cart')


@login_required
def checkout_view(request):
    cart = get_or_create_cart(request)
    cart_items = cart.items.select_related('product').all()

    if not cart_items.exists():
        messages.warning(request, "Your cart is empty. Add items before checking out.")
        return redirect('home')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Check stock for all items
                    for item in cart_items:
                        if item.quantity > item.product.stock:
                            raise ValueError(f"Insufficient stock for {item.product.name}. Only {item.product.stock} left.")

                    order = form.save(commit=False)
                    order.user = request.user
                    order.total_price = cart.get_total_price
                    order.status = 'Pending'
                    order.save()

                    for item in cart_items:
                        OrderItem.objects.create(
                            order=order,
                            product=item.product,
                            product_name=item.product.name,
                            price=item.product.price,
                            quantity=item.quantity
                        )
                        # Deduct stock
                        item.product.stock -= item.quantity
                        item.product.save()

                    # Clear cart
                    cart_items.delete()

                messages.success(request, f"Order #{order.id} placed successfully!")
                return redirect('order_confirm', order_id=order.id)

            except ValueError as e:
                messages.error(request, str(e))
            except Exception as e:
                messages.error(request, f"An error occurred while processing your order: {e}")
    else:
        initial_data = {
            'full_name': f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
            'email': request.user.email,
        }
        form = CheckoutForm(initial=initial_data)

    context = {
        'form': form,
        'cart': cart,
        'cart_items': cart_items,
    }
    return render(request, 'store/checkout.html', context)


@login_required
def order_confirm_view(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    context = {
        'order': order,
        'order_items': order.items.all(),
    }
    return render(request, 'store/order_confirm.html', context)


@login_required
def order_history_view(request):
    orders = Order.objects.filter(user=request.user)
    context = {
        'orders': orders,
    }
    return render(request, 'store/order_history.html', context)


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to sweepKart, {user.username}!")
            return redirect('home')
    else:
        form = RegisterForm()

    return render(request, 'store/auth/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            next_url = request.GET.get('next') or 'home'
            return redirect(next_url)
    else:
        form = LoginForm()

    return render(request, 'store/auth/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('home')

