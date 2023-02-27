import json
import random
import string
from typing import Union

from uuid import UUID


class LinkListHandler:
    def __init__(self, ll=None):
        self.ll = {} if not isinstance(ll, dict) else ll

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


class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            # if the obj is uuid, we simply return the value of uuid
            return str(obj)
        return json.JSONEncoder.default(self, obj)


class TypeCheck(object):
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
        return True if data_checked else False

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
        return True if (len(result) == len(data) and all(result) is True) else False
