from django.core.management.base import BaseCommand
from apps.shared.extends.caching import CacheManagement


class Command(BaseCommand):
    help = 'Clean cache server'

    def handle(self, *args, **options):
        CacheManagement().clean()
        self.stdout.write(self.style.SUCCESS('Successfully clean cache server.'))
