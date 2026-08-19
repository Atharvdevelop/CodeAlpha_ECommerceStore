import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from store.models import Category, Product, ProductVariant

print("Seeding database with parent categories and variants...")

# 1. Create Superuser
if not User.objects.filter(username='admin').exists():
    admin_user = User.objects.create_superuser('admin', 'admin@sweepkart.com', 'admin123')
    print("Created superuser: admin / admin123")

# 2. Create Demo User
if not User.objects.filter(username='demo').exists():
    demo_user = User.objects.create_user('demo', 'demo@sweepkart.com', 'demo123', first_name='Demo', last_name='User')
    print("Created demo user: demo / demo123")

# 3. Create Parent & Subcategories
# Parent Categories
cat_men, _ = Category.objects.get_or_create(name='Men', parent=None)
cat_women, _ = Category.objects.get_or_create(name='Women', parent=None)
cat_kids, _ = Category.objects.get_or_create(name='Kids', parent=None)
cat_elec, _ = Category.objects.get_or_create(name='Electronics', parent=None)

# Subcategories
sub_men_jackets, _ = Category.objects.get_or_create(name="Men's Jackets", parent=cat_men)
sub_men_shirts, _ = Category.objects.get_or_create(name="Men's Shirts", parent=cat_men)

sub_women_hoodies, _ = Category.objects.get_or_create(name="Women's Hoodies", parent=cat_women)
sub_women_dresses, _ = Category.objects.get_or_create(name="Women's Dresses", parent=cat_women)

sub_kids_wear, _ = Category.objects.get_or_create(name="Kids Wear", parent=cat_kids)

sub_audio, _ = Category.objects.get_or_create(name="Audio & Headphones", parent=cat_elec)
sub_watches, _ = Category.objects.get_or_create(name="Smartwatches", parent=cat_elec)

# 4. Products & Variants Data
seed_data = [
    {
        'name': 'Men Leather Biker Jacket',
        'category': sub_men_jackets,
        'price': 3499.00,
        'stock': 30,
        'image': 'products/leather_jacket.jpg',
        'description': 'Premium genuine leather jacket with heavy duty zippers, quilted shoulder padding, and soft satin interior lining.',
        'variants': [
            {'color_name': 'Midnight Black', 'color_code': '#0a0a0a', 'size': 'M', 'stock': 10, 'price': 3499.00},
            {'color_name': 'Midnight Black', 'color_code': '#0a0a0a', 'size': 'L', 'stock': 10, 'price': 3499.00},
            {'color_name': 'Dark Chestnut Brown', 'color_code': '#4a2c11', 'size': 'L', 'stock': 10, 'price': 3699.00},
        ]
    },
    {
        'name': 'Men Slim Fit Denim Shirt',
        'category': sub_men_shirts,
        'price': 1299.00,
        'stock': 40,
        'image': 'products/denim_shirt.jpg',
        'description': 'Breathable cotton denim shirt with button-down collar and double chest flap pockets.',
        'variants': [
            {'color_name': 'Ocean Blue', 'color_code': '#2563eb', 'size': 'S', 'stock': 10, 'price': 1299.00},
            {'color_name': 'Ocean Blue', 'color_code': '#2563eb', 'size': 'M', 'stock': 15, 'price': 1299.00},
            {'color_name': 'Washed Black', 'color_code': '#1e293b', 'size': 'L', 'stock': 15, 'price': 1299.00},
        ]
    },
    {
        'name': "Women Oversized Fleece Hoodie",
        'category': sub_women_hoodies,
        'price': 1899.00,
        'stock': 35,
        'image': 'products/fleece_hoodie.jpg',
        'description': 'Ultra-cozy plush fleece pullover hoodie featuring kangaroo pocket and ribbed storm cuffs.',
        'variants': [
            {'color_name': 'Blush Pink', 'color_code': '#f472b6', 'size': 'S', 'stock': 10, 'price': 1899.00},
            {'color_name': 'Lavender Violet', 'color_code': '#a855f7', 'size': 'M', 'stock': 15, 'price': 1899.00},
            {'color_name': 'Mint Green', 'color_code': '#10b981', 'size': 'L', 'stock': 10, 'price': 1899.00},
        ]
    },
    {
        'name': "Women Elegant Evening Maxi Dress",
        'category': sub_women_dresses,
        'price': 2799.00,
        'stock': 20,
        'image': 'products/maxi_dress.jpg',
        'description': 'Sophisticated floor-length dress made with flowing chiffon fabric and metallic accent waist belt.',
        'variants': [
            {'color_name': 'Emerald Green', 'color_code': '#059669', 'size': 'M', 'stock': 10, 'price': 2799.00},
            {'color_name': 'Ruby Red', 'color_code': '#dc2626', 'size': 'L', 'stock': 10, 'price': 2799.00},
        ]
    },
    {
        'name': "Kids Printed Cotton T-Shirt Set",
        'category': sub_kids_wear,
        'price': 899.00,
        'stock': 50,
        'image': 'products/kids_tshirt.jpg',
        'description': 'Set of 2 hypoallergenic 100% organic cotton graphic printed crew-neck t-shirts for toddlers and kids.',
        'variants': [
            {'color_name': 'Sunshine Yellow', 'color_code': '#eab308', 'size': 'S', 'stock': 25, 'price': 899.00},
            {'color_name': 'Sky Cyan', 'color_code': '#06b6d4', 'size': 'M', 'stock': 25, 'price': 899.00},
        ]
    },
    {
        'name': 'Wireless Active Noise-Canceling Headphones',
        'category': sub_audio,
        'price': 4999.00,
        'stock': 25,
        'image': 'products/headphones.jpg',
        'description': 'High-fidelity audio with hybrid active noise cancellation, 40-hour battery life, and spatial audio support.',
        'variants': [
            {'color_name': 'Space Silver', 'color_code': '#94a3b8', 'size': None, 'stock': 15, 'price': 4999.00},
            {'color_name': 'Matte Stealth Black', 'color_code': '#0f172a', 'size': None, 'stock': 10, 'price': 4999.00},
        ]
    },
    {
        'name': 'Smart Fitness Watch Series X',
        'category': sub_watches,
        'price': 3299.00,
        'stock': 30,
        'image': 'products/smartwatch.jpg',
        'description': 'AMOLED touch display with continuous SpO2 monitor, GPS, 100+ workout modes, and 5ATM waterproof rating.',
        'variants': [
            {'color_name': 'Obsidian Black', 'color_code': '#000000', 'size': None, 'stock': 15, 'price': 3299.00},
            {'color_name': 'Neon Cyan', 'color_code': '#22d3ee', 'size': None, 'stock': 15, 'price': 3299.00},
        ]
    }
]

for p_data in seed_data:
    product, created = Product.objects.get_or_create(
        name=p_data['name'],
        defaults={
            'category': p_data['category'],
            'price': p_data['price'],
            'stock': p_data['stock'],
            'image': p_data.get('image', ''),
            'description': p_data['description'],
            'is_active': True,
        }
    )
    if created:
        print(f"Created product: {product.name}")
    else:
        # Update category & price if existed
        product.category = p_data['category']
        product.price = p_data['price']
        product.description = p_data['description']
        product.save()

    # Create Product Variants
    for v_data in p_data.get('variants', []):
        variant, v_created = ProductVariant.objects.get_or_create(
            product=product,
            color_name=v_data.get('color_name', ''),
            size=v_data.get('size'),
            defaults={
                'color_code': v_data.get('color_code', ''),
                'stock': v_data.get('stock', 10),
                'price': v_data.get('price'),
            }
        )
        if v_created:
            print(f"  -> Added variant: {variant}")

print("Seeding completed successfully!")
