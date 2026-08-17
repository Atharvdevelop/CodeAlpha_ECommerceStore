from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from store.models import Category, Product, Cart, CartItem, Order, OrderItem


class StoreModelTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Gadgets")
        self.product = Product.objects.create(
            category=self.category,
            name="Test Headphones",
            price=1999.00,
            stock=10,
            description="High quality test headphones"
        )

    def test_category_and_product_slug_generation(self):
        self.assertEqual(self.category.slug, "gadgets")
        self.assertEqual(self.product.slug, "test-headphones")
        self.assertTrue(self.product.in_stock)

    def test_cart_total_price_calculation(self):
        cart = Cart.objects.create(session_key="test_session")
        CartItem.objects.create(cart=cart, product=self.product, quantity=2)
        self.assertEqual(cart.get_total_items, 2)
        self.assertEqual(cart.get_total_price, 3998.00)


class StoreViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="password123")
        self.category = Category.objects.create(name="Tech")
        self.product = Product.objects.create(
            category=self.category,
            name="Laptop Stand",
            price=999.00,
            stock=5
        )

    def test_home_view(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "sweepKart")
        self.assertContains(response, "Laptop Stand")

    def test_add_to_cart_flow(self):
        response = self.client.post(reverse('add_to_cart', args=[self.product.id]), {'quantity': 2})
        self.assertRedirects(response, reverse('cart'))

        cart_response = self.client.get(reverse('cart'))
        self.assertEqual(cart_response.status_code, 200)
        self.assertContains(cart_response, "Laptop Stand")
        self.assertContains(cart_response, "1998.00")

    def test_checkout_and_stock_deduction(self):
        self.client.login(username="testuser", password="password123")
        self.client.post(reverse('add_to_cart', args=[self.product.id]), {'quantity': 2})

        checkout_data = {
            'full_name': 'Test User',
            'email': 'test@example.com',
            'address': '123 Test St',
            'city': 'Test City',
            'postal_code': '123456',
            'country': 'India',
        }
        response = self.client.post(reverse('checkout'), checkout_data)
        
        # Verify order creation
        order = Order.objects.get(user=self.user)
        self.assertEqual(order.total_price, 1998.00)
        self.assertRedirects(response, reverse('order_confirm', args=[order.id]))

        # Verify stock deduction
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 3)

    def test_ajax_add_to_cart(self):
        response = self.client.post(
            reverse('add_to_cart', args=[self.product.id]),
            {'quantity': 1},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertTrue(json_data['success'])
        self.assertEqual(json_data['cart_item_count'], 1)

    def test_review_submission(self):
        self.client.login(username="testuser", password="password123")
        review_data = {
            'rating': 5,
            'comment': 'Awesome laptop stand!'
        }
        response = self.client.post(reverse('add_review', args=[self.product.id]), review_data)
        self.assertRedirects(response, reverse('product_detail', args=[self.product.slug]))
        self.assertEqual(self.product.reviews.count(), 1)

    def test_download_pdf_invoice(self):
        self.client.login(username="testuser", password="password123")
        order = Order.objects.create(
            user=self.user,
            full_name="Test User",
            email="test@example.com",
            address="123 Test St",
            city="Test City",
            postal_code="123456",
            total_price=999.00
        )
        OrderItem.objects.create(order=order, product=self.product, product_name=self.product.name, price=999.00, quantity=1)

        response = self.client.get(reverse('download_invoice', args=[order.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')


