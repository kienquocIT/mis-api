from django.urls import reverse
from rest_framework import status

from apps.core.auths.tests import TestCaseAuth
from apps.shared import AdvanceTestCase
from rest_framework.test import APIClient


class AccountTestCase(AdvanceTestCase):
    def setUp(self):
        self.maxDiff = None
        self.client = APIClient()

        login_data = TestCaseAuth.test_login(self)
        self.authenticated(login_data)
        # create industry
        url_create_industry = reverse('IndustryList')
        response_industry = self.client.post(
            url_create_industry,
            {
                'code': 'I01',
                'title': 'Banking',
            },
            format='json'
        )

        # create account type
        url_create_account_type = reverse('AccountTypeList')
        response_account_type = self.client.post(
            url_create_account_type,
            {
                'code': 'AT01',
                'title': 'customer',
            },
            format='json'
        )

        self.industry = response_industry.data['result']
        self.account_type = response_account_type.data['result']

    def test_create_new_account(self):
        data = {
            'name': 'Công Ty Hạt Giống Trúc Phượng',
            'code': 'PM002',
            'website': 'trucphuong.com.vn',
            'tax_code': '81H1',
            'annual_revenue': '10-20 billions',
            'total_employees': '< 20 people',
            'phone': '0903608494',
            'email': 'cuong@gmail.com',
            'industry': self.industry['id'],
            'manager': ['a2c0cf06-5221-417c-8d4d-149c015b428e',
                        'ca3f9aae-884f-4791-a1b9-c7a33d51dbdf'],
            'account_type': [str(self.account_type['id'])],
            'customer_type': 'individual',
        }
        url = reverse('AccountList')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        return response

    def test_create_account_duplicate_code(self):
        self.test_create_new_account()
        data = {
            'name': 'Công Ty Hạt Giống Trúc Phượng',
            'code': 'PM002',
            'website': 'trucphuong.com.vn',
            'tax_code': '81H1',
            'annual_revenue': '10-20 billions',
            'total_employees': '< 20 people',
            'phone': '0903608494',
            'email': 'cuong@gmail.com',
            'industry': self.industry['id'],
            'manager': ['a2c0cf06-5221-417c-8d4d-149c015b428e',
                        'ca3f9aae-884f-4791-a1b9-c7a33d51dbdf'],
            'account_type': [str(self.account_type['id'])],
            'customer_type': 'individual',
        }
        url = reverse('AccountList')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)
        return response

    def test_create_missing_data(self):
        data = {
            'website': 'trucphuong.com.vn',
            'tax_code': '81H1',
            'annual_revenue': '10-20 billions',
            'total_employees': '< 20 people',
            'phone': '0903608494',
            'email': 'cuong@gmail.com',
            'industry': self.industry['id'],
            'manager': ['a2c0cf06-5221-417c-8d4d-149c015b428e',
                        'ca3f9aae-884f-4791-a1b9-c7a33d51dbdf'],
            'account_type': [str(self.account_type['id'])],
            'customer_type': 'individual',
        }
        url = reverse('AccountList')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)
        return response

    def test_data_not_UUID(self):
        data = {
            'name': 'Công Ty Hạt Giống Trúc Phượng',
            'code': 'PM002',
            'website': 'trucphuong.com.vn',
            'tax_code': '81H1',
            'annual_revenue': '10-20 billions',
            'total_employees': '< 20 people',
            'phone': '0903608494',
            'email': 'cuong@gmail.com',
            'industry': '1',
            'manager': ['a2c0cf06-5221-417c-8d4d-149c015b428e',
                        'ca3f9aae-884f-4791-a1b9-c7a33d51dbdf'],
            'account_type': '1',
            'customer_type': 'individual',
        }
        url = reverse('AccountList')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)
        return response


class ProductTestCase(AdvanceTestCase):
    def setUp(self):
        self.maxDiff = None
        self.client = APIClient()

        login_data = TestCaseAuth.test_login(self)
        self.authenticated(login_data)
        self.url = reverse("ProductList")

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
        return response.data['result']

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
        return response.data['result']

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
        return response.data['result']

    def create_uom(self):
        data_uom_gr = self.create_uom_group()
        url = reverse('UnitOfMeasureGroupList')
        response = self.client.post(
            url,
            {
                "code": "MIN",
                "title": "minute",
                "group": data_uom_gr['id'],
                "ratio": 1,
                "rounding": 5,
                "is_referenced_unit": True
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        return response.data['result'], data_uom_gr

    def test_create_product_missing_code(self):
        product_type = self.create_product_type()
        product_category = self.create_product_category()
        unit_of_measure, uom_group = self.create_uom()
        data1 = {
            "code": "P01",
            "title": "Laptop HP HLVVL6R",
            "general_information": {
                'product_type': product_type['id'],
                'product_category': product_category['id'],
                'uom_group': uom_group['id']
            },
            "inventory_information": {},
            "sale_information": {},
            "purchase_information": {}
        }
        response1 = self.client.post(
            self.url,
            data1,
            format='json'
        )
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)

        data2 = {
            "code": "",
            "title": "Laptop HP HLVVL6R",
            "general_information": {
                'product_type': product_type['id'],
                'product_category': product_category['id'],
                'uom_group': uom_group['id']
            },
            "inventory_information": {},
            "sale_information": {},
            "purchase_information": {}
        }
        response2 = self.client.post(
            self.url,
            data2,
            format='json'
        )
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        return True

    def test_create_product_missing_title(self):
        data = {
            "code": "P01",
            "general_information": {
            },
            "inventory_information": {},
            "sale_information": {},
            "purchase_information": {}
        }
        response = self.client.post(
            self.url,
            data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_product_duplicate_code(self):
        product_type = self.create_product_type()
        product_category = self.create_product_category()
        unit_of_measure, uom_group = self.create_uom()
        data1 = {
            "code": "P01",
            "title": "Laptop HP HLVVL6R",
            "general_information": {
                'product_type': product_type['id'],
                'product_category': product_category['id'],
                'uom_group': uom_group['id']
            },
            "inventory_information": {},
            "sale_information": {},
            "purchase_information": {}
        }
        response1 = self.client.post(
            self.url,
            data1,
            format='json'
        )
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)

        data2 = {
            "code": "P01",
            "title": "Laptop Dell HLVVL6R",
            "general_information": {
                'product_type': product_type['id'],
                'product_category': product_category['id'],
                'uom_group': uom_group['id']
            },
            "inventory_information": {},
            "sale_information": {},
            "purchase_information": {}
        }
        response2 = self.client.post(
            self.url,
            data2,
            format='json'
        )
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        return False

    def test_create_product_not_UUID(self):
        product_type = self.create_product_type()
        product_category = self.create_product_category()
        unit_of_measure, uom_group = self.create_uom()
        data = {
            "code": "P01",
            "title": "Laptop Dell HLVVL6R",
            "general_information": {
                'product_type': product_type['id'],
                'product_category': product_category['id'],
                'uom_group': uom_group['id']
            },
            "sale_information": {
                'default_uom': unit_of_measure['id']
            },
            "inventory_information": {
                'uom': unit_of_measure['id'],
                'inventory_level_min': 5,
                'inventory_level_max': 20
            }
        }
        response = self.client.post(
            self.url,
            data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data1 = {
            "code": "P02",
            "title": "Laptop HP HLVVL6R",
            "general_information": {
                'product_type': '1',
                'product_category': '1',
                'uom_group': '1'
            },
            "inventory_information": {},
            "sale_information": {},
            "purchase_information": {}
        }
        response1 = self.client.post(
            self.url,
            data1,
            format='json'
        )
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        return False


class SalutationTestCase(AdvanceTestCase):
    def setUp(self):
        self.maxDiff = None
        self.client = APIClient()

        login_data = TestCaseAuth.test_login(self)
        self.authenticated(login_data)
        # create industry

    def test_create_new(self):
        data = {
            "code": "S01",
            "title": "Mr",
            "description": "A man"
        }
        url = reverse('SalutationList')
        response = self.client.post(url, data, format='json')
        self.assertCountEqual(
            ['id', 'title', 'code', 'description'],
            list(response.data['result'].keys()),
            check_sum_second=False,
        )
        self.assertEqual(response.status_code, 201)
        return response

    def test_duplicate_code(self):
        data1 = {  # noqa
            "code": "S01",
            "title": "Mr",
            "description": "A man"
        }
        url = reverse('SalutationList')
        response = self.client.post(url, data1, format='json')
        self.assertCountEqual(
            ['id', 'title', 'code', 'description'],
            list(response.data['result'].keys()),
            check_sum_second=False,
        )

        data2 = {  # noqa
            "code": "S01",
            "title": "Miss",
            "description": "A Human"
        }
        url = reverse('SalutationList')
        response2 = self.client.post(url, data2, format='json')
        self.assertEqual(response2.status_code, 400)
        return True

    def test_missing_data(self):
        data = {  # noqa
            "code": "S01",
            "description": "A Human"
        }
        url = reverse('SalutationList')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)

        data1 = {  # noqa
            "code": "S01",
            "title": "Mr"
        }
        url = reverse('SalutationList')
        response1 = self.client.post(url, data1, format='json')
        self.assertEqual(response1.status_code, 201)

        data2 = {  # noqa
            "title": "Miss",
            "description": "A Human"
        }
        url = reverse('SalutationList')
        response2 = self.client.post(url, data2, format='json')
        self.assertEqual(response2.status_code, 201)
        return True

    def test_get_salutation(self):
        salutation = self.test_create_new()
        url = reverse('SalutationList')
        url_detail = reverse('SalutationDetail', args=[salutation.data['result']['id']])

        response = self.client.get(url)
        response_detail = self.client.get(url_detail)
        self.assertEqual(response.status_code, 200)
        self.assertCountEqual(
            ['id', 'title', 'code', 'description'],
            list(response_detail.data['result'].keys()),
            check_sum_second=False,
        )
        return True


class UoMTestCase(AdvanceTestCase):
    def setUp(self):
        self.maxDiff = None
        self.client = APIClient()

        login_data = TestCaseAuth.test_login(self)
        self.authenticated(login_data)

    def test_create_new_uom_group(self):
        data = {
            "title": "Unit"
        }
        url = reverse('UnitOfMeasureGroupList')
        response = self.client.post(url, data, format='json')
        self.assertCountEqual(
            ['id', 'title'],
            list(response.data['result'].keys()),
            check_sum_second=False,
        )
        self.assertEqual(response.status_code, 201)
        return response

    def test_create_new_uom(self):
        uom_group = self.test_create_new_uom_group()
        data = {
            "code": "U01",
            "title": "Unit",
            "group": uom_group.data['result']['id'],
            "ratio": 1,
            "rounding": 5,
            "is_referenced_unit": True
        }
        url = reverse('UnitOfMeasureList')
        response = self.client.post(url, data, format='json')
        self.assertCountEqual(
            ['id', 'code', 'title', 'group', 'ratio', 'rounding'],
            list(response.data['result'].keys()),
            check_sum_second=False,
        )
        self.assertEqual(response.status_code, 201)
        return response


class ConfigPaymentTermTestCase(AdvanceTestCase):
    def setUp(self):
        self.maxDiff = None
        self.client = APIClient()

        login_data = TestCaseAuth.test_login(self)
        self.authenticated(login_data)

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

    def test_create_missing_data(self):
        data = {
            'title': 'config payment term 01',
            'apply_for': 1,
            'remark': 'lorem ipsum dolor sit amet.',
        }
        url = reverse('ConfigPaymentTermList')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)
        return response

    def test_create_empty_data(self):
        data = {
            'title': 'config payment term 01',
            'apply_for': 1,
            'remark': 'lorem ipsum dolor sit amet.',
            "term": []
        }
        url = reverse('ConfigPaymentTermList')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)
        return response

    def test_get_list(self):
        self.test_create_config_payment_term()
        url = reverse('ConfigPaymentTermList')
        response = self.client.get(url, format='json')
        self.assertResponseList(
            response,
            status_code=status.HTTP_200_OK,
            key_required=['result', 'status', 'next', 'previous', 'count', 'page_size'],
            all_key=['result', 'status', 'next', 'previous', 'count', 'page_size'],
            all_key_from=response.data,
            type_match={'result': list, 'status': int, 'next': int, 'previous': int, 'count': int, 'page_size': int},
        )
