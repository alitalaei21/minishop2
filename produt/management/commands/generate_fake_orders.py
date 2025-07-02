from django.contrib.auth import get_user_model
from .base_fake_generator import BaseFakeGeneratorCommand
from produt.models import Product, Order, OrderItem, Cart, CartItem
import random

User = get_user_model()

class Command(BaseFakeGeneratorCommand):
    help = 'Generates fake Persian orders and carts for testing'

    def add_arguments(self, parser):
        parser.add_argument('--orders', type=int, default=15, help='Number of orders to create')

    def handle(self, *args, **options):
        # Get all users and products (we need at least one of each)
        users = list(User.objects.all())
        products = list(Product.objects.all())

        if not users:
            self.stdout.write(self.style.ERROR('No users found. Please run generate_fake_users first.'))
            return
        if not products:
            self.stdout.write(self.style.ERROR('No products found. Please run generate_fake_products first.'))
            return

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

        self.stdout.write(self.style.SUCCESS(f'Successfully created {options["orders"]} orders and {len(users)} carts!')) 