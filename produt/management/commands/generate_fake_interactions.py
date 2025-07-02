from django.contrib.auth import get_user_model
from .base_fake_generator import BaseFakeGeneratorCommand, fake
from produt.models import Product, Comment, Like
import random

User = get_user_model()

class Command(BaseFakeGeneratorCommand):
    help = 'Generates fake Persian comments and likes for testing'

    def add_arguments(self, parser):
        parser.add_argument('--comment-ratio', type=float, default=0.5,
                          help='Ratio of products to receive comments (0.0 to 1.0)')

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

        comment_ratio = min(max(options['comment_ratio'], 0.0), 1.0)
        products_to_comment = products[:int(len(products) * comment_ratio)]

        self.stdout.write('Creating comments...')
        jewelry_comments = [
            "کار بسیار با کیفیت و ظریف است!",
            "زیبایی محصول دقیقا همان چیزی است که انتظار داشتم.",
            "رنگ طلا بسیار جذاب است.",
            "سایز مناسب و کیفیت عالی.",
            "طراحی شیک و رضایت‌بخش.",
            "جزئیات فوق‌العاده است."
        ]
        
        for product in products_to_comment:
            for _ in range(random.randint(1, 5)):
                Comment.objects.create(
                    user=random.choice(users),
                    product=product,
                    comment=random.choice(jewelry_comments) + " " + fake.sentence(),
                    rating=random.randint(1, 5)
                )

        self.stdout.write('Creating likes...')
        for product in products:
            for user in random.sample(users, k=random.randint(0, len(users))):
                Like.objects.create(
                    product=product,
                    user=user
                )

        self.stdout.write(self.style.SUCCESS('Successfully created comments and likes!')) 