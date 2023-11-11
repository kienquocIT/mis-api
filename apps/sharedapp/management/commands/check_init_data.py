from django.core.management.base import BaseCommand
from apps.sharedapp.data.base import check_app_depends_and_mapping


class Command(BaseCommand):
    help = 'Checking initials data for all apps.'

    def handle(self, *args, **options):
        if not check_app_depends_and_mapping():
            raise ValueError('ERRORS')
