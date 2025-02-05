import abc
import os
import sys

from django.utils import timezone


class Colors:
    RED = '\033[31m'
    END_C = '\033[m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'


MONGO_MOCK_ENABLE = os.environ.get('MONGO_MOCK_ENABLE', '0') in [1, '1']


class MongoMapInterface(abc.ABC):
    def __init__(self, connector, *args, **kwargs):
        self.connector = connector

    @abc.abstractmethod
    def collection_name(self, *args, **kwargs) -> str:
        pass

    @abc.abstractmethod
    def metadata(self, *args, **kwargs) -> dict[str, str or int]:
        pass

    @property
    def key__log_level(self):
        return 'log_level'

    @property
    def value__log_level(self):
        return ['INFO', 'ERROR', 'DEBUG', 'WARN']

    @property
    def key__timestamp(self):
        return 'timestamp'

    @property
    def key__metadata(self):
        return 'metadata'

    @property
    def key__errors(self):
        return 'errors'

    def timeseries(self):
        return {
            'timeField': self.key__timestamp,
            'metaField': self.key__metadata,
            'granularity': 'seconds',
        }

    def expire_after_seconds(self):
        return None

    def create_collection(self):
        collection_name = self.collection_name()
        sys.stdout.write(f'Create collection: ' + Colors.BLUE + collection_name + Colors.END_C + ' .......... ')

        if collection_name not in self.connector.list_collection_names():
            try:
                expire_after_seconds = self.expire_after_seconds()
                self.connector.create_collection(
                    collection_name,
                    timeseries=self.timeseries(),
                    **(
                        {
                            'expireAfterSeconds': expire_after_seconds
                        } if isinstance(expire_after_seconds, int) else {}
                    )
                )
            except Exception as err:
                sys.stdout.writelines(Colors.RED + 'error' + Colors.END_C)
                sys.stdout.writelines(str(err))
                return False
            else:
                sys.stdout.writelines(Colors.GREEN + 'ok' + Colors.END_C)
                return True
        else:
            sys.stdout.writelines(Colors.YELLOW + 'skip by exist' + Colors.END_C)

    @property
    def collection(self):
        return getattr(self.connector, self.collection_name(), None)

    def fill_item(self, data: dict):
        if self.key__metadata not in data:
            data[self.key__metadata] = self.metadata()
        if self.key__log_level not in data:
            data[self.key__log_level] = 'INFO'
        if self.key__timestamp not in data:
            data[self.key__timestamp] = timezone.now()
        if self.key__errors not in data:
            data[self.key__errors] = None
        return data

    def _insert_one(self, data: dict[str, any]):
        collection = self.collection
        if collection is not None:
            return self.collection.insert_one(self.fill_item(data))
        return None

    def _insert_many(self, data_list: list[dict[str, any]]):
        collection = self.collection
        if collection is not None:
            return self.collection.insert_many(
                [
                    self.fill_item(item) for item in data_list
                ]
            )
        return None

    @abc.abstractmethod
    def insert_one(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def insert_many(self, *args, **kwargs):
        pass

    def find(self, filter_data: dict[str, any], sort: dict = None, skip: int = None, limit: int = None):
        collection = self.collection
        if collection is not None:
            cursor = self.collection.find(filter_data)
            if sort:
                cursor = cursor.sort(sort)
            if skip:
                cursor = cursor.skip(skip)
            if limit:
                cursor = cursor.limit(limit)
            return cursor
        return None

    def aggregate(self, stages: list[dict[str, any]]):
        collection = self.collection
        if collection is not None:
            if MONGO_MOCK_ENABLE is True:
                return []
            return self.collection.aggregate(stages)
        return []

    def count_documents(self, filter_data: dict[str, any]):
        collection = self.collection
        if collection is not None:
            return self.collection.count_documents(filter_data)
        return 0


class MongoAuthLog(MongoMapInterface):
    def collection_name(self) -> str:
        return 'logs_auth'

    def expire_after_seconds(self):
        return 60 * 60 * 24 * 30  # will destroy after 30 days

    def metadata(self, user_id) -> dict[str, str or int]:
        return {
            "service_name": "AUTH",
            "user_id": str(user_id),
        }

    def insert_one(self, metadata: dict, endpoint: str, return_type: str = '', error_data: str = '', log_level='INFO'):
        return self._insert_one(
            data={
                'metadata': metadata,
                'endpoint': endpoint.upper(),
                'return_type': return_type,
                self.key__errors: error_data,
                self.key__log_level: log_level,
            }
        )

    def insert_many(self, data_list):
        pass


class MongoOppTaskLog(MongoMapInterface):
    def collection_name(self) -> str:
        return 'logs_opp_task'

    def metadata(self, employee_inherit_id, tenant_id, company_id) -> dict[str, str or int]:
        return {
            'employee_inherit_id': employee_inherit_id,
            'tenant_id': tenant_id,
            'company_id': company_id,
        }

    def insert_one(
            self,
            employee_inherit_id, tenant_id, company_id,
            date_changes, task_id,
            task_status, status_translate='',
            task_color='',
    ):
        return self._insert_one(
            data={
                self.key__timestamp: date_changes,
                "metadata": self.metadata(
                    employee_inherit_id=str(employee_inherit_id),
                    tenant_id=str(tenant_id),
                    company_id=str(company_id),
                ),
                "task_id": str(task_id),
                "task_status": str(task_status),
                "task_status_translate": status_translate,
                "task_color": task_color,
            }
        )

    def insert_many(self, data_list: list):
        return self._insert_many(
            [
                {
                    "metadata": self.metadata(
                        employee_inherit_id=str(item.pop('employee_inherit_id', '')),
                        tenant_id=str(item.pop('tenant_id', '')),
                        company_id=str(item.pop('company_id', '')),
                    ),
                    self.key__timestamp: item.pop('date_changes', ''),
                    **item,
                }
                for item in data_list
            ]
        )


class MongoCallFBAPI(MongoMapInterface):
    def collection_name(self) -> str:
        return 'logs_call_fb_api'

    def expire_after_seconds(self):
        # 200 req / hours
        return 60 * 60 * 24 * 30  # will destroy after 30 days

    def metadata(self, company_id) -> dict[str, str or int]:
        return {
            "service_name": "FB",
            "company_id": str(company_id),
        }

    def insert_one(self, metadata: dict, url: str, method: str, resp_status: int = ''):
        return self._insert_one(
            data={
                'metadata': metadata,
                'url': url,
                'method': method,
                'resp_status': resp_status,
            }
        )

    def insert_many(self, data_list):
        pass
