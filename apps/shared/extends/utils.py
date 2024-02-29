import json
import random
import re
import string
from datetime import datetime, date
from typing import Union, Type
from uuid import UUID

from django.core.serializers.json import DjangoJSONEncoder
from django.conf import settings

__all__ = ['LinkListHandler', 'StringHandler', 'ListHandler', 'CustomizeEncoder', 'TypeCheck', 'FORMATTING']


class LinkListHandler:
    def __init__(self, ll=None):  # pylint: disable=C0103
        self.ll = {} if not isinstance(ll, dict) else ll  # pylint: disable=C0103

    def convert(self, start_key):
        if self.ll:
            result = self.ll_iterator(start_key)
            return list(result)
        return []

    @staticmethod
    def fill_data(list_arranged, data):
        result = []
        if list_arranged and data:
            for key in list_arranged:
                result.append(data[key] if key in data else {})
        return result

    def ll_iterator(self, node) -> list:  # generator object
        while node is not None:
            yield node
            if node in self.ll:
                node = self.ll[node]
            else:
                node = None


class StringHandler:
    @staticmethod
    def random_str(length):
        return ''.join([random.choice(string.ascii_letters) for _ in range(length)])

    @staticmethod
    def random_number(length, to_type: Type = str):
        if to_type is str:
            return ''.join([random.choice(string.digits) for _ in range(length)])
        if to_type is int:
            first_item = random.choice('123456789')
            remainder_item = ''.join([random.choice(string.digits) for _ in range(length - 1)])
            return int(first_item + remainder_item)
        return StringHandler.random_str(length=length)

    @staticmethod
    def remove_special_characters_regex(text):
        """Fast with short string"""
        return re.sub(r'[^\w\s]', '', text)

    @staticmethod
    def remove_special_characters_translate(text):
        """Fast with string too long"""
        return text.translate(str.maketrans('', '', string.punctuation)).replace(' ', '')


class ListHandler:
    @staticmethod
    def diff_two_list(arr_a: list[str], arr_b: list[str]) -> (list[str], list[str], list[str]):
        """
        Returns:
            0: letters in "a" but not in "b"
            1: letters in both "a" and "b"
            2: letters in "b" but not in "a"
        """
        # best performance by set: https://docs.python.org/3/tutorial/datastructures.html#sets
        both_set = list(set(arr_a) & set(arr_b))
        left_split = list(set(arr_a) - set(both_set))
        right_split = list(set(arr_b) - set(both_set))
        return left_split, both_set, right_split

    @staticmethod
    def distant_dict_in_list(dict_in_list):
        try:
            return [dict(strJSON) for strJSON in set(frozenset(data.items()) for data in dict_in_list)]
        except Exception as err:
            if settings.DEBUG:
                print('[SKIP]  [distant_dict_...] :', 'ERR', '=', err, ',', 'data', '=', dict_in_list)

        dict_in_list__unique = []
        for item in dict_in_list:
            tmp = json.dumps(item, cls=CustomizeEncoder)
            if tmp not in dict_in_list__unique:
                dict_in_list__unique.append(item)
        return dict_in_list__unique


class CustomizeEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, (UUID, datetime)):
            return str(obj)
        return super().default(obj)


class TypeCheck:
    @staticmethod
    def check_uuid(data: any, return_data=False) -> Union[UUID, bool, None]:
        # check
        try:
            if isinstance(data, UUID):
                data_checked = data
            else:
                data_checked = UUID(data)
        except (Exception,):
            data_checked = None

        # return
        if return_data is True:
            return data_checked if data_checked else None
        if data_checked:
            return True
        return False

    @classmethod
    def check_uuid_list(cls, data: list[any], return_data=False) -> Union[list, bool]:
        result = []
        if data and isinstance(data, list):
            for idx_val in data:
                tmp = cls.check_uuid(idx_val, return_data=return_data)
                if return_data is True:
                    if tmp is not None:
                        result.append(tmp)
                else:
                    result.append(tmp)
                    if tmp is False:
                        break

        if return_data is True:
            return result
        if len(result) == len(data) and all(result) is True:
            return True
        return False

    @classmethod
    def list_child_type(cls, data: list, child_type: type) -> bool:
        if isinstance(data, list):
            return all(isinstance(x, child_type) for x in data)
        return False

    @classmethod
    def dict_child_type(cls, data: dict, key_type: type, value_type: type) -> bool:
        if isinstance(data, dict):
            return all(
                all(
                    [isinstance(key, key_type), isinstance(value, value_type)]
                ) for key, value in data.items()
            )
        return False


class FORMATTING:
    DATETIME = settings.REST_FRAMEWORK['DATETIME_FORMAT']
    DATE = settings.REST_FRAMEWORK['DATE_FORMAT']
    PAGE_SIZE = settings.REST_FRAMEWORK['PAGE_SIZE']

    @classmethod
    def parse_datetime(cls, value):
        if isinstance(value, datetime):
            return datetime.strftime(value, cls.DATETIME) if value else None
        return str(value)

    @classmethod
    def parse_to_datetime(cls, value_str):
        if value_str:
            if isinstance(value_str, datetime):
                return value_str
            if isinstance(value_str, str):
                return datetime.strptime(value_str, cls.DATETIME)
        return None

    @classmethod
    def parse_date(cls, value):
        if isinstance(value, date):
            return datetime.strftime(value, cls.DATE) if value else None
        return str(value)

    @classmethod
    def parse_to_date(cls, value_str):
        if value_str:
            if isinstance(value_str, date):
                return value_str
            if isinstance(value_str, str):
                return datetime.strptime(value_str, cls.DATE)
        return None

    @classmethod
    def bytes_to_large(cls, value, ext_code, stop_code='TB') -> (int, str):
        def upgrade_code():
            if ext_code == 'B':
                return 'KB'
            if ext_code == 'KB':
                return 'MB'
            if ext_code == 'MB':
                return 'GB'
            return 'TB'

        if value < 1024 or value == 'TB' or ext_code == stop_code:
            return value, ext_code

        return cls.bytes_to_large(value / 1024, upgrade_code())

    @classmethod
    def size_to_text(cls, value, ext_code='B', rounded=2) -> str:
        data = cls.bytes_to_large(value=value, ext_code=ext_code)
        return f'{round(data[0], rounded)} {data[1]}'
