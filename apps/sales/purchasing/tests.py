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
            "tax_type": 0
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
            ['id', 'title', 'code', 'rate', 'category', 'tax_type'],
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
            "account_type_selection": 0,
            "account_group": account_group,
            "manager": [
                employee
            ],
            "parent_account_mapped": None,
            "tax_code": "string",
            "industry": industry,
            "annual_revenue": 1,
            "total_employees": 1,
            "phone": "string",
            "email": "string",
            "contact_mapped": [
                {
                    'id': contact,
                    'is_account_owner': True
                }
            ],
            "system_status": 0
        }
        url = reverse("AccountList")
        response = self.client.post(url, data, format='json')
        return response

    def test_create_purchase_request(self):
        supplier = self.test_create_account()
        product = self.test_create_product()

        data = {
            "title": "Purchase Request 1",
            "supplier": supplier.data['result']['id'],
            "contact": supplier.data['result']['contact_mapped'][0]['id'],
            "request_for": 1,
            "sale_order": None,
            "delivered_date": "2029-08-11",
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
             'purchase_status', 'contact', 'note', 'purchase_request_product_datas', 'pretax_amount', 'taxes',
             'total_price'],
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
        response = self.client.get(url, format='json')  # noqa
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

    def test_update_purchase_request(self):
        purchase_request = self.test_create_purchase_request()
        unit_price = 20000000
        quantity = 3
        product = purchase_request.data['result']['purchase_request_product_datas'][0]['product']
        tax = purchase_request.data['result']['purchase_request_product_datas'][0]['tax']
        uom = purchase_request.data['result']['purchase_request_product_datas'][0]['uom']
        url = reverse("PurchaseRequestDetail", kwargs={'pk': purchase_request.data['result']['id']})
        data = {
            "purchase_request_product_datas": [
                {
                    "sale_order_product": None,
                    "product": product['id'],
                    "description": "",
                    "uom": uom['id'],
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "tax": tax['id'],
                    "sub_total_price": quantity * unit_price
                }
            ],
            "pretax_amount": quantity * unit_price,
            "taxes": quantity * unit_price * (tax['rate'] / 100),
            "total_price": (quantity * unit_price) + (quantity * unit_price * (
                        tax['rate'] / 100)),
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data_changed = self.test_get_detail_purchase_request(data_id=purchase_request.data['result']['id'])
        self.assertEqual(
            data_changed.data['result']['purchase_request_product_datas'][0]['sub_total_price'],
            unit_price * quantity
        )
        self.assertEqual(
            data_changed.data['result']['pretax_amount'],
            unit_price * quantity
        )
        return response


# PO
class TestCasePurchaseOrder(AdvanceTestCase):
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
            "tax_type": 0
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
            ['id', 'title', 'code', 'rate', 'category', 'tax_type'],
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
        response = AccountGroupTestCase.test_create_new(self, code="AG0002", title="AG test PO")
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
            "code": "SUP01",
            "website": "trucphuong.com.vn",
            "account_type": [account_type],
            "account_type_selection": 0,
            "account_group": account_group,
            "manager": [
                employee
            ],
            "parent_account_mapped": None,
            "tax_code": "string",
            "industry": industry,
            "annual_revenue": 1,
            "total_employees": 1,
            "phone": "string",
            "email": "string",
            "contact_mapped": [
                {
                    'id': contact,
                    'is_account_owner': True
                }
            ],
            "system_status": 0
        }
        url = reverse("AccountList")
        response = self.client.post(url, data, format='json')
        return response

    def test_create_purchase_order_no_pr(self):
        account_create = self.test_create_account()
        product_create = self.test_create_product()
        supplier = account_create.data['result']['id']
        contact = account_create.data['result']['contact_mapped'][0]['id']
        product = product_create.data['result']['id']
        uom = product_create.data['result']['sale_information']['default_uom']['uom_id']
        tax = product_create.data['result']['sale_information']['tax']['id']

        data = {
            "title": "test PO no PQ",
            "supplier": supplier,
            "contact": contact,
            "purchase_requests_data": [],
            "delivered_date": "2023-10-09 12:00:00",
            "status_delivered": 0,
            "purchase_order_products_data": [
                {
                    "product": product,
                    "product_title": "Máy tính Core I7",
                    "product_code": "JUN01",
                    "product_description": "",
                    "uom_order_request": uom,
                    "uom_order_actual": uom,
                    "tax": tax,
                    "product_tax_title": "VAT-8",
                    "product_tax_value": 8,
                    "product_tax_amount": 24000,
                    "product_quantity_order_request": 3,
                    "product_quantity_order_actual": 3,
                    "stock": 0,
                    "product_unit_price": 100000,
                    "product_subtotal_price": 300000,
                    "product_subtotal_price_after_tax": 324000,
                    "order": 1,
                    "purchase_request_products_data": []
                }
            ],
            "total_product_pretax_amount": 300000,
            "total_product_tax": 24000,
            "total_product": 324000,
            "total_product_revenue_before_tax": 300000,
            "system_status": 1
        }

        url = reverse("PurchaseOrderList")
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
                'supplier',
                'delivered_date',
                'receipt_status',
                'system_status',
            ],
            check_sum_second=True,
        )

        return response

    def test_get_list_purchase_order(self):
        self.test_create_purchase_order_no_pr()
        url = reverse('PurchaseOrderList')
        response = self.client.get(url, format='json')
        self.assertResponseList(  # noqa
            response,
            status_code=status.HTTP_200_OK,
            key_required=['result', 'status', 'next', 'previous', 'count', 'page_size'],
            all_key=['result', 'status', 'next', 'previous', 'count', 'page_size'],
            all_key_from=response.data,
            type_match={'result': list, 'status': int, 'next': int, 'previous': int, 'count': int,
                        'page_size': int},
        )
        self.assertEqual(
            len(response.data['result']), 1
        )
        self.assertCountEqual(
            response.data['result'][0],
            [
                'id',
                'title',
                'code',
                'supplier',
                'delivered_date',
                'receipt_status',
                'system_status',
            ],
            check_sum_second=True,
        )
        return response

    def test_get_detail_purchase_order(self, data_id=None):
        data_created = None
        if not data_id:
            data_created = self.test_create_purchase_order_no_pr()
            data_id = data_created.data['result']['id']
        url = reverse("PurchaseOrderDetail", kwargs={'pk': data_id})
        response = self.client.get(url, format='json')  # noqa
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
            [
                'id',
                'title',
                'code',
                'purchase_requests_data',
                'purchase_quotations_data',
                'purchase_request_products_data',
                'supplier',
                'contact',
                'delivered_date',
                'status_delivered',
                'receipt_status',
                # purchase order tabs
                'purchase_order_products_data',
                # total amount
                'total_product_pretax_amount',
                'total_product_tax',
                'total_product',
                'total_product_revenue_before_tax',
                # system
                'system_status',
                'workflow_runtime_id',
                'is_active',
            ],
            check_sum_second=True,
        )
        if not data_id:
            self.assertEqual(response.data['result']['id'], data_created.data['result']['id'])
            self.assertEqual(response.data['result']['title'], data_created.data['result']['title'])
        else:
            self.assertEqual(response.data['result']['id'], data_id)
        return response
