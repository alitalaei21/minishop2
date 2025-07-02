from .base_fake_generator import BaseFakeGeneratorCommand
from produt.models import Baner
from django.core.files import File
import random
import os

class Command(BaseFakeGeneratorCommand):
    help = 'Generates fake Persian banners for testing'

    def add_arguments(self, parser):
        parser.add_argument('--banners', type=int, default=5, help='Number of banners to create')

    def handle(self, *args, **options):
        self.stdout.write('Creating banners...')
        banner_names = ['مجموعه طلای ویژه', 'ورودهای جدید', 'فصل عروسی']
        image_dir = self.get_image_dirs()['banner']

        image_paths = self.walk_image_directory(image_dir)
        if not image_paths:
            self.stdout.write(self.style.ERROR('No banner images found in the assets directory.'))
            return

        banners_created = 0
        for image_path in image_paths:
            if banners_created >= options['banners']:
                break
                
            with open(image_path, 'rb') as img_file:
                banner = Baner(
                    name=random.choice(banner_names)
                )
                banner.image.save(
                    os.path.basename(image_path),
                    File(img_file),
                    save=True
                )
                banners_created += 1

        self.stdout.write(self.style.SUCCESS(f'Successfully created {banners_created} banners!')) 