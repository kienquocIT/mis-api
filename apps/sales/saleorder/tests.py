from django.urls import reverse
from rest_framework import status

from apps.masterdata.saledata.tests import ProductTestCase, TaxAndTaxCategoryTestCase, IndustryTestCase
from apps.shared.extends.tests import AdvanceTestCase
from rest_framework.test import APIClient


# Create your tests here.


class TestCaseSaleOrder(AdvanceTestCase):
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

    def create_new_tax_category(self):
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

    def get_base_unit_measure(self):
        url = reverse('BaseItemUnitList')
        response = self.client.get(url, format='json')
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

    def get_employee(self):
        url = reverse("EmployeeList")
        response = self.client.get(url, format='json')
        return response

    def create_industry(self):
        response = IndustryTestCase.test_create_new(self)
        return response

    def get_account_type(self):
        url = reverse("AccountTypeList")
        response = self.client.get(url, format='json')
        return response

    def test_create_config_payment_term(self):
        data = {
            'title': 'config payment term 01',
            'apply_for': 1,
            'remark': 'lorem ipsum dolor sit amet.',
            'term': [
                {
                    "value": '100% sau khi ký HD',
                    "unit_type": 1,
                    "day_type": 1,
                    "no_of_days": "1",
                    "after": 1
                }
            ],
        }
        url = reverse('ConfigPaymentTermList')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        return response

    def test_create_sale_order(self):
        data_salutation = {  # noqa
            "code": "S01ORDER",
            "title": "MrORDER",
            "description": "A man"
        }
        url_salutation = reverse('SalutationList')
        response_salutation = self.client.post(url_salutation, data_salutation, format='json')
        url_contact = reverse("ContactList")
        salutation = response_salutation.data['result']['id']
        employee = self.get_employee().data['result'][0]['id']
        data_contact = {
            "owner": employee,
            "job_title": "Giám đốc nè",
            "biography": "không có",
            "fullname": "Trịnh Tuấn Nam",
            "salutation": salutation,
            "phone": "string",
            "mobile": "string",
            "email": "string",
            "report_to": None,
            "address_information": {},
            "additional_information": {},
            "account_name": None,
            "system_status": 0
        }
        response_contact = self.client.post(url_contact, data_contact, format='json')
        url_account_group = reverse("AccountGroupList")
        data_account_group = {  # noqa
            "code": "AG01ORDER",
            "title": "Nhóm khách hàng test đơn hàng",
            "description": ""
        }
        response_account_group = self.client.post(url_account_group, data_account_group, format='json')
        account_type = self.get_account_type().data['result'][0]['id']
        account_group = response_account_group.data['result']['id']
        contact = response_contact.data['result']['id']
        industry = self.create_industry().data['result']['id']
        data_account = {
            "name": "Công ty hạt giống, phân bón Trúc Phượng",
            "code": "AC01ORDER",
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
        response_account = self.client.post(url, data_account, format='json')
        opportunity = None
        customer = response_account.data['result']['id']
        employee = self.get_employee().data['result'][0]['id']
        payment_term = self.create_config_payment_term().data['result']['id']
        data = {
            "title": "Đơn hàng test",
            "opportunity": opportunity,
            "customer": customer,
            "contact": contact,
            "sale_person": employee,
            "payment_term": payment_term,
        }
        url = reverse("SaleOrderList")
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
            [
                'id',
                'title',
                'code',
                'opportunity',
                'customer',
                'contact',
                'sale_person',
                'payment_term',
                'quotation',
                'system_status',
                # sale order tabs
                'sale_order_products_data',
                'sale_order_logistic_data',
                'customer_shipping_id',
                'customer_billing_id',
                'sale_order_costs_data',
                'sale_order_expenses_data',
                # total amount of products
                'total_product_pretax_amount',
                'total_product_discount_rate',
                'total_product_discount',
                'total_product_tax',
                'total_product',
                'total_product_revenue_before_tax',
                # total amount of costs
                'total_cost_pretax_amount',
                'total_cost_tax',
                'total_cost',
                # total amount of expenses
                'total_expense_pretax_amount',
                'total_expense_tax',
                'total_expense',
                'date_created',
                'delivery_call',
                # indicator tab
                'sale_order_indicators_data',
            ],
            check_sum_second=True,
        )
        return response

    def test_get_list_sale_order(self):
        self.test_create_sale_order()
        url = reverse('SaleOrderList')
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
            len(response.data['result']), 2
        )
        self.assertCountEqual(
            response.data['result'][0],
            [
                'id',
                'title',
                'code',
                'customer',
                'sale_person',
                'date_created',
                'total_product',
                'system_status',
                'opportunity',
                'quotation',
                'delivery_call',
            ],
            check_sum_second=True,
        )
        return response
