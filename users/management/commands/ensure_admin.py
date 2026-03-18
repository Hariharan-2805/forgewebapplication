
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os

class Command(BaseCommand):
    help = 'Ensures a superuser exists'

    def handle(self, *args, **options):
        User = get_user_model()
        username = os.environ.get("DJANGO_SUPERUSER_USERNAME") or "admin"
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL") or "admin@example.com"
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD") or "Admin123!"

        try:
            user, created = User.objects.get_or_create(username=username, defaults={"email": email})
            user.email = email
            user.is_staff = True
            user.is_superuser = True
            user.is_active = True
            user.set_password(password)
            user.save()

            if created:
                self.stdout.write(self.style.SUCCESS(f'Created superuser "{username}" with derived credentials'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Updated superuser "{username}" credentials'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating superuser: {e}'))
