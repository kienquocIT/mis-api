from django.conf import settings
from django.core.management.base import BaseCommand
from apps.core.account.models import User


class Command(BaseCommand):
    help = 'Checking initials data for all apps.'

    def handle(self, *args, **options):
        if settings.DEBUG is True:
            for obj in User.objects.all():
                obj.set_password('Admin111111')
                obj.save(update_fields=['password'])
                self.stdout.write(f'Changed: {obj.username}')
