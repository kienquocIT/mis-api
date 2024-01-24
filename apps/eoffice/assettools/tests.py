from django.urls import reverse
from django.utils import timezone
from rest_framework import status
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
        self.product_type = self.client.post(
            reverse('ProductTypeList'),
            {
                'title': 'San pham 1',
                'description': '',
            },
            format='json'
        )
        self.prod_category = self.client.post(
            reverse('ProductCategoryList'),
            {
                'title': 'Hardware',
                'description': '',
            },
            format='json'
        )
        self.uom_group = self.client.post(
            reverse('UnitOfMeasureGroupList'),
            {
                'title': 'Time',
            },
            format='json'
        )
        self.uom = self.client.post(
            reverse('UnitOfMeasureList'),
            {
                "code": "MIN",
                "title": "minute",
                "group": self.uom_group.data['result']['id'],
                "ratio": 1,
                "rounding": 5,
                "is_referenced_unit": True
            },
            format='json'
        )
        self.tax_category = self.client.post(
            reverse("TaxCategoryList"),
            {
                "title": "Thuế doanh nghiệp kinh doanh tư nhân",
                "description": "Áp dụng cho các hộ gia đình kinh doanh tư nhân",
            }, format='json'
        )
        self.tax = self.client.post(
            reverse("TaxList"),
            {
                "title": "Thuế bán hành VAT-10%",
                "code": "VAT-10",
                "rate": 10,
                "category": self.tax_category.data['result']['id'],
                "tax_type": 0
            }
            , format='json'
        )
        currency = self.client.get(reverse('CurrencyList'), format='json')
        currency_id = currency.data['result'][3]['id']
        price_list = self.client.get(reverse('PriceList'), format='json')
        price_list_id = price_list.data['result'][0]['id']
        # create product
        data = {
            "code": 'ASSETPROD001',
            "title": "Macbook Air 15″",
            'product_choice': [0, 1, 2],
            # general
            'product_types_mapped_list': [self.product_type.data['result']['id']],
            'general_product_category': self.prod_category.data['result']['id'],
            'general_uom_group': self.uom_group.data['result']['id'],
            'length': 50,
            'width': 30,
            'height': 10,
            'volume': 15000,
            'weight': 200,
            # sale
            'sale_default_uom': self.uom.data['result']['id'],
            'sale_tax': self.tax.data['result']['id'],
            'sale_currency_using': currency_id,
            'sale_product_price_list': [
                {
                    'price_list_id': price_list_id,
                    'price_value': 20000000,
                    'is_auto_update': False,
                }
            ],
            # inventory
            'inventory_uom': self.uom.data['result']['id'],
            'inventory_level_min': 5,
            'inventory_level_max': 20,
            # purchase
            'purchase_default_uom': self.uom.data['result']['id'],
            'purchase_tax': self.tax.data['result']['id'],
        }
        prod_resp = self.client.post(
            reverse("ProductList"),
            data,
            format='json'
        )
        self.assertEqual(prod_resp.status_code, 201)
        self.product = prod_resp

        self.warehouse = self.client.post(
            reverse('WareHouseList'),
            {
                "title": "Kho công cụ, dụng cụ",
                "remark": 'if we vibe, we vibe',
                "full_address": '1696 Arden Way, Sacramento, California, United States'
            },
            format='json'
        )

    def test_get_asset_tools_config(self):
        url = reverse('AssetToolConfigDetail')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)

    def test_update_asset_tools_config(self):
        is_url = reverse('AssetToolConfigDetail')
        data_update = {
            'product_type_id': self.product_type.data['result']['id'],
            'warehouse': self.warehouse.data['result']['id']}
        self.client.put(is_url, data_update, format='json')
        response = self.client.get(is_url, format='json')
        self.assertEqual(response.status_code, 200)

    def test_create_asset_provide(self):
        time_now = timezone.now().strftime('%Y-%m-%d')
        data = {
            'date_created': time_now,
            'title': 'Asset, tools create test',
            "employee_inherit_id": str(self.employee.id),
            "products": [
                {
                    "product": self.product.data['result']['id'],
                    "order": 1,
                    "tax": self.tax.data['result']['id'],
                    "uom": self.uom.data['result']['id'],
                    "quantity": 1,
                    "price": 100,
                    "subtotal": 100,
                    "product_remark": "lorem ipsum"
                }
            ],
            "system_status": 1,
            "pretax_amount": 100,
            "taxes": 10,
            "total_amount": 110
        }
        response = self.client.post(reverse('AssetToolsProvideRequestList'), data, format='json')
        self.assertEqual(response.status_code, 201)
        return response

    def test_get_list_asset_provide(self):
        self.test_create_asset_provide()
        response = self.client.get(reverse('AssetToolsProvideRequestList'), format='json')
        self.assertResponseList(  # noqa
            response,
            status_code=status.HTTP_200_OK,
            key_required=['result', 'status', 'next', 'previous', 'count', 'page_size'],
            all_key=['result', 'status', 'next', 'previous', 'count', 'page_size'],
            all_key_from=response.data,
            type_match={'result': list, 'status': int, 'next': int, 'previous': int, 'count': int, 'page_size': int},
        )

    def test_get_detail_asset_provide(self):
        res = self.test_create_asset_provide()
        url = reverse('AssetToolsProvideRequestDetail', args=[res.data['result'].get('id', '')])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, res.data['result'].get('id', ''), None, response.status_code)
        self.assertContains(response, res.data['result'].get('title', ''), None, response.status_code)

    def test_update_asset_provide(self):
        res = self.test_create_asset_provide()
        url = reverse('AssetToolsProvideRequestDetail', args=[res.data['result'].get('id', '')])
        data_update = {
            'title': 'Test update provide asset tools',
            'employee_inherit_id': str(self.employee.id),
            "products": [
                {
                    "product": self.product.data['result']['id'],
                    "order": 1,
                    "tax": self.tax.data['result']['id'],
                    "uom": self.uom.data['result']['id'],
                    "quantity": 1,
                    "price": 1000,
                    "subtotal": 1000,
                    "product_remark": "lorem ipsum updated"
                }
            ],
        }
        self.client.put(url, data_update, format='json')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)

    def test_create_asset_delivery(self):
        time_now = timezone.now().strftime('%Y-%m-%d')
        provided = self.test_create_asset_provide()
        data = {
            'date_created': time_now,
            'title': 'Asset, tools delivery create',
            "employee_inherit_id": str(self.employee.id),
            "provide": provided.data['result']['id'],
            "products": [
                {
                    "product": self.product.data['result']['id'],
                    "order": 1,
                    "tax": self.tax.data['result']['id'],
                    "uom": self.uom.data['result']['id'],
                    "quantity": 1,
                    "price": 100,
                    "subtotal": 100,
                    "product_remark": "lorem ipsum"
                }
            ],
            "system_status": 1,
        }
        # response = self.client.post(reverse('AssetToolsProvideRequestList'), data, format='json')
        # self.assertEqual(response.status_code, 201)
        # return response
