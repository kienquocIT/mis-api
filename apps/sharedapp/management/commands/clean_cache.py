from django.core.management.base import BaseCommand
from apps.shared import CacheController


class Command(BaseCommand):
    help = 'Clean cache server'

    def handle(self, *args, **options):
        CacheController().clean()
        self.stdout.write(self.style.SUCCESS('Successfully clean cache server.'))
