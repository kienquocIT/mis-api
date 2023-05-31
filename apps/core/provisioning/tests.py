from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from apps.shared import AdvanceTestCase


class TestCaseProvisioning(AdvanceTestCase):
    def setUp(self) -> None:
        self.maxDiff = None
        self.client = APIClient()

    def test_new_tenant(self):
        return self._new_tenant()

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
        if len(response_data['result']) == 1:
            self.assertCountEqual(
                [{'title': 'Cong Ty TNHH MiS', 'code': 'mis'}],
                response_data['result']
            )
