import os
import sys

from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
from django.db import connections


class Command(BaseCommand):
    help = 'Migrate to mockup db ci sqlite3'

    SQL_GET_TABLES = """SELECT tbl_name FROM sqlite_master WHERE `type`='table' and tbl_name not like '%sqlite%';"""
    SQL_DROP_TABLE = """DROP TABLE IF EXISTS {tbl_name}"""
    SQL_DISABLE_FOREIGN_KEY = """PRAGMA foreign_keys = 0"""
    SQL_ENABLE_FOREIGN_KEY = """PRAGMA foreign_keys = 1"""

    def destroy_tables(self):
        try:
            cursor = connections['mockup_db_ci'].cursor()
            cursor.execute(self.SQL_GET_TABLES)
            tables = cursor.fetchall()
            sys.stdout.write(f'Tables: {len(tables)}\n')
            cursor.execute(self.SQL_DISABLE_FOREIGN_KEY)
            for row in tables:
                tbl_name = row[0]
                sys.stdout.write(f'\t {tbl_name}\n')
                cursor.execute(self.SQL_DROP_TABLE.format(tbl_name=tbl_name))
            cursor.execute(self.SQL_ENABLE_FOREIGN_KEY)
            sys.stdout.write('Destroy table is done\n')
            return True
        except Exception as err:
            sys.stdout.write(str(err) + '\n')
        return False

    def handle(self, *args, **kwargs):
        # flag allow to migrate in DB Routers
        os.environ['ENABLE_MIGRATE_MOCKUP_DB_CI'] = '1'

        # main
        mockup_db_ci = settings.DATABASES.get('mockup_db_ci', None)
        if mockup_db_ci and 'ENGINE' in mockup_db_ci and 'NAME' in mockup_db_ci:
            engine = mockup_db_ci['ENGINE']
            db_path = mockup_db_ci['NAME']
            if engine == 'django.db.backends.sqlite3':
                state = self.destroy_tables()
                if state is True:
                    call_command('migrate', '--database=mockup_db_ci')
            else:
                sys.stdout.write(f'Database mockup_db_ci config is incorrect. Not support: {engine}, {db_path}')
        else:
            sys.stdout.write('Database mockup_db_ci config is incorrect')

        # reset flag to disable
        os.environ['ENABLE_MIGRATE_MOCKUP_DB_CI'] = '0'
