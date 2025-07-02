from .base_fake_generator import BaseFakeGeneratorCommand, fake
from produt.models import Category, Product, ProductVariant
from django.core.files import File
from django.core.files.storage import default_storage
import random
import os
from produt.models import variant_image_path

class Command(BaseFakeGeneratorCommand):
    help = 'Generates fake Persian products and variants for testing'

    def add_arguments(self, parser):
        parser.add_argument('--products', type=int, default=20, help='Number of products to create')

    def handle(self, *args, **options):
        self.stdout.write('Creating products...')
        
        # Get all categories (we need at least one category)
        categories = list(Category.objects.all())
        if not categories:
            self.stdout.write(self.style.ERROR('No categories found. Please run generate_fake_categories first.'))
            return

        jewelry_adjectives = ['زیبا', 'لوکس', 'کلاسیک', 'مدرن', 'دست‌ساز', 'طراحی شده', 'منحصر به فرد']
        jewelry_materials = ['طلا', 'نقره', 'پلاتین', 'الماس', 'مروارید', 'کریستال']
        tag_options = ['۱۸عیار', '۱۴عیار', 'طلای خالص', 'الماس', 'مروارید',
                      'سنگ‌های قیمتی', 'دست‌ساز', 'کلاسیک', 'مدرن', 'ویژه', 'لوکس',
                      'روزمره', 'عروسی', 'مهمانی', 'هدیه', 'خاص', 'مد روز']
        sizes = [5, 6, 7, 8, 9, 10]
        colors = ['gold', 'rosegold', 'white']

        products = []
        image_dir = self.get_image_dirs()['product']

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
                tags=random.sample(tag_options, k=random.randint(2, 4))
            )
            product.save()
            products.append(product)

            # Create random variants with different size/color combinations
            num_variants = random.randint(1, 3)
            size_color_combinations = random.sample([(s, c) for s in sizes for c in colors], k=num_variants)
            
            for size, color in size_color_combinations:
                variant = ProductVariant(
                    product=product,
                    size=size,
                    color=color,
                    weight=round(random.uniform(0.1, 5), 3),
                    stock=random.randint(1, 10),
                    special_sale=random.choice([True, False]),
                    discount=random.randint(0, 30) if random.choice([True, False]) else 0
                )
                variant.save()

                # Add multiple variant images
                num_images = random.randint(1, 3)
                variant_images = []
                for _ in range(num_images):
                    image_path = self.get_random_image(image_dir)
                    if image_path:
                        with open(image_path, 'rb') as img_file:
                            file_obj = File(img_file)
                            image_name = variant_image_path(variant, os.path.basename(image_path))
                            saved_path = default_storage.save(image_name, file_obj)
                            variant_images.append(saved_path)
                variant.images = variant_images
                variant.save()

        self.stdout.write(self.style.SUCCESS(f'Successfully created {len(products)} products with variants!')) 