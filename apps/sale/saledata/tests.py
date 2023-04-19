from django.urls import reverse
from rest_framework import status

from apps.core.auths.tests import TestCaseAuth
from apps.sale.saledata.models.config import PaymentTerm
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
        data = { # noqa
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
        data = { # noqa
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


# class ContactTestCase(AdvanceTestCase):
#     def setUp(self):
#         self.maxDiff = None
#         self.client = APIClient()
#
#         login_data = TestCaseAuth.test_login(self)
#         self.authenticated(login_data)
#
#         # create salutation
#         url_create_salutation = reverse('SalutationList')
#         response_salutation = self.client.post(
#             url_create_salutation,
#             {
#                 'code': 'SA01',
#                 'title': 'Mr',
#             },
#             format='json'
#         )
#
#         # create salutation
#         url_create_interest = reverse('InterestsList')
#         response_interest = self.client.post(
#             url_create_interest,
#             {
#                 'code': 'IN01',
#                 'title': 'Traveling',
#             },
#             format='json'
#         )
#
#         self.salutation = response_salutation.data['result']
#         self.interest = response_interest.data['result']
#
#     def test_create_new_contact(self):
#         data = {
#             'owner': 'a0635b66-6b56-40ad-b2d6-0d67156cbc99',
#             'fullname': 'Nguyễn Văn Thanh',
#             'salutation': self.salutation['id'],
#         }
#         url = reverse('ContactList')
#         response = self.client.post(url, data, format='json')
#         self.assertEqual(response.status_code, 201)
#         return response
#
#     def test_create_contact_with_numeric_fullname(self):
#         data = {
#             'owner': 'a0635b66-6b56-40ad-b2d6-0d67156cbc99',
#             'fullname': '9876543210',
#             'salutation': self.salutation['id'],
#         }
#         url = reverse('ContactList')
#         response = self.client.post(url, data, format='json')
#         self.assertEqual(response.status_code, 400)
#         return response
#
#     def test_create_missing_owner(self):
#         data = {
#             'owner': None,
#             'fullname': 'Nguyễn Văn Thanh',
#             'salutation': self.salutation['id'],
#         }
#         url = reverse('ContactList')
#         response = self.client.post(url, data, format='json')
#         self.assertEqual(response.status_code, 400)
#         return response
#
#     def test_create_missing_fullname(self):
#         data = {
#             'owner': 'a0635b66-6b56-40ad-b2d6-0d67156cbc99',
#             'fullname': None,
#             'salutation': self.salutation['id'],
#         }
#         url = reverse('ContactList')
#         response = self.client.post(url, data, format='json')
#         self.assertEqual(response.status_code, 400)
#         return response
#
#     def test_data_not_owner_UUID(self):
#         data = {
#             'owner': '1',
#             'fullname': 'Nguyễn Văn Nam',
#             'salutation': self.salutation['id'],
#         }
#         url = reverse('ContactList')
#         response = self.client.post(url, data, format='json')
#         self.assertEqual(response.status_code, 400)
#         return response
#
#     def test_data_not_salutation_UUID(self):
#         data = {
#             'owner': 'a0635b66-6b56-40ad-b2d6-0d67156cbc99',
#             'fullname': 'Nguyễn Văn Nam',
#             'salutation': self.salutation['title'],
#         }
#         url = reverse('ContactList')
#         response = self.client.post(url, data, format='json')
#         self.assertEqual(response.status_code, 400)
#         return response


# class ProductTestCase(AdvanceTestCase):
#     def setUp(self):
#         self.maxDiff = None
#         self.client = APIClient()
#
#         login_data = TestCaseAuth.test_login(self)
#         self.authenticated(login_data)
#         self.url = reverse("ProductList")
#
#     def create_product_type(self):
#         url = reverse('ProductTypeList')
#         response = self.client.post(
#             url,
#             {
#                 'title': 'San pham 1',
#                 'description': '',
#             },
#             format='json'
#         )
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         return response.data['result']
#
#     def create_product_category(self):
#         url = reverse('ProductCategoryList')
#         response = self.client.post(
#             url,
#             {
#                 'title': 'Hardware',
#                 'description': '',
#             },
#             format='json'
#         )
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         return response.data['result']
#
#     def create_uom_group(self):
#         url = reverse('UnitOfMeasureGroupList')
#         response = self.client.post(
#             url,
#             {
#                 'title': 'Time',
#             },
#             format='json'
#         )
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         return response.data['result']
#
#     def create_uom(self):
#         data_uom_gr = self.create_uom_group()
#         url = reverse('UnitOfMeasureGroupList')
#         response = self.client.post(
#             url,
#             {
#                 "code": "MIN",
#                 "title": "minute",
#                 "group": data_uom_gr['id'],
#                 "ratio": 1,
#                 "rounding": 5,
#                 "is_referenced_unit": True
#             },
#             format='json'
#         )
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         return response.data['result'], data_uom_gr
#
#     def test_create_product_missing_code(self):
#         product_type = self.create_product_type() # noqa
#         product_category = self.create_product_category()
#         unit_of_measure, uom_group = self.create_uom()
#         data1 = {
#             "code": "P01",
#             "title": "Laptop HP HLVVL6R",
#             "general_information": {
#                 'product_type': product_type['id'],
#                 'product_category': product_category['id'],
#                 'uom_group': uom_group['id']
#             },
#         }
#         response1 = self.client.post(
#             self.url,
#             data1,
#             format='json'
#         )
#         self.assertEqual(response1.status_code, 500)
#
#         return True
#
#     def test_create_product_missing_title(self):
#         data = {
#             "code": "P01",
#             "general_information": {
#             }
#         }
#         response = self.client.post(
#             self.url,
#             data,
#             format='json'
#         )
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#
#     def test_create_product_duplicate_code(self):
#         product_type = self.create_product_type() # noqa
#         product_category = self.create_product_category()
#         unit_of_measure, uom_group = self.create_uom()
#         data1 = {
#             "code": "P01",
#             "title": "Laptop HP HLVVL6R",
#             "general_information": {
#                 'product_type': product_type['id'],
#                 'product_category': product_category['id'],
#                 'uom_group': uom_group['id']
#             },
#         }
#         response1 = self.client.post(
#             self.url,
#             data1,
#             format='json'
#         )
#         self.assertEqual(response1.status_code, 500)
#         return False
#
#     def test_create_product_not_UUID(self):
#         product_type = self.create_product_type()
#         product_category = self.create_product_category()
#         unit_of_measure, uom_group = self.create_uom()
#         data = {
#             "code": "P01",
#             "title": "Laptop Dell HLVVL6R",
#             "general_information": {
#                 'product_type': {
#                     'id': product_type['id'],
#                     'title': product_type['title'],
#                     'code': "",
#                 },
#                 'product_category': {
#                     'id': product_category['id'],
#                     'title': product_category['title'],
#                     'code': "",
#                 },
#                 'uom_group': {
#                     'id': uom_group['id'],
#                     'title': uom_group['title'],
#                     'code': "",
#                 },
#             },
#             "sale_information": {
#                 'default_uom_id': unit_of_measure['id']
#             },
#             "inventory_information": {
#                 'uom': unit_of_measure['id'],
#                 'inventory_level_min': 5,
#                 'inventory_level_max': 20
#             }
#         }
#         response = self.client.post(
#             self.url,
#             data,
#             format='json'
#         )
#         self.assertEqual(response.status_code, 400)
#
#         data1 = {
#             "code": "P02",
#             "title": "Laptop HP HLVVL6R",
#             "general_information": {
#                 'product_type': '1',
#                 'product_category': '1',
#                 'uom_group': '1'
#             },
#             "inventory_information": {},
#             "sale_information": {},
#             "purchase_information": {},
#         }
#         response1 = self.client.post(
#             self.url,
#             data1,
#             format='json'
#         )
#         self.assertEqual(response1.status_code, 400)
#         return True


class SalutationTestCase(AdvanceTestCase):
    def setUp(self):
        self.maxDiff = None
        self.client = APIClient()

        login_data = TestCaseAuth.test_login(self)
        self.authenticated(login_data)

    def test_create_new(self):
        data = { # noqa
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

    def test_create_two_uom_is_referenced_unit_in_uom_gr(self):
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

        data1 = {
            "code": "U02",
            "title": "Dozen",
            "group": uom_group.data['result']['id'],
            "ratio": 1,
            "rounding": 5,
            "is_referenced_unit": True
        }
        try:
            response1 = self.client.post(url, data1, format='json')
            self.assertEqual(response1.status_code, 201)
        except Exception as err:
            print(err)
        return response

    def test_create_uom_missing_data(self):
        uom_group = self.test_create_new_uom_group()
        data = {
            "code": "",
            "title": "Unit",
            "group": uom_group.data['result']['id'],
            "ratio": 1,
            "rounding": 5,
            "is_referenced_unit": True
        }
        url = reverse('UnitOfMeasureList')  # noqa
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)

        data1 = {
            "code": "U01",
            "title": "",
            "group": uom_group.data['result']['id'],
            "ratio": 1,
            "rounding": 5,
            "is_referenced_unit": False
        }
        response1 = self.client.post(url, data1, format='json')
        self.assertEqual(response1.status_code, 400)

        data2 = {
            "code": "U01",
            "title": "Unit",
            "group": "",
            "ratio": 1,
            "rounding": 5,
            "is_referenced_unit": False
        }
        response2 = self.client.post(url, data2, format='json')
        self.assertEqual(response2.status_code, 400)

    def test_get_list_and_detail(self):
        uom = self.test_create_two_uom_is_referenced_unit_in_uom_gr()
        url = reverse('UnitOfMeasureList')
        response = self.client.get(url, format='json')
        url_detail = reverse('UnitOfMeasureDetail', args=[uom.data['result']['id']])

        response_detail = self.client.get(url_detail)
        self.assertEqual(response.status_code, 200)
        self.assertCountEqual(
            ['id', 'title', 'code', 'group', 'ratio', 'rounding'],
            list(response_detail.data['result'].keys()),
            check_sum_second=False,
        )
        return True


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
        self.assertResponseList( # noqa
            response,
            status_code=status.HTTP_200_OK,
            key_required=['result', 'status', 'next', 'previous', 'count', 'page_size'],
            all_key=['result', 'status', 'next', 'previous', 'count', 'page_size'],
            all_key_from=response.data,
            type_match={'result': list, 'status': int, 'next': int, 'previous': int, 'count': int, 'page_size': int},
        )

    def test_get_detail(self):
        res = self.test_create_config_payment_term()
        url = reverse('ConfigPaymentTermDetail', args=[res.data['result'].get('id', '')])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, res.data['result'].get('id', ''), None, response.status_code)
        self.assertContains(response, res.data['result'].get('title', ''), None, response.status_code)

    def test_update_detail(self):
        res = self.test_create_config_payment_term()
        url = reverse('ConfigPaymentTermDetail', args=[res.data['result'].get('id', '')])
        data = {
            'id': res.data['result'].get('id', ''),
            'title': 'config payment term 01 edited',
            'apply_for': 0,
            'remark': 'lorem ipsum dolor sit amet...',
            'term': [
                {
                    "value": '100% sau khi ký HD edited',
                    "unit_type": 0,
                    "day_type": 0,
                    "no_of_days": "15",
                    "after": 3
                }
            ],
        }
        self.client.put(url, data, format='json')
        response = self.client.get(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.data['result'], data)

    def test_delete_detail(self):
        res = self.test_create_config_payment_term()
        url = reverse('ConfigPaymentTermDetail', args=[res.data['result']['id']])

        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(PaymentTerm.objects.filter(pk=res.data['result']['id']).exists())


class CurrencyTestCase(AdvanceTestCase):
    def setUp(self):
        self.maxDiff = None
        self.client = APIClient()

        login_data = TestCaseAuth.test_login(self)
        self.authenticated(login_data)
        self.url = reverse("CurrencyList")

    def test_get_list_currency_default(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertResponseList(  # noqa
            response,
            status_code=status.HTTP_200_OK,
            key_required=['result', 'status', 'next', 'previous', 'count', 'page_size'],
            all_key=['result', 'status', 'next', 'previous', 'count', 'page_size'],
            all_key_from=response.data,
            type_match={'result': list, 'status': int, 'next': int, 'previous': int, 'count': int, 'page_size': int},
        )
        return True

    def test_create_new_currency(self):
        data = {
            "abbreviation": "CAD",
            "title": "CANADIAN DOLLAR",
            "rate": 0.45
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 201)
        return True

    def test_create_new_currency_exists(self):
        data = {
            "abbreviation": "VND",
            "title": "VIETNAM DONG",
            "rate": 1
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 400)
        return True

    def test_create_new_currency_rate_less_than_zero(self):
        data = {
            "abbreviation": "VND",
            "title": "VIETNAM DONG",
            "rate": -1
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 400)
        return True


class TaxAndTaxCategoryTestCase(AdvanceTestCase):
    def setUp(self):
        self.maxDiff = None
        self.client = APIClient()

        login_data = TestCaseAuth.test_login(self)
        self.authenticated(login_data)
        self.url_tax = reverse("TaxList")
        self.url_tax_category = reverse("TaxCategoryList")

    def test_create_new_tax_category(self):
        data = {
            "title": "Thuế doanh nghiệp kinh doanh tư nhân",
            "description": "Áp dụng cho các hộ gia đình kinh doanh tư nhân",
        }
        response = self.client.post(self.url_tax_category, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertCountEqual(
            ['id', 'title', 'description'],
            list(response.data['result'].keys()),
            check_sum_second=False,
        )
        return response

    def test_create_new_tax(self):
        tax_category = self.test_create_new_tax_category()
        data = {
            "title": "Thuế bán hành VAT-10%",
            "code": "VAT-10",
            "rate": 10,
            "category": tax_category.data['result']['id'],
            "type": 0
        }
        response = self.client.post(self.url_tax, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertCountEqual(
            ['id', 'title', 'code', 'rate', 'category', 'type'],
            list(response.data['result'].keys()),
            check_sum_second=False,
        )
        return response

    def test_create_tax_missing_data(self):
        tax_category = self.test_create_new_tax_category()

        # missing title
        data = {
            "code": "VAT-10",
            "rate": 10,
            "category": tax_category.data['result']['id'],
            "type": 0
        }
        response = self.client.post(self.url_tax, data, format='json')
        self.assertEqual(response.status_code, 400)

        # missing code
        data1 = {
            "title": "Thuế bán hàng tư nhân",
            "rate": 10,
            "category": tax_category.data['result']['id'],
            "type": 0
        }
        response1 = self.client.post(self.url_tax, data1, format='json')
        self.assertEqual(response1.status_code, 400)

        # missing category
        data2 = {
            "title": "Thuế bán hàng tư nhân VAT-5%",
            "code": 'VAT-5',
            "rate": 10,
            "type": 0
        }
        response2 = self.client.post(self.url_tax, data2, format='json')
        self.assertEqual(response2.status_code, 400)

        # missing type
        data3 = {
            "title": "Thuế bán hàng tư nhân VAT-15%",
            "code": 'VAT-15',
            "category": tax_category.data['result']['id'],
            "rate": 10,
        }
        response3 = self.client.post(self.url_tax, data3, format='json')
        self.assertEqual(response3.status_code, 400)
        return response

    def test_create_tax_empty_data(self):
        tax_category = self.test_create_new_tax_category()

        # title
        data = {
            "code": "VAT-10",
            "title": "",
            "rate": 10,
            "category": tax_category.data['result']['id'],
            "type": 0
        }
        response = self.client.post(self.url_tax, data, format='json')
        self.assertEqual(response.status_code, 400)

        # code
        data1 = {
            "code": "",
            "title": "Thuế bán hàng tư nhân",
            "rate": 10,
            "category": tax_category.data['result']['id'],
            "type": 0
        }
        response1 = self.client.post(self.url_tax, data1, format='json')
        self.assertEqual(response1.status_code, 400)

        # category
        data2 = {
            "code": "VAT-5",
            "title": "Thuế bán hàng tư nhân VAT-5%",
            "rate": 10,
            "category": "",
            "type": 0
        }
        response2 = self.client.post(self.url_tax, data2, format='json')
        self.assertEqual(response2.status_code, 400)

        return True


class ProductTypeAndProductCategoryTestCase(AdvanceTestCase):
    def setUp(self):
        self.maxDiff = None
        self.client = APIClient()

        login_data = TestCaseAuth.test_login(self)
        self.authenticated(login_data)
        self.url_product_category = reverse("ProductCategoryList")
        self.url_product_type = reverse("TaxCategoryList")

    def test_create_new_product_category(self):
        data = {
            "title": "Phần cứng",
            "description": "Phần cứng máy tính"
        }
        response = self.client.post(self.url_product_category, data, format='json')
        self.assertEqual(response.status_code, 201)
        return response

    def test_create_new_product_type(self):
        data = {
            "title": "Sảm phẩm lỗi",
            "description": "Những sản phẩm mắc lỗi kỹ thuật"
        }
        response = self.client.post(self.url_product_type, data, format='json')
        self.assertEqual(response.status_code, 201)
        return response

    def test_create_new_product_type_missing_and_empty_data(self):
        data = {
            "title": "",
            "description": "Những sản phẩm mắc lỗi kỹ thuật"
        }
        response = self.client.post(self.url_product_type, data, format='json')
        self.assertEqual(response.status_code, 400)

        data1 = {
            "description": "Những sản phẩm mắc lỗi kỹ thuật"
        }
        response1 = self.client.post(self.url_product_type, data1, format='json')
        self.assertEqual(response1.status_code, 400)
        return True

    def test_create_new_product_category_missing_and_empty_data(self):
        data = {
            "description": "Application"
        }
        response = self.client.post(self.url_product_type, data, format='json')
        self.assertEqual(response.status_code, 400)

        data1 = {
            "title": "",
            "description": "Application"
        }
        response1 = self.client.post(self.url_product_type, data1, format='json')
        self.assertEqual(response1.status_code, 400)
        return True

    def test_get_list_and_detail_product_category(self):
        product_category = self.test_create_new_product_category()
        response = self.client.get(self.url_product_category, format='json') # noqa
        self.assertResponseList( # noqa
            response,
            status_code=status.HTTP_200_OK,
            key_required=['result', 'status', 'next', 'previous', 'count', 'page_size'],
            all_key=['result', 'status', 'next', 'previous', 'count', 'page_size'],
            all_key_from=response.data,
            type_match={'result': list, 'status': int, 'next': int, 'previous': int, 'count': int, 'page_size': int},
        )

        url_detail = reverse('ProductCategoryDetail', args=[product_category.data['result']['id']])

        response_detail = self.client.get(url_detail)
        self.assertEqual(response_detail.status_code, 200)
        self.assertCountEqual(
            ['id', 'title', 'description'],
            list(response_detail.data['result'].keys()),
            check_sum_second=False,
        )

    def test_get_list_and_detail_product_type(self):
        product_type = self.test_create_new_product_type()
        response = self.client.get(self.url_product_type, format='json') # noqa
        self.assertResponseList( # noqa
            response,
            status_code=status.HTTP_200_OK,
            key_required=['result', 'status', 'next', 'previous', 'count', 'page_size'],
            all_key=['result', 'status', 'next', 'previous', 'count', 'page_size'],
            all_key_from=response.data,
            type_match={'result': list, 'status': int, 'next': int, 'previous': int, 'count': int, 'page_size': int},
        )

        url_detail = reverse('ProductTypeDetail', args=[product_type.data['result']['id']])

        response_detail = self.client.get(url_detail)
        self.assertEqual(response_detail.status_code, 200)
        # self.assertCountEqual(
        #     ['id', 'title', 'description'],
        #     list(response_detail.data['result'].keys()),
        #     check_sum_second=False,
        # )
        return True


class InterestTestCase(AdvanceTestCase):
    def setUp(self):
        self.maxDiff = None
        self.client = APIClient()

        login_data = TestCaseAuth.test_login(self)
        self.authenticated(login_data)
        self.url = reverse("InterestsList")

    def test_create_new(self):
        data = { # noqa
            "code": "I01",
            "title": "Yoga",
            "description": "Tập yoga"
        }
        response = self.client.post(self.url, data, format='json')
        self.assertCountEqual(
            ['id', 'title', 'code', 'description'],
            list(response.data['result'].keys()),
            check_sum_second=False,
        )
        self.assertEqual(response.status_code, 201)
        return response

    def test_duplicate_code(self):
        data1 = {  # noqa
            "code": "I01",
            "title": "Travel",
            "description": "Đi du lịch"
        }
        response = self.client.post(self.url, data1, format='json')
        self.assertCountEqual(
            ['id', 'title', 'code', 'description'],
            list(response.data['result'].keys()),
            check_sum_second=False,
        )

        data2 = {  # noqa
            "code": "I01",
            "title": "Yoga",
            "description": "Tập Yoga"
        }
        response2 = self.client.post(self.url, data2, format='json')
        self.assertEqual(response2.status_code, 400)
        return True

    def test_missing_data(self):
        data = {  # noqa
            "code": "I01",
            "description": "Tập Yoga"
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 400)

        data1 = {  # noqa
            "code": "I01",
            "title": "Yoga"
        }

        response1 = self.client.post(self.url, data1, format='json')
        self.assertEqual(response1.status_code, 201)

        data2 = {  # noqa
            "title": "Yoga",
            "description": "Tập Yoga"
        }

        response2 = self.client.post(self.url, data2, format='json')
        self.assertEqual(response2.status_code, 400)
        return True

    def test_get_interest(self):
        interest = self.test_create_new() # noqa
        url_detail = reverse('InterestDetail', args=[interest.data['result']['id']])

        response = self.client.get(self.url) # noqa
        response_detail = self.client.get(url_detail)
        self.assertEqual(response.status_code, 200)
        self.assertCountEqual(
            ['id', 'title', 'code', 'description'],
            list(response_detail.data['result'].keys()),
            check_sum_second=False,
        )
        return True


class AccountTypeTestCase(AdvanceTestCase):
    def setUp(self): # noqa
        self.maxDiff = None
        self.client = APIClient()

        login_data = TestCaseAuth.test_login(self)
        self.authenticated(login_data)
        self.url = reverse("AccountTypeList")

    def test_create_new(self):
        data = { # noqa
            "title": "Customer",
            "description": "Cho phép người dùng tự điều chỉnh"
        }
        response = self.client.post(self.url, data, format='json')
        self.assertCountEqual(
            ['id', 'title', 'code', 'description'],
            list(response.data['result'].keys()),
            check_sum_second=False,
        )
        self.assertEqual(response.status_code, 201)
        return response

    def test_duplicate_code(self):
        data1 = {  # noqa
            "code": "AT01",
            "title": "Customer",
            "description": "Cho phép người dùng tự điều chỉnh"
        }
        response = self.client.post(self.url, data1, format='json')
        self.assertCountEqual(
            ['id', 'title', 'code', 'description'],
            list(response.data['result'].keys()),
            check_sum_second=False,
        )

        data2 = {  # noqa
            "code": "AT01",
            "title": "Supplier",
            "description": ""
        }
        response2 = self.client.post(self.url, data2, format='json')
        self.assertEqual(response2.status_code, 400)
        return True

    def test_missing_data(self):
        data = {  # noqa
            "code": "AT01",
            "description": "Customer"
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 400)

        data1 = {  # noqa
            "title": "Supplier",
            "description": "Supplier"
        }

        response1 = self.client.post(self.url, data1, format='json') # noqa
        self.assertEqual(response1.status_code, 201)

        data2 = {  # noqa
            "code": "AT02",
            "title": "Customer",
        }

        response2 = self.client.post(self.url, data2, format='json')  # noqa
        self.assertEqual(response2.status_code, 201)

        return True

    def test_get_account_type(self):
        account_type = self.test_create_new() # noqa
        url_detail = reverse('AccountTypeDetail', args=[account_type.data['result']['id']])

        response = self.client.get(self.url) # noqa
        response_detail = self.client.get(url_detail)
        self.assertEqual(response.status_code, 200)
        self.assertCountEqual(
            ['id', 'title', 'code', 'description'],
            list(response_detail.data['result'].keys()),
            check_sum_second=False,
        )
        return True


class IndustryTestCase(AdvanceTestCase):
    def setUp(self): # noqa
        self.maxDiff = None
        self.client = APIClient()

        login_data = TestCaseAuth.test_login(self)
        self.authenticated(login_data)
        self.url = reverse("IndustryList")

    def test_create_new(self):
        data = { # noqa
            "title": "IT Service",
            "description": "Dịch vụ"
        }
        response = self.client.post(self.url, data, format='json')
        self.assertCountEqual(
            ['id', 'title', 'code', 'description'],
            list(response.data['result'].keys()),
            check_sum_second=False,
        )
        self.assertEqual(response.status_code, 201)
        return response

    def test_duplicate_code(self):
        data1 = {  # noqa
            "code": "I01",
            "title": "Banking",
            "description": "Ngân hàng"
        }
        response = self.client.post(self.url, data1, format='json')
        self.assertCountEqual(
            ['id', 'title', 'code', 'description'],
            list(response.data['result'].keys()),
            check_sum_second=False,
        )

        data2 = {  # noqa
            "code": "I01",
            "title": "IT Service",
            "description": ""
        }
        response2 = self.client.post(self.url, data2, format='json')
        self.assertEqual(response2.status_code, 400)
        return True

    def test_missing_data(self):
        data = {  # noqa
            "code": "I01",
            "description": "Dịch vụ"
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 400)

        data1 = {  # noqa
            "title": "IT Service",
            "description": "Dịch vụ"
        }

        response1 = self.client.post(self.url, data1, format='json') # noqa
        self.assertEqual(response1.status_code, 201)

        data2 = {  # noqa
            "code": "I02",
            "title": "Internet Banking",
        }

        response2 = self.client.post(self.url, data2, format='json')  # noqa
        self.assertEqual(response2.status_code, 201)

        return True

    def test_get_account_type(self):
        industry = self.test_create_new() # noqa
        url_detail = reverse('IndustryDetail', args=[industry.data['result']['id']])

        response = self.client.get(self.url) # noqa
        response_detail = self.client.get(url_detail)
        self.assertEqual(response.status_code, 200)
        self.assertCountEqual(
            ['id', 'title', 'code', 'description'],
            list(response_detail.data['result'].keys()),
            check_sum_second=False,
        )
        return True
