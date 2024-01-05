from django.urls import reverse
from rest_framework import status
from apps.shared.extends.tests import AdvanceTestCase
from rest_framework.test import APIClient


# Create your tests here.


class TestCaseProcess(AdvanceTestCase):
    def setUp(self):
        self.maxDiff = None
        self.client = APIClient()

        self.authenticated()

    def test_get_list_sale_function(self):
        url = reverse('FunctionProcessList')
        response = self.client.get(url, format='json')  # noqa
        self.assertResponseList(  # noqa
            response,
            status_code=status.HTTP_200_OK,
            key_required=['result', 'status', 'next', 'previous', 'count', 'page_size'],
            all_key=['result', 'status', 'next', 'previous', 'count', 'page_size'],
            all_key_from=response.data,
            type_match={'result': list, 'status': int, 'next': int, 'previous': int, 'count': int, 'page_size': int},
        )
        self.assertEqual(
            len(response.data['result']), 12
        )
        self.assertCountEqual(
            response.data['result'][0],
            ['id', 'function', 'is_free', 'is_in_process', 'is_default'],
            check_sum_second=True,
        )
        return response

    def test_get_process(self):
        url = reverse('ProcessDetail')
        response = self.client.get(url, format='json')
        self.assertResponseList(  # noqa
            response,
            status_code=status.HTTP_200_OK,
            key_required=['result', 'status'],
            all_key=['result', 'status'],
            all_key_from=response.data,
            type_match={'result': dict, 'status': int},
        )
        self.assertCountEqual(
            response.data['result'],
            ['id', 'process_step_datas'],
            check_sum_second=True,
        )
        return response

    def test_update_process(self):
        list_function = self.test_get_list_sale_function()
        url = reverse('ProcessDetail')
        data = {
            "process_step_datas": [
                {
                    "step": [
                        {
                            "function_id": list_function.data['result'][1]['id'],
                            "function_title": list_function.data['result'][1]['function']['title'],
                            "subject": "Subject 1",
                            "is_current": True,
                            "is_completed": False
                        }
                    ]
                },
                {
                    "step": [
                        {
                            "function_id": list_function.data['result'][4]['id'],
                            "function_title": list_function.data['result'][4]['function']['title'],
                            "subject": "Subject 2.1",
                            "is_current": True,
                            "is_completed": False
                        },
                        {
                            "function_id": list_function.data['result'][5]['id'],
                            "function_title": list_function.data['result'][5]['function']['title'],
                            "subject": "Subject 2.2",
                            "is_current": True,
                            "is_completed": False
                        },
                    ]
                },
                {
                    "step": [
                        {
                            "function_id": list_function.data['result'][6]['id'],
                            "function_title": list_function.data['result'][6]['function']['title'],
                            "subject": "Subject 3",
                            "is_current": True,
                            "is_completed": False
                        }
                    ]
                },
                {
                    "step": [
                        {
                            "function_id": list_function.data['result'][2]['id'],
                            "function_title": list_function.data['result'][2]['function']['title'],
                            "subject": "Subject 4",
                            "is_current": True,
                            "is_completed": False
                        }
                    ]
                },

            ]
        }

        response = self.client.put(url, data, format='json')
        data_change = self.test_get_process()
        return response
