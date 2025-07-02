from django.contrib.auth import get_user_model
from .base_fake_generator import BaseFakeGeneratorCommand, fake

User = get_user_model()

class Command(BaseFakeGeneratorCommand):
    help = 'Generates fake Persian users for testing'

    def add_arguments(self, parser):
        parser.add_argument('--users', type=int, default=5, help='Number of users to create')

    def handle(self, *args, **options):
        self.stdout.write('Creating users...')
        users = []
        for _ in range(options['users']):
            user = User.objects.create_user(
                username=fake.user_name(),
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                email=fake.email(),
                password='testpass123'
            )
            users.append(user)
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {len(users)} users!')) 