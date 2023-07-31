from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from apps.core.provisioning.tests import TestCaseProvisioning
from apps.shared.extends.tests import AdvanceTestCase


class TestCaseAuth(AdvanceTestCase):
    def setUp(self) -> None:
        self.maxDiff = None
        self.client = APIClient()

    def test_login(self):
        return self._login()

    def test_my_profile(self):
        self.authenticated()
        url = reverse('MyProfile')
        response = self.client.get(url, format='json')
        self.assertResponseList(
            response,
            status_code=status.HTTP_200_OK,
            key_required=['result', 'status'],
            all_key=[
                'id', 'first_name', 'last_name', 'username_auth', 'username', 'email', 'last_login', 'is_admin_tenant',
                'language', 'tenant_current', 'company_current', 'space_current', 'employee_current', 'companies',
            ],
            all_key_from=response.data['result']['data'],
            type_match={
                'result': dict,
                'status': int,
            }
        )
        return response.data['result']['data']

    def test_alive_check(self):
        self.authenticated()
        url = reverse('AliveCheck')
        response = self.client.get(url, format='json')
        self.assertResponseList(
            response,
            status_code=status.HTTP_200_OK,
            key_required=['result', 'status'],
            all_key=['state'],
            all_key_from=response.data['result'],
            type_match={
                'result': dict,
                'status': int,
            }
        )
        self.assertEqual(response.data['result']['state'], 'You are still alive.')
        return response.data

    def test_refresh_token(self):
        login_data = self.test_login()
        self.authenticated(login_data)
        url = reverse('AuthRefreshLogin')
        data = {'refresh': login_data['token']['refresh_token']}
        response = self.client.post(url, data, format='json')
        self.assertResponseList(
            response,
            status_code=status.HTTP_200_OK,
            key_required=['result', 'status'],
            all_key=['access_token', ],
            all_key_from=response.data['result'],
            type_match={
                'result': dict,
                'status': int,
            }
        )
        return response.data['result']

    def test_switch_company(self):
        # call login
        # call add to another company, in tenant.
        # call main VIEW test
        return True

