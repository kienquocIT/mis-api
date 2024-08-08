import sys

from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings


class Command(BaseCommand):
    help = 'Migrate to mockup db ci sqlite3'

    def handle(self, *args, **kwargs):
        mockup_db_ci = settings.DATABASES.get('mockup_db_ci', None)
        if mockup_db_ci and 'ENGINE' in mockup_db_ci and 'NAME' in mockup_db_ci:
            engine = mockup_db_ci['ENGINE']
            name = mockup_db_ci['NAME']
            if engine == 'django.db.backends.sqlite3' and name.endswith('.gitlab-ci-db.sqlite3'):
                call_command('migrate', '--database=mockup_db_ci')
            else:
                sys.stdout.write(f'Database mockup_db_ci config is incorrect. Not support: {engine}, {name}')
        else:
            sys.stdout.write('Database mockup_db_ci config is incorrect')
