import logging
from io import BytesIO
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db import transaction
from django.db.models import Q

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from .models import Category, Product, ProductVariant, Wishlist, Cart, CartItem, Order, OrderItem, Review
from .forms import RegisterForm, LoginForm, CheckoutForm, ReviewForm

logger = logging.getLogger(__name__)


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
                        variant=item.variant,
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

    wishlist_ids = set()
    wishlist_count = 0
    if request.user.is_authenticated:
        wishlist_ids = set(Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True))
        wishlist_count = len(wishlist_ids)

    parent_categories = Category.objects.filter(parent__isnull=True).prefetch_related('subcategories')

    return {
        'cart_item_count': count,
        'nav_categories': parent_categories,
        'user_wishlist_ids': wishlist_ids,
        'wishlist_count': wishlist_count,
    }


def home_view(request):
    products = Product.objects.filter(is_active=True).select_related('category', 'category__parent').prefetch_related('variants')
    categories = Category.objects.all().select_related('parent')

    # Category Filtering (supports parent category or specific subcategory)
    selected_category_slug = request.GET.get('category')
    selected_category = None
    if selected_category_slug:
        selected_category = Category.objects.filter(slug=selected_category_slug).first()
        if selected_category:
            products = products.filter(
                Q(category=selected_category) | Q(category__parent=selected_category)
            )

    # Search
    search_query = request.GET.get('q')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(category__name__icontains=search_query) |
            Q(category__parent__name__icontains=search_query)
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
        'selected_category': selected_category,
        'selected_category_slug': selected_category_slug,
        'search_query': search_query,
        'min_price': min_price,
        'max_price': max_price,
    }
    return render(request, 'store/home.html', context)


def search_suggest_view(request):
    query = request.GET.get('q', '').strip()
    if not query or len(query) < 2:
        return JsonResponse({'results': []})

    products = Product.objects.filter(is_active=True).filter(
        Q(name__icontains=query) | Q(category__name__icontains=query) | Q(category__parent__name__icontains=query)
    ).select_related('category')[:6]

    results = []
    for p in products:
        results.append({
            'id': p.id,
            'name': p.name,
            'price': str(p.price),
            'slug': p.slug,
            'category': p.category.name,
            'image_url': p.image.url if p.image else '',
        })

    return JsonResponse({'results': results})


def product_detail_view(request, slug):
    product = get_object_or_404(Product.objects.prefetch_related('variants', 'reviews__user'), slug=slug, is_active=True)
    related_products = Product.objects.filter(category=product.category, is_active=True).exclude(id=product.id).prefetch_related('variants')[:4]
    reviews = product.reviews.all()
    review_form = ReviewForm()

    variants = list(product.variants.all())
    variants_data = []
    for v in variants:
        variants_data.append({
            'id': v.id,
            'color_name': v.color_name,
            'color_code': v.color_code,
            'size': v.size,
            'stock': v.stock,
            'price': str(v.price) if v.price else str(product.price),
            'image_url': v.variant_image.url if v.variant_image else (product.image.url if product.image else ''),
        })

    is_wishlisted = False
    if request.user.is_authenticated:
        is_wishlisted = Wishlist.objects.filter(user=request.user, product=product).exists()

    context = {
        'product': product,
        'variants': variants,
        'variants_json': variants_data,
        'related_products': related_products,
        'reviews': reviews,
        'review_form': review_form,
        'is_wishlisted': is_wishlisted,
    }
    return render(request, 'store/product_detail.html', context)


@login_required
def wishlist_toggle_view(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    wishlist_item = Wishlist.objects.filter(user=request.user, product=product).first()
    
    if wishlist_item:
        wishlist_item.delete()
        added = False
        message = f"Removed {product.name} from your Wishlist."
    else:
        Wishlist.objects.create(user=request.user, product=product)
        added = True
        message = f"Added {product.name} to your Wishlist!"

    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or 'application/json' in request.headers.get('Accept', '')
    if is_ajax:
        wishlist_count = Wishlist.objects.filter(user=request.user).count()
        return JsonResponse({
            'success': True,
            'added': added,
            'message': message,
            'wishlist_count': wishlist_count
        })

    messages.info(request, message)
    return redirect(request.META.get('HTTP_REFERER', 'home'))


@login_required
def wishlist_view(request):
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product', 'product__category').prefetch_related('product__variants')
    return render(request, 'store/wishlist.html', {'wishlist_items': wishlist_items})


@login_required
def add_review_view(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id, is_active=True)
        form = ReviewForm(request.POST)
        if form.is_valid():
            Review.objects.create(
                product=product,
                user=request.user,
                rating=int(form.cleaned_data['rating']),
                comment=form.cleaned_data['comment']
            )
            messages.success(request, "Thank you! Your product review has been posted.")
        else:
            messages.error(request, "Please enter a valid review comment.")
        return redirect('product_detail', slug=product.slug)
    return redirect('home')


def cart_view(request):
    cart = get_or_create_cart(request)
    cart_items = cart.items.select_related('product', 'variant').all()
    context = {
        'cart': cart,
        'cart_items': cart_items,
    }
    return render(request, 'store/cart.html', context)


def add_to_cart_view(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id, is_active=True)
        variant_id = request.POST.get('variant_id')
        variant = None
        
        if variant_id:
            variant = get_object_or_404(ProductVariant, id=variant_id, product=product)

        try:
            quantity = int(request.POST.get('quantity', 1))
            if quantity <= 0:
                if request.headers.get('x-requested-with') == 'XMLHttpRequest' or 'application/json' in request.headers.get('Accept', ''):
                    return JsonResponse({'success': False, 'message': 'Please enter a valid positive quantity.'}, status=400)
                messages.error(request, "Please enter a valid positive quantity.")
                return redirect('product_detail', slug=product.slug)
        except (ValueError, TypeError):
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or 'application/json' in request.headers.get('Accept', ''):
                return JsonResponse({'success': False, 'message': 'Invalid quantity provided.'}, status=400)
            messages.error(request, "Invalid quantity provided.")
            return redirect('product_detail', slug=product.slug)

        available_stock = variant.stock if variant else product.stock

        if quantity > available_stock:
            msg = f"Only {available_stock} left in stock for this selection."
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or 'application/json' in request.headers.get('Accept', ''):
                return JsonResponse({'success': False, 'message': msg}, status=400)
            messages.error(request, msg)
            return redirect('product_detail', slug=product.slug)

        cart = get_or_create_cart(request)
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            variant=variant,
            defaults={'quantity': quantity}
        )

        if not created:
            if (cart_item.quantity + quantity) > available_stock:
                msg = f"Cannot add more. Stock limit of {available_stock} reached."
                if request.headers.get('x-requested-with') == 'XMLHttpRequest' or 'application/json' in request.headers.get('Accept', ''):
                    return JsonResponse({'success': False, 'message': msg}, status=400)
                messages.warning(request, msg)
                return redirect('cart')
            cart_item.quantity += quantity
            cart_item.save()

        # Check for AJAX request
        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or 'application/json' in request.headers.get('Accept', '')
        if is_ajax:
            item_desc = f"{product.name} ({variant})" if variant else product.name
            return JsonResponse({
                'success': True,
                'cart_item_count': cart.get_total_items,
                'message': f'✓ Added {item_desc} to cart!'
            })

        messages.success(request, f"Added {product.name} to your cart!")
        return redirect('cart')

    return redirect('home')



def update_cart_view(request, item_id):
    if request.method == 'POST':
        cart = get_or_create_cart(request)
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
        try:
            quantity = int(request.POST.get('quantity', 1))
        except (ValueError, TypeError):
            messages.error(request, "Invalid quantity provided.")
            return redirect('cart')

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
    cart_items = cart.items.select_related('product', 'variant').all()

    if not cart_items.exists():
        messages.warning(request, "Your cart is empty. Add items before checking out.")
        return redirect('home')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Lock product and variant rows and verify stock
                    for item in cart_items:
                        product_locked = Product.objects.select_for_update().get(id=item.product.id)
                        if item.variant:
                            variant_locked = ProductVariant.objects.select_for_update().get(id=item.variant.id)
                            if item.quantity > variant_locked.stock:
                                raise ValueError(f"Insufficient stock for {product_locked.name} ({variant_locked.color_name} {variant_locked.size or ''}). Only {variant_locked.stock} remaining.")
                        else:
                            if item.quantity > product_locked.stock:
                                raise ValueError(f"Insufficient stock for {product_locked.name}. Only {product_locked.stock} remaining.")

                    order = form.save(commit=False)
                    order.user = request.user
                    order.total_price = cart.get_total_price
                    order.status = 'Pending'
                    order.save()

                    for item in cart_items:
                        product_locked = Product.objects.select_for_update().get(id=item.product.id)
                        variant_locked = None
                        v_info = ""
                        if item.variant:
                            variant_locked = ProductVariant.objects.select_for_update().get(id=item.variant.id)
                            variant_locked.stock -= item.quantity
                            variant_locked.save()
                            v_info = str(item.variant)

                        OrderItem.objects.create(
                            order=order,
                            product=product_locked,
                            variant=variant_locked,
                            product_name=product_locked.name,
                            variant_info=v_info,
                            price=item.unit_price,
                            quantity=item.quantity
                        )
                        # Deduct main product stock
                        product_locked.stock = max(0, product_locked.stock - item.quantity)
                        product_locked.save()

                    # Clear cart
                    cart_items.delete()

                messages.success(request, f"Order #{order.id} placed successfully!")
                return redirect('order_confirm', order_id=order.id)

            except ValueError as e:
                messages.error(request, str(e))
            except Exception as e:
                logger.exception("Unexpected error occurred during checkout processing:")
                messages.error(request, "An unexpected error occurred while placing your order. Please try again.")
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


@login_required
def download_invoice_view(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    story = []
    styles = getSampleStyleSheet()

    # Title / Header
    title_style = ParagraphStyle(
        'InvoiceTitle',
        parent=styles['Heading1'],
        fontSize=22,
        textColor=colors.HexColor('#2874f0'),
        spaceAfter=12
    )
    story.append(Paragraph("sweepKart — Official Tax Invoice", title_style))
    story.append(Paragraph(f"<b>Order Reference:</b> #{order.id} | <b>Date:</b> {order.created_at.strftime('%B %d, %Y - %H:%M')}", styles['Normal']))
    story.append(Spacer(1, 14))

    # Customer Details
    cust_info = f"<b>Shipping Address:</b><br/><b>{order.full_name}</b><br/>{order.address}<br/>{order.city}, {order.postal_code}, {order.country}<br/>Email: {order.email}"
    story.append(Paragraph(cust_info, styles['Normal']))
    story.append(Spacer(1, 16))

    # Items Table
    data = [["Product Description", "Unit Price", "Qty", "Total Amount"]]
    for item in order.items.all():
        data.append([item.product_name, f"Rs. {item.price}", str(item.quantity), f"Rs. {item.get_cost}"])

    data.append(["", "", "Grand Total:", f"Rs. {order.total_price}"])

    t = Table(data, colWidths=[240, 90, 60, 110])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2874f0')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -2), colors.HexColor('#f8fafc')),
        ('GRID', (0, 0), (-1, -2), 0.5, colors.HexColor('#e0e0e0')),
        ('FONTNAME', (2, -1), (-1, -1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (3, -1), (3, -1), colors.HexColor('#2874f0')),
    ]))
    story.append(t)
    story.append(Spacer(1, 20))
    story.append(Paragraph("Thank you for shopping with sweepKart! For support, contact support@sweepkart.com.", styles['Italic']))

    doc.build(story)
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="sweepKart_Invoice_Order_{order.id}.pdf"'
    return response


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
