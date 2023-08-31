import json
from django.utils.translation import gettext as _

from django.urls import reverse
from rest_framework import status

from apps.masterdata.saledata.tests import ProductTestCase, SalutationTestCase, \
    AccountGroupTestCase, IndustryTestCase
from apps.shared.extends.tests import AdvanceTestCase
from rest_framework.test import APIClient


# Create your tests here.


class TestCasePurchaseRequest(AdvanceTestCase):
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
        url = reverse('UnitOfMeasureList')
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

    def get_base_unit_measure(self):
        url = reverse('BaseItemUnitList')
        response = self.client.get(url, format='json')
        return response

    def create_new_tax_category(self):
        url_tax_category = reverse("TaxCategoryList")
        data = {
            "title": "Thuế doanh nghiệp kinh doanh tư nhân",
            "description": "Áp dụng cho các hộ gia đình kinh doanh tư nhân",
        }
        response = self.client.post(url_tax_category, data, format='json')
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

    def create_new_tax(self):
        url_tax = reverse("TaxList")
        tax_category = self.create_new_tax_category()
        data = {
            "title": "Thuế bán hành VAT-10%",
            "code": "VAT-10",
            "rate": 10,
            "category": tax_category.data['result']['id'],
            "type": 0
        }
        response = self.client.post(url_tax, data, format='json')
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
            ['id', 'title', 'code', 'rate', 'category', 'type'],
            check_sum_second=True,
        )
        return response

    def get_price_list(self):
        url = reverse('PriceList')
        response = self.client.get(url, format='json')
        return response

    def get_currency(self):
        url = reverse('CurrencyList')
        response = self.client.get(url, format='json')
        return response

    def test_create_product(self):
        self.url = reverse("ProductList")
        product = ProductTestCase.test_create_product(self)
        return product

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

    def get_employee(self):
        url = reverse("EmployeeList")
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
            "account_type_selection": 0,
            "system_status": 0
        }
        url = reverse("AccountList")
        response = self.client.post(url, data, format='json')
        return response

    def test_create_purchase_request(self):
        supplier = self.test_create_account()
        product = self.test_create_product()
        emp_current = self.get_employee()

        data = {
            "title": "Purchase Request 1",
            "supplier": supplier.data['result']['id'],
            "contact": supplier.data['result']['owner']['id'],
            "request_for": 1,
            "sale_order": None,
            "delivered_date": "2023-08-11",
            "purchase_status": 0,
            "note": "",
            "purchase_request_product_datas": [
                {
                    "sale_order_product": None,
                    "product": product.data['result']['id'],
                    "description": "",
                    "uom": product.data['result']['sale_information']['default_uom']['uom_id'],
                    "quantity": 1,
                    "unit_price": 20000000,
                    "tax": product.data['result']['sale_information']['tax']['id'],
                    "sub_total_price": 20000000
                }
            ],
            "pretax_amount": 20000000,
            "taxes": 2000000,
            "total_price": 22000000,
            "employee_created": emp_current.data['result'][0]['id']
        }

        url = reverse("PurchaseRequestList")
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
            ['id', 'code', 'title', 'request_for', 'sale_order', 'supplier', 'delivered_date', 'system_status',
             'purchase_status', ],
            check_sum_second=True,
        )

        return response

    def test_get_list_purchase_request(self):
        self.test_create_purchase_request()
        url = reverse('PurchaseRequestList')
        response = self.client.get(url, format='json')
        self.assertResponseList(  # noqa
            response,
            status_code=status.HTTP_200_OK,
            key_required=['result', 'status', 'next', 'previous', 'count', 'page_size'],
            all_key=['result', 'status', 'next', 'previous', 'count', 'page_size'],
            all_key_from=response.data,
            type_match={'result': list, 'status': int, 'next': int, 'previous': int, 'count': int, 'page_size': int},
        )
        self.assertEqual(
            len(response.data['result']), 1
        )
        self.assertCountEqual(
            response.data['result'][0],
            ['id', 'code', 'title', 'request_for', 'sale_order', 'supplier', 'delivered_date', 'system_status',
             'purchase_status', ],
            check_sum_second=True,
        )
        return response

    def test_get_detail_purchase_request(self, data_id=None):
        data_created = None
        if not data_id:
            data_created = self.test_create_purchase_request()
            data_id = data_created.data['result']['id']
        url = reverse("PurchaseRequestDetail", kwargs={'pk': data_id})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
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
            ['id', 'title', 'code', 'request_for', 'supplier', 'contact', 'delivered_date', 'system_status',
             'purchase_status', 'note', 'sale_order', 'purchase_request_product_datas', 'pretax_amount',
             'taxes', 'total_price', ],
            check_sum_second=True,
        )
        if not data_id:
            self.assertEqual(response.data['result']['id'], data_created.data['result']['id'])
            self.assertEqual(response.data['result']['title'], data_created.data['result']['title'])
        else:
            self.assertEqual(response.data['result']['id'], data_id)
        return response
