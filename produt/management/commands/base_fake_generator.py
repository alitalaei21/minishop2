from django.core.management.base import BaseCommand
from faker import Faker
import random
import os
from django.conf import settings
from django.core.files import File
from django.core.files.storage import default_storage

fake = Faker('fa_IR')  # Persian locale for fake data

class BaseFakeGeneratorCommand(BaseCommand):
    def get_random_image(self, image_dir):
        """Get a random image from the specified directory"""
        image_paths = []
        for root, dirs, files in os.walk(image_dir):
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    image_paths.append(os.path.join(root, file))
        return random.choice(image_paths) if image_paths else None

    def walk_image_directory(self, image_dir):
        image_paths = []
        for root, dirs, files in os.walk(image_dir):
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    image_paths.append(os.path.join(root, file))
        return image_paths

    def get_image_dirs(self):
        return {
            'category': os.path.join(settings.BASE_DIR, 'assets', 'category_test_images'),
            'product': os.path.join(settings.BASE_DIR, 'assets', 'product_test_images'),
            'banner': os.path.join(settings.BASE_DIR, 'assets', 'banner_test_images')
        } 