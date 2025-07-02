from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.contrib.auth import get_user_model
from faker import Faker
from produt.models import (
    Category, Product, ProductVariant,
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


def walk_image_directory(image_dir):
    image_paths = []
    for root, dirs, files in os.walk(image_dir):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                image_paths.append(os.path.join(root, file))
    return image_paths


class Command(BaseCommand):
    help = 'Generates all fake Persian data for testing'

    def add_arguments(self, parser):
        parser.add_argument('--users', type=int, default=5, help='Number of users to create')
        parser.add_argument('--categories', type=int, default=5, help='Number of categories to create')
        parser.add_argument('--products', type=int, default=20, help='Number of products to create')
        parser.add_argument('--orders', type=int, default=15, help='Number of orders to create')
        parser.add_argument('--banners', type=int, default=5, help='Number of banners to create')
        parser.add_argument('--max-addresses', type=int, default=3, help='Maximum number of addresses per user')
        parser.add_argument('--comment-ratio', type=float, default=0.5, help='Ratio of products to receive comments')

    def handle(self, *args, **options):
        try:
            self.stdout.write('Starting fake data generation...\n')

            # Generate data in the correct order to maintain dependencies
            self.stdout.write('1. Generating users...')
            call_command('generate_fake_users', users=options['users'])

            self.stdout.write('\n2. Generating categories...')
            call_command('generate_fake_categories', categories=options['categories'])

            self.stdout.write('\n3. Generating products...')
            call_command('generate_fake_products', products=options['products'])

            self.stdout.write('\n4. Generating orders and carts...')
            call_command('generate_fake_orders', orders=options['orders'])

            self.stdout.write('\n5. Generating comments and likes...')
            call_command('generate_fake_interactions', comment_ratio=options['comment_ratio'])

            self.stdout.write('\n6. Generating addresses...')
            call_command('generate_fake_addresses', max_addresses=options['max_addresses'])

            self.stdout.write('\n7. Generating banners...')
            call_command('generate_fake_banners', banners=options['banners'])

            self.stdout.write(self.style.SUCCESS('\nSuccessfully generated all fake data!'))

        except Exception as e:
            raise CommandError(f'Error generating fake data: {str(e)}')