import json
import random
import string

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
