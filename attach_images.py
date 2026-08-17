import os
import shutil
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from store.models import Product

media_dir = os.path.join(os.getcwd(), 'media', 'products')
os.makedirs(media_dir, exist_ok=True)

brain_dir = r"C:\Users\athar\.gemini\antigravity-ide\brain\59f8988d-b77a-481d-be5e-7901e7cd3cc1"

mapping = {
    'Wireless Noise-Canceling Headphones': 'headphones_1786905845110.jpg',
    'Smart Fitness Watch Series 5': 'smartwatch_1786905941767.jpg',
    'Ergonomic Mechanical Keyboard RGB': 'keyboard_1786905992439.jpg',
}

for product_name, src_filename in mapping.items():
    src_path = os.path.join(brain_dir, src_filename)
    if os.path.exists(src_path):
        dest_filename = src_filename.split('_')[0] + '.jpg'
        dest_path = os.path.join(media_dir, dest_filename)
        shutil.copy(src_path, dest_path)
        
        # Update database model row by exact name
        p = Product.objects.filter(name=product_name).first()
        if p:
            p.image = f'products/{dest_filename}'
            p.save()
            print(f"Successfully attached {dest_filename} to {p.name}")
        else:
            print(f"Product not found for {product_name}")
    else:
        print(f"Source file missing: {src_path}")

