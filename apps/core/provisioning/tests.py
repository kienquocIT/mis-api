from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from apps.shared import AdvanceTestCase


class TestCaseProvisioning(AdvanceTestCase):
    def setUp(self) -> None:
        self.maxDiff = None
        self.client = APIClient()

    def test_new_tenant(self):
        url = reverse('NewTenant')
        data = {
            "tenant_data": {
                "title": "Cong Ty TNHH MiS",
                "code": "MiS",
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
                "username": "queptl",
                "password": "queptl@1234"
            },
            "create_admin": True,
            "create_employee": True,
            "plan_data": {}
        }
        response = self.client.post(url, data, format='json')
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

    def test_tenant_list(self):
        url = reverse('NewTenant')
        self.test_new_tenant()
        response = self.client.get(url, format='json')
        response_data = self.reload_json(response.data)
        self.assertResponseList(
            response,
            status_code=status.HTTP_200_OK,
            key_required=['result', 'status'],
            all_key=['result', 'status'],
            all_key_from=response.data,
            type_match={'result': list, 'status': int},
        )
        self.assertCountEqual(
            [{'title': 'Cong Ty TNHH MiS', 'code': 'mis'}],
            response_data['result']
        )
