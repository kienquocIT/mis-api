import json
from copy import deepcopy

from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from rest_framework.test import APIClient

from apps.core.tenant.models import TenantPlan
from apps.core.hr.models import Employee
from apps.sharedapp.data.base import FULL_PERMISSIONS_BY_CONFIGURED, FULL_PLAN_ID

from .utils import CustomizeEncoder
from ..permissions import PermissionsUpdateSerializer

__all__ = ['AdvanceTestCase']


class AdvanceTestCase(TestCase):
    tenant_code = 'MiS'
    admin_username = 'queptl'
    admin_password = 'queptl@1234'

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

    def call_another(self, testcase_cls: callable, func_name, args: list = None, kwargs: dict = None):
        args = args if (args and isinstance(args, list)) else []
        kwargs = kwargs if (kwargs and isinstance(kwargs, dict)) else {}

        test_cls = testcase_cls()
        test_cls.client = self.client
        result = getattr(test_cls, func_name, None)(*args, **kwargs)
        test_cls.tearDown()
        return result

    def authenticated(self, login_data=None):
        login_data = login_data if login_data is not None else self._login()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + login_data['token']['access_token'])

    def _new_tenant(self):
        url = reverse('NewTenant')
        data = {
            "tenant_data": {
                "title": "Cong Ty TNHH MiS",
                "code": self.tenant_code,
                "sub_domain": "MiS",
                "representative_fullname": "Nguyen Van A",
                "representative_phone_number": "0987654321",
                "auto_create_company": True,
                "company_quality_max": 5,
                "user_request_created": {
                    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    "full_name": "Nguyen Van A",
                    "email": "nva@mis.com",
                    "phone": "0987654321"
                },
                "plan": {}
            },
            "user_data": {
                "first_name": "Quế",
                "last_name": "Phan Thị Loan",
                "email": "ptlque@mis.com",
                "phone": "0988776655",
                "username": self.admin_username,
                "password": self.admin_password
            },
            "create_admin": True,
            "create_employee": True,
            "plan_data": {}
        }
        response = self.client.post(url, data, format='json')
        if response.status_code not in [200, 201]:
            print(response.status_code, response.data)
        resp_data = self.reload_json(response.data)
        self.assertResponseList(
            response,
            status_code=status.HTTP_200_OK,
            key_required=['result', 'status'],
            all_key=[
                'id', 'admin_info', 'user_request_created', 'title', 'date_created', 'date_modified', 'code', 'kind',
                'private_block', 'sub_domain', 'sub_domain_suffix',
                'representative_fullname', 'representative_phone_number', 'plan', 'auto_create_company',
                'company_quality_max', 'admin_created', 'company_total', 'admin',
            ],
            all_key_from=resp_data['result'],
            type_match={
                'result': dict,
                'status': int,
            }
        )
        self.assertCountEqual(
            ['id', 'date_created', 'date_modified', 'admin', 'user_request_created'],
            list(resp_data['result'].keys()),
            check_sum_second=False,
        )
        self.assertCountEqual(
            {
                'admin_info': {
                    'fullname': 'Quế Phan Thị Loan', 'phone_number': '0988776655', 'username': 'queptl',
                    'email': 'ptlque@mis.com'
                },
                'title': 'Cong Ty TNHH MiS',
                'code': 'MiS', 'kind': 0, 'private_block': '',
                'sub_domain': 'MiS', 'sub_domain_suffix': '.quantrimis.com.vn',
                'representative_fullname': 'Nguyen Van A', 'representative_phone_number': '0987654321',
                'plan': '{}', 'auto_create_company': True, 'company_quality_max': 5, 'admin_created': True,
                'company_total': 1,
            }.items(),
            resp_data['result'].items(),
            check_sum_second=False,
        )
        return resp_data['result']

    def _login(self):
        new_tenant = self._new_tenant()
        url = reverse('AuthLogin')
        data = {
            'tenant_code': self.tenant_code.lower(),
            'username': self.admin_username,
            'password': self.admin_password,
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertResponseList(
            response,
            status_code=status.HTTP_200_OK,
            key_required=['result', 'status'],
            all_key=['result', 'status'],
            all_key_from=response.data,
            type_match={
                'result': dict,
                'status': int,
            }
        )
        self.assertCountEqual(
            ['id', 'first_name', 'last_name', 'username_auth', 'username', 'email', 'last_login', 'is_admin_tenant',
             'language', 'tenant_current', 'company_current', 'space_current',
             'employee_current', 'companies', 'token',
             ],
            list(response.data['result'].keys()),
            check_sum_second=False,
        )
        self.assertCountEqual(
            ['access_token', 'refresh_token'],
            list(response.data['result']['token'].keys())
        )

        employee_current_id = response.data['result']['employee_current']['id']
        employee_obj = Employee.objects.get(pk=employee_current_id)
        tenant_current_id = response.data['result']['tenant_current']['id']
        if employee_current_id and tenant_current_id:
            TenantPlan.objects.bulk_create([
                TenantPlan(tenant_id=tenant_current_id, plan_id=x) for x in FULL_PLAN_ID
            ])
            PermissionsUpdateSerializer.force_permissions(
                instance=employee_obj, validated_data={'permission_by_configured': FULL_PERMISSIONS_BY_CONFIGURED}
            )
            employee_obj.save()
        return response.data['result']
