from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from produt.models import Category, Product, ProductVariant, Order, OrderItem, Baner, Cart, CartItem, Like, Comment, Address

User = get_user_model()

class Command(BaseCommand):
    help = 'Deletes all data from the database'

    def handle(self, *args, **options):
        self.stdout.write('Deleting all data...')
        
        # Delete in correct order to respect foreign key constraints
        Comment.objects.all().delete()
        Like.objects.all().delete()
        CartItem.objects.all().delete()
        Cart.objects.all().delete()
        OrderItem.objects.all().delete()
        Order.objects.all().delete()
        ProductVariant.objects.all().delete()
        Product.objects.all().delete()
        Category.objects.all().delete()
        Baner.objects.all().delete()
        Address.objects.all().delete()

        self.stdout.write('Deleting users...')
        User.objects.filter(is_superuser=False).delete()

        self.stdout.write(self.style.SUCCESS('Successfully deleted all data!')) 