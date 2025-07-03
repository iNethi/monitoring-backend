import os
import logging
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Create a superuser from environment variables if not already present.'

    def handle(self, *args, **options):
        User = get_user_model()
        username = os.environ.get('SUPERUSER_USERNAME')
        email = os.environ.get('SUPERUSER_EMAIL')
        password = os.environ.get('SUPERUSER_PASSWORD')

        if not username or not email or not password:
            logger.error('SUPERUSER_USERNAME, SUPERUSER_EMAIL, and SUPERUSER_PASSWORD must be set in the environment.')
            # linter-ignore: self.style.ERROR is a valid instance attribute
            self.stdout.write(self.style.ERROR('Superuser env variables not set.'))
            return

        if User.objects.filter(username=username).exists():
            logger.info(f'Superuser "{username}" already exists.')
            # linter-ignore: self.style.SUCCESS is a valid instance attribute
            self.stdout.write(self.style.SUCCESS(f'Superuser "{username}" already exists.'))
            return

        User.objects.create_superuser(username=username, email=email, password=password)
        logger.info(f'Superuser "{username}" created.')
        # linter-ignore: self.style.SUCCESS is a valid instance attribute
        self.stdout.write(self.style.SUCCESS(f'Superuser "{username}" created.')) 