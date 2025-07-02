from django.contrib.auth import get_user_model
from .base_fake_generator import BaseFakeGeneratorCommand
from produt.models import Category
from django.core.files import File
import random
import os

User = get_user_model()

class Command(BaseFakeGeneratorCommand):
    help = 'Generates fake Persian categories for testing'

    def add_arguments(self, parser):
        parser.add_argument('--categories', type=int, default=5, help='Number of categories to create')

    def handle(self, *args, **options):
        self.stdout.write('Creating categories...')
        
        # Get all users (we need at least one user)
        users = list(User.objects.all())
        if not users:
            self.stdout.write(self.style.ERROR('No users found. Please run generate_fake_users first.'))
            return

        jewelry_categories = [
            'گردنبند', 'انگشتر', 'دستبند', 'گوشواره',
            'آویز', 'پابند', 'حلقه‌های ازدواج', 'حلقه‌های نامزدی'
        ]
        
        categories = []
        image_dir = self.get_image_dirs()['category']
        
        for category_name in jewelry_categories[:options['categories']]:
            category = Category(
                user=random.choice(users),
                name=category_name,
            )
            image_path = self.get_random_image(image_dir)
            if image_path:
                with open(image_path, 'rb') as img_file:
                    category.image.save(
                        os.path.basename(image_path),
                        File(img_file),
                        save=True
                    )
            categories.append(category)

        self.stdout.write(self.style.SUCCESS(f'Successfully created {len(categories)} categories!')) 