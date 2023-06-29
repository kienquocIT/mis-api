from django.urls import reverse
from rest_framework import status

from apps.masterdata.saledata.tests import ProductTestCase, TaxAndTaxCategoryTestCase, SalutationTestCase, \
    AccountGroupTestCase, IndustryTestCase
from apps.shared import AdvanceTestCase
from rest_framework.test import APIClient


# Create your tests here.


class TestCaseOpportunity(AdvanceTestCase):
    def setUp(self):
        self.maxDiff = None
        self.client = APIClient()

        self.authenticated()

    def create_product_type(self):
        url = reverse('ProductTypeList')
        response = self.client.post(
            url,
            {
                'title': 'San pham 1',
                'description': '',
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        return response

    def create_product_category(self):
        url = reverse('ProductCategoryList')
        response = self.client.post(
            url,
            {
                'title': 'Hardware',
                'description': '',
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        return response

    def create_uom_group(self):
        url = reverse('UnitOfMeasureGroupList')
        response = self.client.post(
            url,
            {
                'title': 'Time',
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        return response

    def create_uom(self):
        data_uom_gr = self.create_uom_group()
        url = reverse('UnitOfMeasureGroupList')
        response = self.client.post(
            url,
            {
                "code": "MIN",
                "title": "minute",
                "group": data_uom_gr.data['result']['id'],
                "ratio": 1,
                "rounding": 5,
                "is_referenced_unit": True
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        return response, data_uom_gr

    def test_create_new_tax_category(self):
        data = {
            "title": "Thuế doanh nghiệp kinh doanh tư nhân",
            "description": "Áp dụng cho các hộ gia đình kinh doanh tư nhân",
        }
        response = self.client.post(reverse('TaxCategoryList'), data, format='json')
        self.assertResponseList(
            response,
            status_code=status.HTTP_201_CREATED,
            key_required=['result', 'status'],
            all_key=['result', 'status'],
            all_key_from=response.data,
            type_match={'result': dict, 'status': int},
        )
        self.assertCountEqual(
            response.data['result'],
            ['id', 'title', 'description', 'is_default'],
            check_sum_second=True,
        )
        return response

    def create_tax(self):
        tax = TaxAndTaxCategoryTestCase.test_create_new_tax(self)
        return tax

    def test_create_product(self):
        self.url = reverse("ProductList")
        product = ProductTestCase.test_create_product(self)
        return product

    def get_employee(self):
        url = reverse("EmployeeList")
        response = self.client.get(url, format='json')
        return response

    def create_salutation(self):
        salutation = SalutationTestCase.test_create_new(self)
        return salutation

    def create_account_group(self):
        response = AccountGroupTestCase.test_create_new(self)
        return response

    def create_industry(self):
        response = IndustryTestCase.test_create_new(self)
        return response

    def get_account_type(self):
        url = reverse("AccountTypeList")
        response = self.client.get(url, format='json')
        return response

    def test_create_contact(self):
        url = reverse("ContactList")
        salutation = self.create_salutation()
        employee = self.get_employee()
        data = {
            "owner": employee.data['result'][0]['id'],
            "job_title": "Giám đốc nè",
            "biography": "không có",
            "fullname": "Trịnh Tuấn Nam",
            "salutation": salutation.data['result']['id'],
            "phone": "string",
            "mobile": "string",
            "email": "string",
            "report_to": None,
            "address_information": {},
            "additional_information": {},
            "account_name": None,
            "system_status": 0
        }

        response = self.client.post(url, data, format='json')
        return response

    def test_create_account(self):
        account_type = self.get_account_type().data['result'][0]['id']
        account_group = self.create_account_group().data['result']['id']
        employee = self.get_employee().data['result'][0]['id']
        contact = self.test_create_contact().data['result']['id']
        industry = self.create_industry().data['result']['id']

        data = {
            "name": "Công ty hạt giống, phân bón Trúc Phượng",
            "code": "AC01",
            "website": "trucphuong.com.vn",
            "account_type": [account_type],
            "owner": contact,
            "manager": {employee},
            "parent_account": None,
            "account_group": account_group,
            "tax_code": "string",
            "industry": industry,
            "annual_revenue": 1,
            "total_employees": 1,
            "phone": "string",
            "email": "string",
            "shipping_address": {},
            "billing_address": {},
            "contact_select_list": [
                contact
            ],
            "contact_primary": contact,
            "account_type_selection": 0,
            "system_status": 0
        }
        url = reverse("AccountList")
        response = self.client.post(url, data, format='json')
        return response

    def test_create_opportunity(self):
        self.url_tax = reverse('TaxList')
        emp = self.get_employee().data['result'][0]['id']
        customer = self.test_create_account().data['result']['id']
        data = {
            "title": "Dự Án Của Nam nè",
            "customer": customer,
            "product_category": [],
            "sale_person": emp
        }
        url = reverse("OpportunityList")
        response = self.client.post(url, data, format='json')

        self.assertResponseList(
            response,
            status_code=status.HTTP_201_CREATED,
            key_required=['result', 'status'],
            all_key=['result', 'status'],
            all_key_from=response.data,
            type_match={'result': dict, 'status': int},
        )
        self.assertCountEqual(
            response.data['result'],
            ['id', 'title', 'code', 'customer', 'sale_person', 'open_date', 'quotation_id', 'sale_order_id', 'opportunity_sale_team_datas'],
            check_sum_second=True,
        )

        data1 = {
            "title": "Dự Án Của Nam nè",
            "customer": '83de3bab-edc2-4d72-ac11-dfa4540cec88',
            "product_category": [],
            "sale_person": emp,

        }
        response1 = self.client.post(url, data1, format='json')

        self.assertResponseList(
            response1,
            status_code=status.HTTP_400_BAD_REQUEST,
            key_required=['errors', 'status'],
            all_key=['errors', 'status'],
            all_key_from=response1.data,
            type_match={'errors': dict, 'status': int},
        )
        self.assertCountEqual(
            response1.data['errors'],
            ['detail'],
            check_sum_second=True,
        )

        data2 = {
            "title": "Dự Án Của Nam nè",
            "customer": customer,
            "product_category": [],
            "sale_person": '83de3bab-edc2-4d72-ac11-dfa4540cec88'
        }
        response2 = self.client.post(url, data2, format='json')

        self.assertResponseList(
            response2,
            status_code=status.HTTP_400_BAD_REQUEST,
            key_required=['errors', 'status'],
            all_key=['errors', 'status'],
            all_key_from=response2.data,
            type_match={'errors': dict, 'status': int},
        )
        self.assertCountEqual(
            response2.data['errors'],
            ['detail'],
            check_sum_second=True,
        )

        return response
