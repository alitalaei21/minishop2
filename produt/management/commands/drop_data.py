from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from produt.models import Category, Product, ProductVariant, SizeColor, Order, OrderItem, Baner, Cart, CartItem, Like, Comment, Address

User = get_user_model()

class Command(BaseCommand):
    help = 'Drop all data from the database'

    def handle(self, *args, **options):
        self.stdout.write('Deleting likes...')
        Like.objects.all().delete()

        self.stdout.write('Deleting comments...')
        Comment.objects.all().delete()

        self.stdout.write('Deleting cart items...')
        CartItem.objects.all().delete()

        self.stdout.write('Deleting carts...')
        Cart.objects.all().delete()

        self.stdout.write('Deleting order items...')
        OrderItem.objects.all().delete()

        self.stdout.write('Deleting orders...')
        Order.objects.all().delete()

        self.stdout.write('Deleting addresses...')
        Address.objects.all().delete()

        self.stdout.write('Deleting product variants...')
        ProductVariant.objects.all().delete()

        self.stdout.write('Deleting size colors...')
        SizeColor.objects.all().delete()

        self.stdout.write('Deleting products...')
        Product.objects.all().delete()

        self.stdout.write('Deleting categories...')
        Category.objects.all().delete()

        self.stdout.write('Deleting baners...')
        Baner.objects.all().delete()

        self.stdout.write('Deleting users...')
        User.objects.filter(is_superuser=False).delete()

        self.stdout.write(self.style.SUCCESS('Successfully dropped all data')) 