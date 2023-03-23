import json
from copy import deepcopy

from django.test import TestCase

from rest_framework.test import APIClient

from .utils import CustomizeEncoder

__all__ = ['AdvanceTestCase']


class AdvanceTestCase(TestCase):
    client = APIClient()

    @staticmethod
    def reload_json(data):
        return json.loads(json.dumps(data, cls=CustomizeEncoder))

    def assertCountEqual(self, first, second, msg=None, check_sum_second=True):
        if check_sum_second is False:
            if isinstance(first, list) and isinstance(second, list):
                first_method = deepcopy(list(first))
                second_method = deepcopy(list(second))
                diff = list(set(second_method) - set(first_method))
                for key in diff:
                    second_method.remove(key)
            elif isinstance(first, dict) and isinstance(second, dict):
                first_method = deepcopy(dict(first))
                second_method = deepcopy(dict(second))
                diff = list(set(second_method.keys()) - set(first_method.keys()))
                for key in diff:
                    del second_method[key]
            elif isinstance(first, type({}.items())) and isinstance(second, type({}.items())):
                first_dict = {
                    x[0]: x[1] for x in first
                }
                second_dict = {
                    x[0]: x[1] for x in second
                }
                diff = list(set([x1 for x1 in second_dict]) - set(x2 for x2 in first_dict))
                for key in diff:
                    del second_dict[key]
                first_method = dict(first_dict.items())
                second_method = dict(second_dict.items())
            else:
                return self.fail(
                    'First or Second type are incorrect. Type of First = {}, Type of Second = {}'.format(
                        type(first), type(second)
                    )
                )
            return super().assertCountEqual(first_method, second_method, msg)
        return super().assertCountEqual(first, second, msg)

    def assertResponseList(
            self,
            resp,
            status_code,
            key_required: list[str] = list,
            all_key: list[str] = list,
            all_key_from: dict = dict,
            type_match: dict = dict,
    ):
        resp_data = self.reload_json(resp.data)
        self.assertEqual(resp.status_code, status_code)
        self.assertEqual(resp_data['status'], status_code)
        if key_required:
            self.assertCountEqual(
                key_required,
                resp_data
            )
        if all_key:
            if all_key_from:
                self.assertCountEqual(
                    all_key,
                    all_key_from.keys()
                )
            else:
                self.fail('if all_key had value, all_key_from is required.')
        if type_match:
            for key, __type in type_match.items():
                self.assertIsInstance(resp_data[key], __type)

    @classmethod
    def call_another(cls, testcase_cls: callable, func_name):
        test_result = testcase_cls()
        test_result.setUp()
        result = getattr(test_result, func_name, None)()
        test_result.tearDown()
        return result

    def authenticated(self, login_data):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + login_data['token']['access_token'])
