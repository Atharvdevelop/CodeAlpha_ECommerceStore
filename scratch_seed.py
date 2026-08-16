import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from store.models import Category, Product

print("Seeding database...")

# 1. Create Superuser
if not User.objects.filter(username='admin').exists():
    admin_user = User.objects.create_superuser('admin', 'admin@sweepkart.com', 'admin123')
    print("Created superuser: admin / admin123")

# 2. Create Demo User
if not User.objects.filter(username='demo').exists():
    demo_user = User.objects.create_user('demo', 'demo@sweepkart.com', 'demo123', first_name='Demo', last_name='User')
    print("Created demo user: demo / demo123")

# 3. Create Categories
cat_electronics, _ = Category.objects.get_or_create(name='Electronics')
cat_clothing, _ = Category.objects.get_or_create(name='Clothing')
cat_books, _ = Category.objects.get_or_create(name='Books')
cat_home, _ = Category.objects.get_or_create(name='Home & Kitchen')

# 4. Create Sample Products
products_data = [
    {
        'name': 'Wireless Noise-Canceling Headphones',
        'category': cat_electronics,
        'price': 4999.00,
        'stock': 15,
        'description': 'Experience crystal clear high-fidelity audio with active noise cancellation, 30-hour battery life, and ultra-soft memory foam ear cushions.'
    },
    {
        'name': 'Smart Fitness Watch Series 5',
        'category': cat_electronics,
        'price': 2999.00,
        'stock': 25,
        'description': 'Track your daily activity, heart rate, oxygen levels, and sleep patterns. Features a vibrant AMOLED touchscreen and 5ATM water resistance.'
    },
    {
        'name': 'Ergonomic Mechanical Keyboard RGB',
        'category': cat_electronics,
        'price': 3499.00,
        'stock': 8,
        'description': 'Tactile mechanical switches with customizable per-key RGB backlighting and durable aluminum top frame for ultimate typing performance.'
    },
    {
        'name': 'Ultra-Soft Cotton Hoodie',
        'category': cat_clothing,
        'price': 1499.00,
        'stock': 40,
        'description': 'Premium heavyweight fleece hoodie designed for maximum everyday comfort. Features a lined hood and spacious front kangaroo pocket.'
    },
    {
        'name': 'Slim Fit Denim Jacket',
        'category': cat_clothing,
        'price': 2299.00,
        'stock': 12,
        'description': 'Classic timeless blue denim jacket with button closure, double chest pockets, and durable contrast stitching.'
    },
    {
        'name': 'Clean Code & Architecture Guide',
        'category': cat_books,
        'price': 899.00,
        'stock': 30,
        'description': 'A comprehensive handbook for software engineers on writing clean, scalable, maintainable, and testable code.'
    },
    {
        'name': 'Modern Web Design Masterclass',
        'category': cat_books,
        'price': 699.00,
        'stock': 20,
        'description': 'Learn modern CSS layouts, glassmorphism UI design, responsive grids, and interactive frontend development step-by-step.'
    },
    {
        'name': 'Smart Espresso & Coffee Maker',
        'category': cat_home,
        'price': 7999.00,
        'stock': 5,
        'description': 'Brew cafe-quality espressos, lattes, and cappuccinos at home with 19-bar extraction pressure and built-in milk frother.'
    }
]

for p_data in products_data:
    product, created = Product.objects.get_or_create(
        name=p_data['name'],
        defaults={
            'category': p_data['category'],
            'price': p_data['price'],
            'stock': p_data['stock'],
            'description': p_data['description'],
            'is_active': True,
        }
    )
    if created:
        print(f"Created product: {product.name}")
    else:
        print(f"Product already exists: {product.name}")

print("Seeding completed successfully!")
