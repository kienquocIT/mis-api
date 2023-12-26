from django.urls import reverse
from rest_framework.test import APIClient

from apps.core.hr.models import Employee
from apps.shared.extends.tests import AdvanceTestCase


class AssetToolsTestCase(AdvanceTestCase):
    def setUp(self):
        self.maxDiff = None  # noqa
        self.client = APIClient()
        self.authenticated()
        url_emp = reverse("EmployeeList")
        response = self.client.get(url_emp, format='json')
        employee_obj = Employee.objects.get(id=response.data['result'][0]['id'])
        self.employee = employee_obj

    def test_get_asset_tools_config(self):
        url = reverse('AssetToolConfigDetail')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)

    def test_update_asset_tools_config(self):
        is_url = reverse('AssetToolConfigDetail')
        url = reverse('ProductTypeList')
        response_type = self.client.post(
            url,
            {
                'title': 'San pham 1',
                'description': '',
            },
            format='json'
        )
        self.assertEqual(response_type.status_code, 201)
        data_update = {'product_type_id': response_type.data['result']['id']}
        self.client.put(is_url, data_update, format='json')
        response = self.client.get(is_url, format='json')
        self.assertEqual(response.status_code, 200)
