from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from apps.masterdata.saledata.tests import ExpenseTestCase
from apps.shared.extends.tests import AdvanceTestCase


class BusinessTripTestCase(AdvanceTestCase):
    def get_base_currency(self):
        response = self.client.get(reverse("BaseCurrencyList"), format='json')
        self.assertEqual(response.status_code, 200)
        return response

    def setUp(self):
        self.maxDiff = None  # noqa
        self.client = APIClient()
        self.authenticated()

        company_data = {
            'title': 'Cty TNHH one member',
            'code': 'BUSINESS_MMT',
            'representative_fullname': 'Mike Nguyen',
            'address': '7826 avenue, Victoria Street, California, American',
            'email': 'mike.nguyen.7826@gmail.com',
            'phone': '0983875345',
            'primary_currency': self.get_base_currency().data['result'][0]['id']
        }
        self.company = self.client.post(reverse("CompanyList"), company_data, format='json')

        url_tax_category = reverse("TaxCategoryList")
        data = {
            "title": "Thuế doanh nghiệp kinh doanh tư nhân",
            "description": "Áp dụng cho các hộ gia đình kinh doanh tư nhân",
        }
        tax_category = self.client.post(url_tax_category, data, format='json')

        data = {
            "title": "Thuế bán hành VAT-10%",
            "code": "B-VAT-10",
            "rate": 10,
            "category": tax_category.data['result']['id'],
            "tax_type": 0
        }
        tax = self.client.post(reverse("TaxList"), data, format='json')
        self.tax = tax.data['result']

    def get_employee(self):
        url = reverse("EmployeeList")
        response = self.client.get(url, format='json')
        return response

    def get_expense_item(self):
        expense_item = ExpenseTestCase.create_expense_item(self)
        return expense_item

    def get_city(self):
        url_city = reverse("CityList")
        city = self.client.get(url_city, format='json')
        return city

    def test_create_business_trip(self):
        data = {
            'title': 'Test tạo phiếu công tác trong nước',
            'remark': 'công tác xem sét hiện trạng nhà máy',
            'employee_inherit_id': self.get_employee().data['result'][0]['id'],
            'expense_items': [
                {
                    'title': 'Chi phí đi lại',
                    'expense_item': self.get_expense_item().data['result']['id'],
                    'uom_txt': 'Chuyến',
                    'quantity': 2,
                    'price': '1000000',
                    'tax': self.tax['id'],
                    'subtotal': 1100000,
                    'order': 1
                }
            ],
            'date_created': timezone.now(),
            'departure': self.get_city().data['result'][0]['id'],
            'destination': self.get_city().data['result'][0]['id'],
            'employee_on_trip': [str(self.get_employee().data['result'][0]['id'])],
            'date_f': timezone.now(),
            'morning_f': True,
            'date_t': timezone.now() + timedelta(days=10),
            'morning_t': False,
            'total_day': 10,
            'pretax_amount': 1000000,
            'taxes': 100000,
            'total_amount': 1100000
        }
        response = self.client.post(reverse('BusinessTripRequestList'), data, format='json')
        self.assertEqual(response.status_code, 201)
        return response

    def test_get_detail_business_trip(self):
        res = self.test_create_business_trip()
        url = reverse('BusinessTripRequestDetail', args=[res.data['result'].get('id', '')])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, res.data['result'].get('id', ''), None, response.status_code)
        self.assertContains(response, res.data['result'].get('title', ''), None, response.status_code)

    def test_update_business_trip(self):
        res = self.test_create_business_trip()
        url = reverse('BusinessTripRequestDetail', args=[res.data['result'].get('id', '')])
        data_update = {
            'title': 'Test tạo phiếu công tác trong nước updated',
        }
        self.client.put(url, data_update, format='json')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
