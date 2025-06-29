from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from faker import Faker
from produt.models import (
    Category, SizeColor, Product, ProductVariant,
    Order, OrderItem, Baner, Cart, CartItem,
    Comment, Like, Address, variant_image_path
)
import random
from django.core.files import File
from pathlib import Path
import os
from django.conf import settings
from django.core.files.storage import default_storage

User = get_user_model()
fake = Faker('fa_IR')  # Persian locale for fake data

def get_random_image(image_dir):
    """Get a random image from the specified directory"""
    image_paths = []
    for root, dirs, files in os.walk(image_dir):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                image_paths.append(os.path.join(root, file))
    return random.choice(image_paths) if image_paths else None

class Command(BaseCommand):
    help = 'Generates fake Persian data for testing'

    def add_arguments(self, parser):
        parser.add_argument('--users', type=int, default=5, help='Number of users to create')
        parser.add_argument('--categories', type=int, default=5, help='Number of categories to create')
        parser.add_argument('--products', type=int, default=20, help='Number of products to create')
        parser.add_argument('--orders', type=int, default=10, help='Number of orders to create')

    def handle(self, *args, **options):
        category_images_dir = os.path.join(settings.BASE_DIR, 'assets', 'category_test_images')
        product_images_dir = os.path.join(settings.BASE_DIR, 'assets', 'product_test_images')

        self.stdout.write('Creating users...')
        users = []
        for _ in range(options['users']):
            user = User.objects.create_user(
                username=fake.user_name(),
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                email=fake.email(),
                password='testpass123'
            )
            users.append(user)

        self.stdout.write('Creating categories...')
        jewelry_categories = [
            'گردنبند', 'انگشتر', 'دستبند', 'گوشواره',
            'آویز', 'پابند', 'حلقه‌های ازدواج', 'حلقه‌های نامزدی'
        ]
        categories = []
        for category_name in jewelry_categories[:options['categories']]:
            category = Category(
                user=random.choice(users),
                name=category_name,
            )
            image_path = get_random_image(category_images_dir)
            if image_path:
                with open(image_path, 'rb') as img_file:
                    category.image.save(
                        os.path.basename(image_path),
                        File(img_file),
                        save=True
                    )
            categories.append(category)

        self.stdout.write('Creating size/color combinations...')
        size_colors = []
        sizes = [5, 6, 7, 8, 9, 10]
        colors = ['gold', 'rosegold', 'white']

        for size in sizes:
            for color in colors:
                size_color = SizeColor.objects.create(
                    size=size,
                    color=color
                )
                size_colors.append(size_color)

        self.stdout.write('Creating products...')
        products = []
        jewelry_adjectives = ['زیبا', 'لوکس', 'کلاسیک', 'مدرن', 'دست‌ساز', 'طراحی شده', 'منحصر به فرد']
        jewelry_materials = ['طلا', 'نقره', 'پلاتین', 'الماس', 'مروارید', 'کریستال']
        tag_options = ['۱۸عیار', '۱۴عیار', 'طلای خالص', 'الماس', 'مروارید',
            'سنگ‌های قیمتی', 'دست‌ساز', 'کلاسیک', 'مدرن', 'ویژه', 'لوکس', 
            'روزمره', 'عروسی', 'مهمانی', 'هدیه', 'خاص', 'مد روز']

        for _ in range(options['products']):
            adj = random.choice(jewelry_adjectives)
            material = random.choice(jewelry_materials)
            category = random.choice(categories)

            product = Product(
                name=f"{adj} {material} {category.name.rstrip('ها')}",
                description=fake.paragraph(nb_sentences=3) + f"\nساخته شده از بهترین {material} با ظرافت بالا.",
                title=f"{adj} {material} {category.name.rstrip('ها')}",
                labor_wage=random.randint(7, 14),
                category=category,
                special_sale=random.choice([True, False]),
                tags=random.sample(tag_options, k=random.randint(2, 4))
            )
            product.save()
            products.append(product)

            selected_size_colors = random.sample(size_colors, k=random.randint(1, 3))
            for size_color in selected_size_colors:
                variant = ProductVariant(
                    product=product,
                    size_color=size_color,
                    weight=round(random.uniform(0.1, 5), 3),
                    stock=random.randint(1, 10),
                    discount=random.randint(0, 30) if product.special_sale else 0
                )
                variant.save()
                
                # Add multiple variant images
                num_images = random.randint(1, 3)  # Random number of images between 1 and 3
                variant_images = []
                for _ in range(num_images):
                    image_path = get_random_image(product_images_dir)
                    if image_path:
                        with open(image_path, 'rb') as img_file:
                            file_obj = File(img_file)
                            image_name = variant_image_path(variant, os.path.basename(image_path))
                            # Save the file to storage and get the path
                            saved_path = default_storage.save(image_name, file_obj)
                            variant_images.append(saved_path)
                variant.images = variant_images
                variant.save()
                

        self.stdout.write('Creating orders...')
        for _ in range(options['orders']):
            order = Order.objects.create(
                customer=random.choice(users),
                status=random.choice(['p', 'c'])
            )
            for _ in range(random.randint(1, 3)):
                product = random.choice(products)
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=random.randint(1, 2),
                    price_per_item=round(random.uniform(100, 5000), 3)
                )
            order.calculate_total_price()

        self.stdout.write('Creating carts...')
        for user in users:
            cart = Cart.objects.create(user=user)
            for _ in range(random.randint(1, 2)):
                CartItem.objects.create(
                    cart=cart,
                    product=random.choice(products),
                    quantity=1
                )

        self.stdout.write('Creating comments...')
        jewelry_comments = [
            "کار بسیار با کیفیت و ظریف است!",
            "زیبایی محصول دقیقا همان چیزی است که انتظار داشتم.",
            "رنگ طلا بسیار جذاب است.",
            "سایز مناسب و کیفیت عالی.",
            "طراحی شیک و رضایت‌بخش.",
            "جزئیات فوق‌العاده است."
        ]
        for product in products[:10]:
            for _ in range(random.randint(1, 5)):
                Comment.objects.create(
                    user=random.choice(users),
                    product=product,
                    comment=random.choice(jewelry_comments) + " " + fake.sentence()
                )

        self.stdout.write('Creating likes...')
        for product in products:
            for user in random.sample(users, k=random.randint(0, len(users))):
                Like.objects.create(
                    product=product,
                    user=user
                )

        self.stdout.write('Creating addresses...')
        for user in users:
            for _ in range(random.randint(1, 3)):
                Address.objects.create(
                    user=user,
                    province=fake.state(),
                    city=fake.city(),
                    street=fake.street_address(),
                    postal_code=fake.postcode(),
                    phone_number=fake.phone_number(),
                    is_default=random.choice([True, False])
                )

        self.stdout.write('Creating banners...')
        banner_names = ['مجموعه طلای ویژه', 'ورودهای جدید', 'فصل عروسی']
        for name in banner_names:
            banner = Baner(
                name=name,
                silde=random.choice([True, False])
            )
            image_path = get_random_image(product_images_dir)
            if image_path:
                with open(image_path, 'rb') as img_file:
                    banner.image.save(
                        os.path.basename(image_path),
                        File(img_file),
                        save=True
                    )

        self.stdout.write(self.style.SUCCESS('Successfully generated fake Persian data!'))
