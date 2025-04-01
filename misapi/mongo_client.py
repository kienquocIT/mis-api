# First import it client will be created
# Next import client use python cache, not execute code in file.
# This rule keep client is init once per all time.
# --- check it:
#   Comment import client from this file in settings
#   Uncomment in print in this file | add print if not exist
#   Open django shell command
#   Import client from this file:
#       from misapi.mongo_client import client as c1
#       from misapi.mongo_client import client as c2
#       from misapi.mongo_client import client as c3
#   Print will be printed only one time.
#   Check state:
#       c1.admin.command("ping")
#       c2.admin.command("ping")
#       c3.admin.command("ping")
#       c1.close()
#       c1.admin.command("ping")
#       c2.admin.command("ping")
#       c3.admin.command("ping")

__all__ = [
    'MongoViewParse',
    'client', 'db_connector',
    'MyMongoClient',
    'mongo_log_auth',
    'mongo_log_opp_task',
    'mongo_log_call_fb_api',
]

import sys

from pymongo import MongoClient, errors
import mongomock

from django.conf import settings

from .mongo_class import MongoAuthLog, MongoOppTaskLog, MongoCallFBAPI, MONGO_MOCK_ENABLE, Colors


class MongoViewParse:
    def __init__(self, request):
        self.request = request
        self.params = self.request.query_params.dict()

    def get_page_index(self):
        key_page = 'page'
        try:
            return int(self.params.get(key_page, 1))
        except ValueError:
            return 0

    def get_search(self):
        key_search = 'search'
        return self.params.get(key_search, 1)

    def get_ordering(self, default_data: dict[str, any]):
        key_ordering = 'ordering'
        value = self.params.get(key_ordering, None)
        if value:
            if value.startswith('-'):
                return {
                    value[1:]: -1
                }
            return {
                value: 1
            }
        return default_data if isinstance(default_data, dict) else {}

    def get_page_size(self):
        key_page = "pageSize"
        page_size_default = 1
        page_size_default = page_size_default if page_size_default > 0 else settings.CUSTOM_PAGE_MAXIMUM_SIZE
        try:
            return int(self.params.get(key_page, page_size_default))
        except ValueError:
            return 0

    @classmethod
    def parse_return(cls, results, page_index=None, count=None, page_size=None):
        return {
            "next": page_index + 1 if isinstance(page_index, int) else 0,
            "previous": page_index - 1 if isinstance(page_index, int) else 0,
            "count": count if isinstance(page_index, int) else 0,
            "page_size": page_size if isinstance(page_size, int) else 0,
            "result": results,
        }


if not (settings.MONGO_HOST and settings.MONGO_PORT and settings.MONGO_DB_NAME):
    raise errors.ConfigurationError('Host, port, database name must be required for connect to MongoDB')

if MONGO_MOCK_ENABLE is True:
    sys.stdout.writelines(Colors.RED + 'Mongo Mock is enabled!' + '\n' + Colors.END_C)
    client = mongomock.MongoClient()
else:
    client = MongoClient(
        **{
            'host': settings.MONGO_HOST,
            'port': settings.MONGO_PORT,

        },
        **(
            {
                'username': settings.MONGO_USERNAME,
                'password': settings.MONGO_PASSWORD,
            } if settings.MONGO_USERNAME and settings.MONGO_PASSWORD else {}
        )
    )

db_connector = client[settings.MONGO_DB_NAME]

mongo_log_auth = MongoAuthLog(connector=db_connector)

mongo_log_opp_task = MongoOppTaskLog(connector=db_connector)

mongo_log_call_fb_api = MongoCallFBAPI(connector=db_connector)

mongo_objs = [
    mongo_log_auth,
    mongo_log_opp_task,
    mongo_log_call_fb_api,
]


class MyMongoClient:
    @staticmethod
    def check_connection():
        client.admin.command('ping')

    @staticmethod
    def migrate():
        sys.stdout.writelines(Colors.RED + 'Integrate to MongoDB is running...' + Colors.END_C + '\n')
        for obj in mongo_objs:
            obj.create_collection()
            sys.stdout.write("\n")

    @staticmethod
    def check_collection():
        collection_not_found = []
        for obj in mongo_objs:
            collection_name = obj.collection_name()
            if collection_name not in db_connector.list_collection_names():
                collection_not_found.append(collection_name)
        if collection_not_found:
            sys.stdout.writelines(
                Colors.RED + '[mongodb] Collection is not found: '
                + str(collection_not_found) +
                '. Please execute commands: mongo_migrate' + Colors.END_C
                + '\n'
            )


MyMongoClient.check_collection()
