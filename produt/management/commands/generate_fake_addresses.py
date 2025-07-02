from django.contrib.auth import get_user_model
from .base_fake_generator import BaseFakeGeneratorCommand, fake
from produt.models import Address
import random

User = get_user_model()

class Command(BaseFakeGeneratorCommand):
    help = 'Generates fake Persian addresses for testing'

    def add_arguments(self, parser):
        parser.add_argument('--max-addresses', type=int, default=3,
                          help='Maximum number of addresses per user')

    def handle(self, *args, **options):
        # Get all users (we need at least one)
        users = list(User.objects.all())
        if not users:
            self.stdout.write(self.style.ERROR('No users found. Please run generate_fake_users first.'))
            return

        self.stdout.write('Creating addresses...')
        for user in users:
            for _ in range(random.randint(1, options['max_addresses'])):
                Address.objects.create(
                    user=user,
                    province=fake.state(),
                    city=fake.city(),
                    street=fake.street_address(),
                    postal_code=fake.postcode(),
                    phone_number=fake.phone_number(),
                    is_default=random.choice([True, False])
                )

        total_addresses = Address.objects.count()
        self.stdout.write(self.style.SUCCESS(f'Successfully created {total_addresses} addresses!')) 