from django.core.management.base import BaseCommand
from misapi.mongo_client import MyMongoClient


class Command(BaseCommand):
    help = 'Migrate collection of MongoDB'

    def handle(self, *args, **options):
        MyMongoClient.check_connection()
        MyMongoClient.migrate()
