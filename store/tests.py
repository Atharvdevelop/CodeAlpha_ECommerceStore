from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from store.models import Category, Product, ProductVariant, Wishlist, Cart, CartItem, Order, OrderItem


class StoreModelTests(TestCase):
    def setUp(self):
        self.parent_cat = Category.objects.create(name="Men")
        self.sub_cat = Category.objects.create(name="Men's Jackets", parent=self.parent_cat)
        self.product = Product.objects.create(
            category=self.sub_cat,
            name="Test Leather Jacket",
            price=3999.00,
            stock=10,
            description="High quality jacket"
        )
        self.variant = ProductVariant.objects.create(
            product=self.product,
            color_name="Black",
            color_code="#000000",
            size="L",
            stock=5,
            price=3999.00
        )

    def test_category_hierarchy_and_slug(self):
        self.assertEqual(self.parent_cat.slug, "men")
        self.assertEqual(self.sub_cat.slug, "mens-jackets")
        self.assertEqual(str(self.sub_cat), "Men > Men's Jackets")

    def test_variant_model_and_cart_calculation(self):
        self.assertEqual(str(self.variant), "Test Leather Jacket (Black / Size L)")
        cart = Cart.objects.create(session_key="test_session")
        cart_item = CartItem.objects.create(cart=cart, product=self.product, variant=self.variant, quantity=2)
        self.assertEqual(cart.get_total_items, 2)
        self.assertEqual(cart.get_total_price, 7998.00)
        self.assertIn("Black", str(cart_item))


class StoreViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="password123")
        self.category = Category.objects.create(name="Electronics")
        self.product = Product.objects.create(
            category=self.category,
            name="Wireless Headphones",
            price=4999.00,
            stock=10
        )
        self.variant = ProductVariant.objects.create(
            product=self.product,
            color_name="Space Silver",
            color_code="#94a3b8",
            stock=5
        )

    def test_home_view(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "sweepKart")
        self.assertContains(response, "Wireless Headphones")

    def test_add_to_cart_with_variant(self):
        response = self.client.post(reverse('add_to_cart', args=[self.product.id]), {
            'quantity': 2,
            'variant_id': self.variant.id
        })
        self.assertRedirects(response, reverse('cart'))

        cart_response = self.client.get(reverse('cart'))
        self.assertEqual(cart_response.status_code, 200)
        self.assertContains(cart_response, "Wireless Headphones")
        self.assertContains(cart_response, "Space Silver")

    def test_wishlist_toggle_view(self):
        self.client.login(username="testuser", password="password123")
        response = self.client.post(
            reverse('wishlist_toggle', args=[self.product.id]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertTrue(json_data['success'])
        self.assertTrue(json_data['added'])
        self.assertEqual(json_data['wishlist_count'], 1)

    def test_search_suggest_api(self):
        response = self.client.get(reverse('search_suggest') + '?q=Wire')
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertTrue(len(json_data['results']) > 0)
        self.assertEqual(json_data['results'][0]['name'], "Wireless Headphones")

    def test_checkout_and_stock_deduction(self):
        self.client.login(username="testuser", password="password123")
        self.client.post(reverse('add_to_cart', args=[self.product.id]), {
            'quantity': 2,
            'variant_id': self.variant.id
        })

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
        self.assertEqual(order.total_price, 9998.00)
        self.assertRedirects(response, reverse('order_confirm', args=[order.id]))

        # Verify variant stock deduction
        self.variant.refresh_from_db()
        self.assertEqual(self.variant.stock, 3)

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



