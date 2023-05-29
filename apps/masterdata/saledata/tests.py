from django.urls import reverse
from rest_framework import status

from apps.masterdata.saledata.models.config import PaymentTerm
from apps.shared import AdvanceTestCase
from rest_framework.test import APIClient


class AccountTestCase(AdvanceTestCase):
    def setUp(self):
        self.maxDiff = None
        self.client = APIClient()

        self.authenticated()
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
                'code': 'AT05',
                'title': 'Service',
            },
            format='json'
        )

        self.industry = response_industry.data['result']
        self.account_type = response_account_type.data['result']

    def test_create_new_account(self):
        data = {  # noqa
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
            'account_type_selection': 0
        }
        url = reverse('AccountList')
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
            ['id', 'name', 'website', 'code', 'account_type', 'manager', 'owner', 'phone', 'shipping_address',
             'billing_address', 'parent_account', 'account_group', 'tax_code', 'industry', 'total_employees',
             'email', 'payment_term_mapped', 'credit_limit', 'currency', 'contact_mapped', 'account_type_selection',
             'bank_accounts_information', 'credit_cards_information', 'annual_revenue', 'price_list_mapped'],
            check_sum_second=True,
        )
        return response

    def test_create_account_duplicate_code(self):
        self.test_create_new_account()
        data = {  # noqa
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
            
        }
        url = reverse('AccountList')
        response = self.client.post(url, data, format='json')
        self.assertResponseList(
            response,
            status_code=status.HTTP_400_BAD_REQUEST,
            key_required=['errors', 'status'],
            all_key=['errors', 'status'],
            all_key_from=response.data,
            type_match={'errors': dict, 'status': int},
        )
        self.assertCountEqual(
            response.data['errors'],
            ['code'],
            check_sum_second=True,
        )
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
            
        }
        url = reverse('AccountList')
        response = self.client.post(url, data, format='json')
        self.assertResponseList(
            response,
            status_code=status.HTTP_400_BAD_REQUEST,
            key_required=['errors', 'status'],
            all_key=['errors', 'status'],
            all_key_from=response.data,
            type_match={'errors': dict, 'status': int},
        )
        self.assertCountEqual(
            response.data['errors'],
            ['code', 'name'],
            check_sum_second=True,
        )
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
            
        }
        url = reverse('AccountList')
        response = self.client.post(url, data, format='json')
        self.assertResponseList(
            response,
            status_code=status.HTTP_400_BAD_REQUEST,
            key_required=['errors', 'status'],
            all_key=['errors', 'status'],
            all_key_from=response.data,
            type_match={'errors': dict, 'status': int},
        )
        self.assertCountEqual(
            response.data['errors'],
            ['industry'],
            check_sum_second=True,
        )
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


class ProductTestCase(AdvanceTestCase):
    url = reverse("ProductList")

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
        return response.data['result']

    def test_get_product_type(self, product_type_id=None):
        if not product_type_id:
            # change to .data['result']['id'] after change data returned create_product_type
            product_type_id = self.create_product_type()['id']
        url = reverse('ProductTypeDetail', kwargs={'pk': product_type_id})
        response = self.client.get(url, format='json')
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
            ['id', 'title', 'description', 'is_default']
        )
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

    def test_create_product(self):
        product_type = self.create_product_type()  # noqa
        product_category = self.create_product_category()
        unit_of_measure, uom_group = self.create_uom()
        data = {
            "code": "P01",
            "title": "Laptop HP HLVVL6R",
            "general_information": {
                'product_type': product_type['id'],
                'product_category': product_category['id'],
                'uom_group': uom_group['id']
            },
        }
        response = self.client.post(
            self.url,
            data,
            format='json'
        )
        self.assertEqual(response.status_code, 201)
        return response

    def test_create_product_missing_code(self):
        product_type = self.create_product_type()  # noqa
        product_category = self.create_product_category()
        unit_of_measure, uom_group = self.create_uom()
        data1 = {
            "title": "Laptop HP HLVVL6R",
            "general_information": {
                'product_type': product_type['id'],
                'product_category': product_category['id'],
                'uom_group': uom_group['id']
            },
        }
        response1 = self.client.post(
            self.url,
            data1,
            format='json'
        )
        self.assertEqual(response1.status_code, 400)

        return None

    def test_create_product_missing_title(self):
        data = {
            "code": "P01",
            "general_information": {
            }
        }
        response = self.client.post(
            self.url,
            data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_product_duplicate_code(self):
        product_type = self.create_product_type()  # noqa
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
        }
        response1 = self.client.post(
            self.url,
            data1,
            format='json'
        )
        self.assertEqual(response1.status_code, 201)

        data1 = {
            "code": "P01",
            "title": "Laptop HP HLVVL6R",
            "general_information": {
                'product_type': product_type['id'],
                'product_category': product_category['id'],
                'uom_group': uom_group['id']
            },
        }
        response1 = self.client.post(
            self.url,
            data1,
            format='json'
        )
        self.assertEqual(response1.status_code, 400)
        return None

    def test_create_product_not_UUID(self):
        product_type = self.create_product_type()
        product_category = self.create_product_category()
        unit_of_measure, uom_group = self.create_uom()
        data = {
            "code": "P01",
            "title": "Laptop Dell HLVVL6R",
            "general_information": {
                'product_type': {
                    'id': product_type['id'],
                    'title': product_type['title'],
                    'code': "",
                },
                'product_category': {
                    'id': product_category['id'],
                    'title': product_category['title'],
                    'code': "",
                },
                'uom_group': {
                    'id': uom_group['id'],
                    'title': uom_group['title'],
                    'code': "",
                },
            },
            "sale_information": {
                'default_uom_id': unit_of_measure['id']
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
        self.assertEqual(response.status_code, 400)

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
            "purchase_information": {},
        }
        response1 = self.client.post(
            self.url,
            data1,
            format='json'
        )
        self.assertEqual(response1.status_code, 400)
        return None


class SalutationTestCase(AdvanceTestCase):
    def setUp(self):
        self.maxDiff = None
        self.client = APIClient()

        self.authenticated()

    def test_create_new(self):
        data = {  # noqa
            "code": "S01",
            "title": "Mr",
            "description": "A man"
        }
        url = reverse('SalutationList')
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
            ['id', 'title', 'code', 'description'],
            check_sum_second=True,
        )
        return response

    def test_duplicate_code(self):
        self.test_create_new()

        data2 = {  # noqa
            "code": "S01",
            "title": "Miss",
            "description": "A Human"
        }
        url = reverse('SalutationList')
        response = self.client.post(url, data2, format='json')
        self.assertResponseList(
            response,
            status_code=status.HTTP_400_BAD_REQUEST,
            key_required=['errors', 'status'],
            all_key=['errors', 'status'],
            all_key_from=response.data,
            type_match={'errors': dict, 'status': int},
        )
        self.assertCountEqual(
            response.data['errors'],
            ['code'],
            check_sum_second=True,
        )
        return None

    def test_missing_data(self):
        data = {  # noqa
            "code": "S01",
            "description": "A Human"
        }
        url = reverse('SalutationList')
        response = self.client.post(url, data, format='json')
        self.assertResponseList(
            response,
            status_code=status.HTTP_400_BAD_REQUEST,
            key_required=['errors', 'status'],
            all_key=['errors', 'status'],
            all_key_from=response.data,
            type_match={'errors': dict, 'status': int},
        )
        self.assertCountEqual(
            response.data['errors'],
            ['title'],
            check_sum_second=True,
        )

        data1 = {  # noqa
            "code": "S01",
            "title": "Mr"
        }
        url = reverse('SalutationList')
        response1 = self.client.post(url, data1, format='json')
        self.assertResponseList(
            response1,
            status_code=status.HTTP_201_CREATED,
            key_required=['result', 'status'],
            all_key=['result', 'status'],
            all_key_from=response1.data,
            type_match={'result': dict, 'status': int},
        )
        self.assertCountEqual(
            response1.data['result'],
            ['id', 'code', 'title', 'description'],
            check_sum_second=True,
        )

        data2 = {  # noqa
            "title": "Miss",
            "description": "A Human"
        }
        url = reverse('SalutationList')
        response2 = self.client.post(url, data2, format='json')
        self.assertResponseList(
            response2,
            status_code=status.HTTP_201_CREATED,
            key_required=['result', 'status'],
            all_key=['result', 'status'],
            all_key_from=response2.data,
            type_match={'result': dict, 'status': int},
        )
        self.assertCountEqual(
            response2.data['result'],
            ['id', 'code', 'title', 'description'],
            check_sum_second=True,
        )
        return None

    def test_get_list(self):
        self.test_create_new()
        url = reverse("SalutationList")
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
            ['id', 'code', 'title', 'description'],
            check_sum_second=True,
        )
        return response

    def test_get_detail(self, data_id=None):
        data_created = None
        if not data_id:
            data_created = self.test_create_new()
            data_id = data_created.data['result']['id']
        url = reverse("SalutationDetail", kwargs={'pk': data_id})
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
            ['id', 'title', 'code', 'description'],
            check_sum_second=True,
        )
        if not data_id:
            self.assertEqual(response.data['result']['id'], data_created.data['result']['id'])
            self.assertEqual(response.data['result']['title'], data_created.data['result']['title'])
        else:
            self.assertEqual(response.data['result']['id'], data_id)
        return response

    def test_update_salutation(self):
        data_created = self.test_create_new()
        description_change = 'A Women'
        title_change = 'Mrs'
        url = reverse("SalutationDetail", kwargs={'pk': data_created.data['result']['id']})
        data = {  # noqa
            "code": "S01",
            "title": title_change,
            "description": description_change

        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data_changed = self.test_get_detail(data_id=data_created.data['result']['id'])
        self.assertEqual(data_changed.data['result']['title'], title_change)
        self.assertEqual(data_changed.data['result']['description'], description_change)

        return response


class UoMTestCase(AdvanceTestCase):
    def setUp(self):
        self.maxDiff = None
        self.client = APIClient()

        self.authenticated()

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
        self.assertResponseList(  # noqa
            response,
            status_code=status.HTTP_201_CREATED,
            key_required=['result', 'status'],
            all_key=['result', 'status'],
            all_key_from=response.data,
            type_match={'result': dict, 'status': int},
        )
        self.assertCountEqual(
            response.data['result'],
            ['id', 'title', 'uom'],
            check_sum_second=True,
        )
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
        self.assertResponseList(  # noqa
            response,
            status_code=status.HTTP_201_CREATED,
            key_required=['result', 'status'],
            all_key=['result', 'status'],
            all_key_from=response.data,
            type_match={'result': dict, 'status': int},
        )
        self.assertCountEqual(
            response.data['result'],
            ['id', 'code', 'title', 'group', 'ratio', 'rounding'],
            check_sum_second=True,
        )
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
        self.assertResponseList(  # noqa
            response,
            status_code=status.HTTP_201_CREATED,
            key_required=['result', 'status'],
            all_key=['result', 'status'],
            all_key_from=response.data,
            type_match={'result': dict, 'status': int},
        )
        self.assertCountEqual(
            response.data['result'],
            ['id', 'code', 'title', 'group', 'ratio', 'rounding'],
            check_sum_second=True,
        )
        data1 = {
            "code": "U02",
            "title": "Dozen",
            "group": uom_group.data['result']['id'],
            "ratio": 1,
            "rounding": 5,
            "is_referenced_unit": True
        }
        response1 = self.client.post(url, data1, format='json')
        self.assertResponseList(  # noqa
            response1,
            status_code=status.HTTP_400_BAD_REQUEST,
            key_required=['errors', 'status'],
            all_key=['errors', 'status'],
            all_key_from=response1.data,
            type_match={'errors': dict, 'status': int},
        )
        self.assertCountEqual(
            response1.data['errors'],
            ['non_field_errors'],
            check_sum_second=True,
        )

        return response

    def test_create_uom(self):
        uom_group = self.test_create_new_uom_group()
        data = {
            "code": "UOP001",
            "title": "Unit",
            "group": uom_group.data['result']['id'],
            "ratio": 1,
            "rounding": 5,
            "is_referenced_unit": True
        }
        url = reverse('UnitOfMeasureList')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
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
        self.assertResponseList(  # noqa
            response,
            status_code=status.HTTP_400_BAD_REQUEST,
            key_required=['errors', 'status'],
            all_key=['errors', 'status'],
            all_key_from=response.data,
            type_match={'errors': dict, 'status': int},
        )
        self.assertCountEqual(
            response.data['errors'],
            ['code'],
            check_sum_second=True,
        )

        data1 = {
            "code": "U01",
            "title": "",
            "group": uom_group.data['result']['id'],
            "ratio": 1,
            "rounding": 5,
            "is_referenced_unit": False
        }
        response1 = self.client.post(url, data1, format='json')
        self.assertResponseList(  # noqa
            response1,
            status_code=status.HTTP_400_BAD_REQUEST,
            key_required=['errors', 'status'],
            all_key=['errors', 'status'],
            all_key_from=response1.data,
            type_match={'errors': dict, 'status': int},
        )
        self.assertCountEqual(
            response1.data['errors'],
            ['title'],
            check_sum_second=True,
        )

        data2 = {
            "code": "U01",
            "title": "Unit",
            "group": "",
            "ratio": 1,
            "rounding": 5,
            "is_referenced_unit": False
        }
        response2 = self.client.post(url, data2, format='json')
        self.assertResponseList(  # noqa
            response2,
            status_code=status.HTTP_400_BAD_REQUEST,
            key_required=['errors', 'status'],
            all_key=['errors', 'status'],
            all_key_from=response2.data,
            type_match={'errors': dict, 'status': int},
        )
        self.assertCountEqual(
            response2.data['errors'],
            ['group'],
            check_sum_second=True,
        )
        return response

    def test_get_list(self):
        self.test_create_new_uom()
        url = reverse("UnitOfMeasureList")
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
            ['id', 'code', 'title', 'group'],
            check_sum_second=True,
        )
        return response

    def test_get_detail(self, data_id=None):
        data_created = None
        if not data_id:
            data_created = self.test_create_new_uom()
            data_id = data_created.data['result']['id']
        url = reverse("UnitOfMeasureDetail", kwargs={'pk': data_id})
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
            ['id', 'code', 'title', 'group', 'ratio', 'rounding'],
            check_sum_second=True,
        )
        if not data_id:
            self.assertEqual(response.data['result']['id'], data_created.data['result']['id'])
            self.assertEqual(response.data['result']['title'], data_created.data['result']['title'])
        else:
            self.assertEqual(response.data['result']['id'], data_id)
        return response

    def test_uom_update(self):
        data_created = self.test_create_new_uom()
        url = reverse("UnitOfMeasureDetail", kwargs={'pk': data_created.data['result']['id']})
        title_change = 'Dozen'
        data = {
            "code": "U01",
            "title": title_change,
            "group": data_created.data['result']['group']['id'],
            "ratio": 1,
            "rounding": 5,
            "is_referenced_unit": True
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data_changed = self.test_get_detail(data_id=data_created.data['result']['id'])
        self.assertEqual(data_changed.data['result']['title'], title_change)
        return response


class CurrencyTestCase(AdvanceTestCase):
    def setUp(self):
        self.maxDiff = None
        self.client = APIClient()

        self.authenticated()
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
        return None

    def test_create_new_currency(self):
        data = {
            "abbreviation": "CAD",
            "title": "CANADIAN DOLLAR",
            "rate": 0.45
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 201)
        return response

    def test_create_new_currency_exists(self):
        data = {
            "abbreviation": "VND",
            "title": "VIETNAM DONG",
            "rate": 1
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 400)
        return None

    def test_create_new_currency_rate_less_than_zero(self):
        data = {
            "abbreviation": "VND",
            "title": "VIETNAM DONG",
            "rate": -1
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 400)
        return None


class TaxAndTaxCategoryTestCase(AdvanceTestCase):
    url_tax_category = reverse("TaxCategoryList")
    url_tax = reverse("TaxList")

    def setUp(self):
        self.maxDiff = None
        self.client = APIClient()
        self.authenticated()

    def test_create_new_tax_category(self):
        data = {
            "title": "Thuế doanh nghiệp kinh doanh tư nhân",
            "description": "Áp dụng cho các hộ gia đình kinh doanh tư nhân",
        }
        response = self.client.post(self.url_tax_category, data, format='json')
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
        self.assertResponseList(
            response,
            status_code=status.HTTP_400_BAD_REQUEST,
            key_required=['errors', 'status'],
            all_key=['errors', 'status'],
            all_key_from=response.data,
            type_match={'errors': dict, 'status': int},
        )
        self.assertCountEqual(
            response.data['errors'],
            ['title'],
            check_sum_second=True,
        )

        # missing code
        data1 = {
            "title": "Thuế bán hàng tư nhân",
            "rate": 10,
            "category": tax_category.data['result']['id'],
            "type": 0
        }
        response1 = self.client.post(self.url_tax, data1, format='json')
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
            ['code'],
            check_sum_second=True,
        )

        # missing category
        data2 = {
            "title": "Thuế bán hàng tư nhân VAT-5%",
            "code": 'VAT-5',
            "rate": 10,
            "type": 0
        }
        response2 = self.client.post(self.url_tax, data2, format='json')
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
            ['category'],
            check_sum_second=True,
        )

        # missing type
        data3 = {
            "title": "Thuế bán hàng tư nhân VAT-15%",
            "code": 'VAT-15',
            "category": tax_category.data['result']['id'],
            "rate": 10,
        }
        response3 = self.client.post(self.url_tax, data3, format='json')
        self.assertResponseList(
            response3,
            status_code=status.HTTP_400_BAD_REQUEST,
            key_required=['errors', 'status'],
            all_key=['errors', 'status'],
            all_key_from=response3.data,
            type_match={'errors': dict, 'status': int},
        )
        self.assertCountEqual(
            response3.data['errors'],
            ['type'],
            check_sum_second=True,
        )
        return None

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
        self.assertResponseList(
            response,
            status_code=status.HTTP_400_BAD_REQUEST,
            key_required=['errors', 'status'],
            all_key=['errors', 'status'],
            all_key_from=response.data,
            type_match={'errors': dict, 'status': int},
        )
        self.assertCountEqual(
            response.data['errors'],
            ['title'],
            check_sum_second=True,
        )

        # code
        data1 = {
            "code": "",
            "title": "Thuế bán hàng tư nhân",
            "rate": 10,
            "category": tax_category.data['result']['id'],
            "type": 0
        }
        response1 = self.client.post(self.url_tax, data1, format='json')
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
            ['code'],
            check_sum_second=True,
        )

        # category
        data2 = {
            "code": "VAT-5",
            "title": "Thuế bán hàng tư nhân VAT-5%",
            "rate": 10,
            "category": "",
            "type": 0
        }
        response2 = self.client.post(self.url_tax, data2, format='json')
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
            ['category'],
            check_sum_second=True,
        )

        return None

    def test_get_list(self):
        self.test_create_new_tax()
        url = reverse("TaxList")
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
            ['id', 'code', 'title', 'rate', 'category', 'type'],
            check_sum_second=True,
        )
        return response

    def test_get_detail(self, data_id=None):
        data_created = None
        if not data_id:
            data_created = self.test_create_new_tax()
            data_id = data_created.data['result']['id']
        url = reverse("TaxDetail", kwargs={'pk': data_id})
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
            ['id', 'code', 'title', 'rate', 'category', 'type'],
            check_sum_second=True,
        )
        if not data_id:
            self.assertEqual(response.data['result']['id'], data_created.data['result']['id'])
            self.assertEqual(response.data['result']['title'], data_created.data['result']['title'])
        else:
            self.assertEqual(response.data['result']['id'], data_id)
        return response

    def test_update_tax(self):
        data_created = self.test_create_new_tax()
        rate_change = 5
        title_change = 'Thuế bán hàng'
        url = reverse("TaxDetail", kwargs={'pk': data_created.data['result']['id']})
        data = {
            "title": title_change,
            "code": 'VAT-10',
            "rate": rate_change,
            "category": data_created.data['result']['category'],
            "type": 0
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data_changed = self.test_get_detail(data_id=data_created.data['result']['id'])
        self.assertEqual(data_changed.data['result']['title'], title_change)
        self.assertEqual(data_changed.data['result']['rate'], rate_change)

        return response


class ProductTypeAndProductCategoryTestCase(AdvanceTestCase):
    def setUp(self):
        self.maxDiff = None
        self.client = APIClient()

        login_data = self._login()
        self.authenticated(login_data)
        self.url_product_category = reverse("ProductCategoryList")
        self.url_product_type = reverse("ProductTypeList")

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
        return None

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
        return None

    def test_get_list_and_detail_product_category(self):
        product_category = self.test_create_new_product_category()
        response = self.client.get(self.url_product_category, format='json')  # noqa
        self.assertResponseList(  # noqa
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
        response = self.client.get(self.url_product_type, format='json')  # noqa
        self.assertResponseList(  # noqa
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
        self.assertCountEqual(
            ['id', 'title', 'description'],
            list(response_detail.data['result'].keys()),
            check_sum_second=False,
        )
        return None


class InterestTestCase(AdvanceTestCase):
    def setUp(self):
        self.maxDiff = None
        self.client = APIClient()

        self.authenticated()
        self.url = reverse("InterestsList")

    def test_create_new(self):
        data = {  # noqa
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
        return response

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
        return None

    def test_get_interest(self):
        interest = self.test_create_new()  # noqa
        url_detail = reverse('InterestDetail', args=[interest.data['result']['id']])

        response = self.client.get(self.url)  # noqa
        response_detail = self.client.get(url_detail)
        self.assertEqual(response.status_code, 200)
        self.assertCountEqual(
            ['id', 'title', 'code', 'description'],
            list(response_detail.data['result'].keys()),
            check_sum_second=False,
        )
        return response


class AccountTypeTestCase(AdvanceTestCase):
    def setUp(self):  # noqa
        self.maxDiff = None
        self.client = APIClient()

        self.authenticated()
        self.url = reverse("AccountTypeList")

    def test_create_new(self):
        data = {  # noqa
            "title": "Customer_01",
            "description": "Cho phép người dùng tự điều chỉnh"
        }
        response = self.client.post(self.url, data, format='json')
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
            ['id', 'code', 'title', 'is_default', 'description'],
            check_sum_second=True,
        )
        return response

    def test_duplicate_code(self):
        data1 = {  # noqa
            "code": "AT08",
            "title": "Customer_02",
            "description": "Cho phép người dùng tự điều chỉnh"
        }
        response = self.client.post(self.url, data1, format='json')
        self.assertCountEqual(
            response.data['result'],
            ['id', 'code', 'title', 'is_default', 'description'],
            check_sum_second=True,
        )

        data2 = {  # noqa
            "code": "AT08",
            "title": "Supplier_01",
            "description": ""
        }
        response2 = self.client.post(self.url, data2, format='json')
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
            ['code'],
            check_sum_second=True,
        )
        return None

    def test_missing_data(self):
        data = {  # noqa
            "code": "AT09",
            "description": "Customer_01"
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertResponseList(
            response,
            status_code=status.HTTP_400_BAD_REQUEST,
            key_required=['errors', 'status'],
            all_key=['errors', 'status'],
            all_key_from=response.data,
            type_match={'errors': dict, 'status': int},
        )
        self.assertCountEqual(
            response.data['errors'],
            ['title'],
            check_sum_second=True,
        )

        data1 = {  # noqa
            "title": "Supplier_01",
            "description": "Supplier"
        }

        response1 = self.client.post(self.url, data1, format='json')  # noqa
        self.assertResponseList(
            response1,
            status_code=status.HTTP_201_CREATED,
            key_required=['result', 'status'],
            all_key=['result', 'status'],
            all_key_from=response1.data,
            type_match={'result': dict, 'status': int},
        )
        self.assertCountEqual(
            response1.data['result'],
            ['id', 'code', 'title', 'is_default', 'description'],
            check_sum_second=True,
        )

        data2 = {  # noqa
            "code": "AT09",
            "title": "Customer_01",
        }

        response2 = self.client.post(self.url, data2, format='json')  # noqa
        self.assertResponseList(
            response2,
            status_code=status.HTTP_201_CREATED,
            key_required=['result', 'status'],
            all_key=['result', 'status'],
            all_key_from=response2.data,
            type_match={'result': dict, 'status': int},
        )
        self.assertCountEqual(
            response2.data['result'],
            ['id', 'code', 'title', 'is_default', 'description'],
            check_sum_second=True,
        )
        return None

    def test_get_account_type(self):
        account_type = self.test_create_new()  # noqa
        response = self.client.get(self.url)
        self.assertResponseList(  # noqa
            response,
            status_code=status.HTTP_200_OK,
            key_required=['result', 'status', 'next', 'previous', 'count', 'page_size'],
            all_key=['result', 'status', 'next', 'previous', 'count', 'page_size'],
            all_key_from=response.data,
            type_match={'result': list, 'status': int, 'next': int, 'previous': int, 'count': int, 'page_size': int},
        )
        self.assertEqual(
            len(response.data['result']), 5
        )
        self.assertCountEqual(
            response.data['result'][0],
            ['id', 'title', 'code', 'is_default', 'description'],
            check_sum_second=True,
        )
        return response

    def test_get_detail(self, data_id=None):
        data_created = None
        if not data_id:
            data_created = self.test_create_new()
            data_id = data_created.data['result']['id']
        url = reverse("AccountTypeDetail", kwargs={'pk': data_id})
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
            ['id', 'title', 'code', 'description', 'is_default'],
            check_sum_second=True,
        )
        if not data_id:
            self.assertEqual(response.data['result']['id'], data_created.data['result']['id'])
            self.assertEqual(response.data['result']['title'], data_created.data['result']['title'])
        else:
            self.assertEqual(response.data['result']['id'], data_id)
        return response


class IndustryTestCase(AdvanceTestCase):
    def setUp(self):  # noqa
        self.maxDiff = None
        self.client = APIClient()

        self.authenticated()
        self.url = reverse("IndustryList")

    def test_create_new(self):
        data = {  # noqa
            "code": "I01",
            "title": "IT Service",
            "description": "Dịch vụ"
        }
        response = self.client.post(self.url, data, format='json')
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
            ['id', 'title', 'code', 'description'],
            check_sum_second=True,
        )
        return response

    def test_duplicate_code(self):
        self.test_create_new()
        data = {  # noqa
            "code": "I01",
            "title": "IT Service1",
            "description": ""
        }
        response = self.client.post(self.url, data, format='json')
        self.assertResponseList(
            response,
            status_code=status.HTTP_400_BAD_REQUEST,
            key_required=['errors', 'status'],
            all_key=['errors', 'status'],
            all_key_from=response.data,
            type_match={'errors': dict, 'status': int},
        )
        self.assertCountEqual(
            response.data['errors'],
            ['code'],
            check_sum_second=True,
        )
        return response

    def test_missing_data(self):
        data = {  # noqa
            "code": "I01",
            "description": "Dịch vụ"
        }
        response = self.client.post(self.url, data, format='json')
        self.assertResponseList(
            response,
            status_code=status.HTTP_400_BAD_REQUEST,
            key_required=['errors', 'status'],
            all_key=['errors', 'status'],
            all_key_from=response.data,
            type_match={'errors': dict, 'status': int},
        )
        self.assertCountEqual(
            response.data['errors'],
            ['title'],
            check_sum_second=True,
        )

        data1 = {  # noqa
            "title": "IT Service",
            "description": "Dịch vụ"
        }

        response1 = self.client.post(self.url, data1, format='json')  # noqa
        self.assertResponseList(
            response1,
            status_code=status.HTTP_201_CREATED,
            key_required=['result', 'status'],
            all_key=['result', 'status'],
            all_key_from=response1.data,
            type_match={'result': dict, 'status': int},
        )
        self.assertCountEqual(
            response1.data['result'],
            ['id', 'code', 'title', 'description'],
            check_sum_second=True,
        )

        data2 = {  # noqa
            "code": "I02",
            "title": "Internet Banking",
        }

        response2 = self.client.post(self.url, data2, format='json')  # noqa
        self.assertResponseList(
            response2,
            status_code=status.HTTP_201_CREATED,
            key_required=['result', 'status'],
            all_key=['result', 'status'],
            all_key_from=response2.data,
            type_match={'result': dict, 'status': int},
        )
        self.assertCountEqual(
            response2.data['result'],
            ['id', 'code', 'title', 'description'],
            check_sum_second=True,
        )

        return None

    def test_get_list(self):
        industry = self.test_create_new()  # noqa
        response = self.client.get(self.url)  # noqa
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
            ['id', 'title', 'code', 'description'],
            check_sum_second=True,
        )
        return response

    def test_get_detail(self, data_id=None):
        data_created = None
        if not data_id:
            data_created = self.test_create_new()
            data_id = data_created.data['result']['id']
        url = reverse("IndustryDetail", kwargs={'pk': data_id})
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
            ['id', 'title', 'code', 'description'],
            check_sum_second=True,
        )
        if not data_id:
            self.assertEqual(response.data['result']['id'], data_created.data['result']['id'])
            self.assertEqual(response.data['result']['title'], data_created.data['result']['title'])
        else:
            self.assertEqual(response.data['result']['id'], data_id)
        return response

    def test_update(self):
        title_change = 'Industry Name updated'
        data_created = self.test_create_new()
        url = reverse("IndustryDetail", kwargs={'pk': data_created.data['result']['id']})
        data = {
            "code": "I01",
            "title": title_change,
            "description": "Dịch vụ"
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data_changed = self.test_get_detail(data_id=data_created.data['result']['id'])
        self.assertEqual(data_changed.data['result']['title'], title_change)
        return response


class ConfigPaymentTermTestCase(AdvanceTestCase):
    def setUp(self):
        self.maxDiff = None
        self.client = APIClient()

        self.authenticated()

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
        self.assertResponseList(  # noqa
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


class ExpenseTestCase(AdvanceTestCase):
    def setUp(self):
        self.maxDiff = None
        self.client = APIClient()

        self.authenticated()

    @staticmethod
    def get_currency(self):
        url = reverse("CurrencyList")
        response = self.client.get(url, format='json')
        return response.data['result']

    @staticmethod
    def create_expense_type(self):
        data = {
            'title': 'chi phí nhân công',
            'description': ''
        }
        url = reverse("ExpenseTypeList")
        response = self.client.post(url, data, format='json')
        return response.data['result']

    @staticmethod
    def create_uom_group(self):
        url = reverse('UnitOfMeasureGroupList')
        response = self.client.post(
            url,
            {
                'title': 'nhân công',
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        return response.data['result']

    @staticmethod
    def create_uom(self, uom_group):
        url = reverse('UnitOfMeasureList')
        response = self.client.post(
            url,
            {
                "code": "MD",
                "title": "manday",
                "group": uom_group['id'],
                "ratio": 1,
                "rounding": 5,
                "is_referenced_unit": True
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        return response.data['result']

    def create_tax_code(self):
        pass

    @staticmethod
    def create_price_list(self, currency):
        data = {
            "title": "chi phí nhân công sản xuất",
            "auto_update": True,
            "can_delete": True,
            "factor": 1,
            "currency": [currency[0], currency[1]],
            "price_list_type": 2,
            "valid_time_start": "2023-05-01 17:13:00",
            "valid_time_end": "2023-05-06 17:13:00"
        }
        url = reverse("PriceList")
        response = self.client.post(url, data, format='json')
        return response.data['result']

    def test_create_new_expense(self):
        currency = self.get_currency(self)  # noqa
        expense_type = self.create_expense_type(self)
        uom_group = self.create_uom_group(self)
        uom = self.create_uom(self, uom_group)
        price_list = self.create_price_list(self, currency)
        data = {  # noqa
            "code": "E01",
            "title": "Chi phí nhân công sản xuất",
            "general_information": {
                "expense_type": expense_type['id'],
                "uom_group": uom_group['id'],
                "uom": uom['id'],
                "tax_code": None,
                "price_list": [
                    {
                        'id': price_list['id'],
                        'value': 0,
                        'is_auto_update': False,
                    }
                ],
                "currency_using": currency[0]['id']
            }
        }
        url = reverse("ExpenseList")
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
            ['id', 'general_information', 'title', 'code', 'date_created', 'date_modified', 'is_active', 'is_delete',
             'employee_created', 'employee_modified', 'tenant', 'company'],
            check_sum_second=True,
        )
        return response, price_list

    def test_create_expense_missing_data(self):
        currency = self.get_currency(self)  # noqa
        expense_type = self.create_expense_type(self)
        uom_group = self.create_uom_group(self)
        uom = self.create_uom(self, uom_group)
        price_list = self.create_price_list(self, currency)
        data = {
            "code": "E01",
            "general_information": {
                "expense_type": expense_type['id'],
                "uom_group": uom_group['id'],
                "uom": uom['id'],
                "tax_code": None,
                "price_list": [
                    {
                        'id': price_list['id'],
                        'value': 0,
                        'is_auto_update': False,
                    }
                ],
                "currency_using": currency[0]['id']
            }
        }
        url = reverse("ExpenseList")

        response = self.client.post(url, data, format='json')
        self.assertResponseList(
            response,
            status_code=status.HTTP_400_BAD_REQUEST,
            key_required=['errors', 'status'],
            all_key=['errors', 'status'],
            all_key_from=response.data,
            type_match={'errors': dict, 'status': int},
        )
        self.assertCountEqual(
            response.data['errors'],
            ['title'],
            check_sum_second=True,
        )
        data1 = {  # noqa
            "title": "Chi phis nhân công sản xuất",
            "general_information": {
                "expense_type": expense_type['id'],
                "uom_group": uom_group['id'],
                "uom": uom['id'],
                "tax_code": None,
                "price_list": [
                    {
                        'id': price_list['id'],
                        'value': 0,
                        'is_auto_update': False,
                    }
                ],
                "currency_using": currency[0]['id']
            }
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
            ['code'],
            check_sum_second=True,
        )

        data2 = {  # noqa
            "code": "E01",
            "title": "Chi phí nhân công sản xuất",
            "general_information": {
                "uom_group": uom_group['id'],
                "uom": uom['id'],
                "tax_code": None,
                "price_list": [
                    {
                        'id': price_list['id'],
                        'value': 0,
                        'is_auto_update': False,
                    }
                ],
                "currency_using": currency[0]['id']
            }
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
            ['expense_type'],
            check_sum_second=True,
        )
        return response

    def test_create_expense_empty_data(self):
        currency = self.get_currency(self)  # noqa
        expense_type = self.create_expense_type(self)
        uom_group = self.create_uom_group(self)
        uom = self.create_uom(self, uom_group)
        price_list = self.create_price_list(self, currency)
        url = reverse("ExpenseList")
        data = {
            "code": "E01",
            "title": "",
            "general_information": {
                "expense_type": expense_type['id'],
                "uom_group": uom_group['id'],
                "uom": uom['id'],
                "tax_code": None,
                "price_list": [
                    {
                        'id': price_list['id'],
                        'value': 0,
                        'is_auto_update': False,
                    }
                ],
                "currency_using": currency[0]['id']
            }
        }

        response = self.client.post(url, data, format='json')
        self.assertResponseList(
            response,
            status_code=status.HTTP_400_BAD_REQUEST,
            key_required=['errors', 'status'],
            all_key=['errors', 'status'],
            all_key_from=response.data,
            type_match={'errors': dict, 'status': int},
        )
        self.assertCountEqual(
            response.data['errors'],
            ['title'],
            check_sum_second=True,
        )
        data1 = {  # noqa
            "code": "",
            "title": "Chi phis nhân công sản xuất",
            "general_information": {
                "expense_type": expense_type['id'],
                "uom_group": uom_group['id'],
                "uom": uom['id'],
                "tax_code": None,
                "price_list": [
                    {
                        'id': price_list['id'],
                        'value': 0,
                        'is_auto_update': False,
                    }
                ],
                "currency_using": currency[0]['id']
            }
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
            ['code'],
            check_sum_second=True,
        )

        data2 = {  # noqa
            "code": "E01",
            "title": "Chi phí nhân công sản xuất",
            "general_information": {
                "expense_type": expense_type['id'],
                "uom_group": "",
                "uom": uom['id'],
                "tax_code": None,
                "price_list": [
                    {
                        'id': price_list['id'],
                        'value': 0,
                        'is_auto_update': False,
                    }
                ],
                "currency_using": currency[0]['id']
            }
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
            ['uom_group'],
            check_sum_second=True,
        )

        data3 = {  # noqa
            "code": "E01",
            "title": "Chi phí nhân công sản xuất",
            "general_information": {
                "expense_type": expense_type['id'],
                "uom_group": uom_group['id'],
                "uom": uom['id'],
                "tax_code": None,
                "price_list": [
                    {
                        'value': 0,
                        'is_auto_update': False
                    }
                ],
                "currency_using": currency[0]['id']
            }
        }
        response3 = self.client.post(url, data3, format='json')
        self.assertResponseList(
            response3,
            status_code=status.HTTP_400_BAD_REQUEST,
            key_required=['errors', 'status'],
            all_key=['errors', 'status'],
            all_key_from=response3.data,
            type_match={'errors': dict, 'status': int},
        )
        self.assertCountEqual(
            response3.data['errors'],
            ['price list'],
            check_sum_second=True,
        )
        return response

    def test_update_expense(self):
        currency = self.get_currency(self)  # noqa
        expense_type = self.create_expense_type(self)
        uom_group = self.create_uom_group(self)
        uom = self.create_uom(self, uom_group)
        price_list = self.create_price_list(self, currency)
        data = {  # noqa
            "code": "E01",
            "title": "Chi phí nhân công sản xuất",
            "general_information": {
                "expense_type": expense_type['id'],
                "uom_group": uom_group['id'],
                "uom": uom['id'],
                "tax_code": None,
                "price_list": [
                    {
                        'id': price_list['id'],
                        'value': 0,
                        'is_auto_update': False,
                    }
                ],
                "currency_using": currency[0]['id']
            }
        }
        url = reverse("ExpenseList")
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        url_update = reverse("ExpenseDetail", args=[response.data['result']['id']])

        data_update = {  # noqa
            "code": "E01",
            "title": "Chi phí nhân công vệ sinh",
            "general_information": {
                "expense_type": expense_type['id'],
                "uom_group": uom_group['id'],
                "uom": uom['id'],
                "tax_code": None,
                "price_list": [
                    {
                        'id': price_list['id'],
                        'value': 100000,
                        'is_auto_update': False,
                    }
                ],
                "currency_using": currency[0]['id']
            }
        }
        response_update = self.client.put(url_update, data_update, format='json')
        self.assertEqual(response_update.status_code, status.HTTP_200_OK)
        return response

    def test_get_expense_in_price_list(self):
        _, price_list = self.test_create_new_expense()
        url = reverse("PriceDetail", args=[price_list['id']])
        response_list = self.client.get(url, format='json')
        self.assertEqual(response_list.status_code, status.HTTP_200_OK)
        return response_list

    def test_get_list_and_detail_expense(self):
        expense = self.test_update_expense()
        url_list = reverse("ExpenseList")
        response_list = self.client.get(url_list, format='json')
        self.assertEqual(response_list.status_code, 200)

        url_detail = reverse("ExpenseDetail", args=[expense.data['result']['id']])
        response_detail = self.client.get(url_detail, format='json')
        self.assertEqual(response_detail.status_code, 200)
        return response_detail


class WareHouseTestCase(AdvanceTestCase):
    def setUp(self) -> None:
        self.maxDiff = None
        self.client = APIClient()
        self.authenticated()

    def test_warehouse_create(self):
        url = reverse("WareHouseList")
        data = {
            'title': 'Kho lưu trữ số 1',
            'code': 'WareHouse_1',
            'description': 'Lưu trữ linh kiện bán lẻ ở Tân Bình',
            'is_active': True,
        }
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
            ['id', 'title', 'code', 'remarks', 'is_active'],
            check_sum_second=True,
        )
        return response

    def test_warehouse_list(self):
        self.test_warehouse_create()
        url = reverse("WareHouseList")
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
            ['id', 'title', 'code', 'remarks', 'is_active'],
            check_sum_second=True,
        )
        return response

    def test_warehouse_detail(self, data_id=None):
        data_created = None
        if not data_id:
            data_created = self.test_warehouse_create()
            data_id = data_created.data['result']['id']
        url = reverse("WareHouseDetail", kwargs={'pk': data_id})
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
            ['id', 'title', 'code', 'remarks', 'is_active'],
            check_sum_second=True,
        )
        if not data_id:
            self.assertEqual(response.data['result']['id'], data_created.data['result']['id'])
            self.assertEqual(response.data['result']['title'], data_created.data['result']['title'])
        else:
            self.assertEqual(response.data['result']['id'], data_id)
        return response

    def test_warehouse_update(self):
        title_change = 'Tên nhà kho đã được thay đổi'
        data_created = self.test_warehouse_create()
        url = reverse("WareHouseDetail", kwargs={'pk': data_created.data['result']['id']})
        data = {
            'title': title_change
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data_changed = self.test_warehouse_detail(data_id=data_created.data['result']['id'])
        self.assertEqual(data_changed.data['result']['title'], title_change)
        return response

    def test_warehouse_delete(self):
        data_created = self.test_warehouse_create()
        url = reverse("WareHouseDetail", kwargs={'pk': data_created.data['result']['id']})
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        return response


class ShippingTestCase(AdvanceTestCase):
    def setUp(self):
        self.maxDiff = None
        self.client = APIClient()

        self.authenticated()

    def get_location(self):
        url = reverse("CityList")
        response = self.client.get(url, format='json')
        return response.data['result']

    def get_shipping_unit(self):
        url = reverse("BaseItemUnitList")
        response = self.client.get(url, format='json')
        return response.data['result']

    def test_create_new_shipping(self):
        currency = ExpenseTestCase.get_currency(self)
        unit = self.get_shipping_unit()
        location = self.get_location()
        data = {
            "title": "Chi phí vận chuyển mặc định",
            "margin": 0,
            "currency": currency[0]['id'],
            "cost_method": 0,
            "fixed_price": 30000,
            "formula_condition": [
                {
                    "location": [
                        location[1]['id']
                    ],
                    "formula": [
                        {
                            "unit": unit[0]['id'],
                            "comparison_operators": 1,
                            "threshold": 2,
                            "amount_condition": 5000,
                            "extra_amount": 500
                        }
                    ]
                }
            ]
        }
        url = reverse('ShippingList')
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
            ['id', 'title', 'code', 'margin', 'is_active', 'currency', 'cost_method', 'fixed_price',
             'formula_condition'],
            check_sum_second=True,
        )

        data1 = {  # noqa
            "title": "Chi phí vận chuyển mặc định",
            "margin": 0,
            "currency": currency[0]['id'],
            "cost_method": 1,
            "formula_condition": [
                {
                    "location": [
                        location[1]['id']
                    ],
                    "formula": [
                        {
                            "unit": unit[0]['id'],
                            "comparison_operators": 1,
                            "threshold": 2,
                            "amount_condition": 5000,
                            "extra_amount": 500
                        }
                    ]
                }
            ]
        }
        response1 = self.client.post(url, data1, format='json')
        self.assertResponseList(
            response1,
            status_code=status.HTTP_201_CREATED,
            key_required=['result', 'status'],
            all_key=['result', 'status'],
            all_key_from=response1.data,
            type_match={'result': dict, 'status': int},
        )
        self.assertCountEqual(
            response1.data['result'],
            ['id', 'title', 'code', 'margin', 'is_active', 'currency', 'cost_method', 'fixed_price',
             'formula_condition'],
            check_sum_second=True,
        )
        return response

    def test_create_fail_validate(self):
        currency = ExpenseTestCase.get_currency(self)
        unit = self.get_shipping_unit()
        location = self.get_location()

        # integer or float field less than 0
        data = {  # noqa
            "title": "Chi phí vận chuyển tiêu chuẩn",
            "margin": -5,
            "currency": currency[0]['id'],
            "cost_method": 0,
            "fixed_price": -30000,
            "formula_condition": [
                {
                    "location": [
                        location[1]['id']
                    ],
                    "formula": [
                        {
                            "unit": unit[0]['id'],
                            "comparison_operators": 1,
                            "threshold": -2,
                            "amount_condition": -5000,
                            "extra_amount": -500
                        }
                    ]
                }
            ]
        }
        url = reverse('ShippingList')
        response = self.client.post(url, data, format='json')

        self.assertResponseList(
            response,
            status_code=status.HTTP_400_BAD_REQUEST,
            key_required=['errors', 'status'],
            all_key=['errors', 'status'],
            all_key_from=response.data,
            type_match={'errors': dict, 'status': int},
        )
        self.assertCountEqual(
            response.data['errors'],
            ['margin', 'price_fixed', 'threshold in condition', 'price_fixed in condition',
             'extra_amount in condition'],
            check_sum_second=True,
        )

        # missing data
        data1 = {
            "title": "Chi phí vận chuyển tiêu chuẩn",
            "margin": 5,
            "currency": currency[0]['id'],
            "cost_method": 0,
            "formula_condition": []
        }
        response1 = self.client.post(url, data1, format='json')  # noqa
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
            ['Amount'],
            check_sum_second=True,
        )

        data2 = {
            "title": "Chi phí vận chuyển tiêu chuẩn",
            "margin": 5,
            "currency": currency[0]['id'],
            "cost_method": 1,
            "formula_condition": [
                {
                    "location": [
                        location[1]['id']
                    ],
                    "formula": [
                        {
                            "comparison_operators": 1,
                            "threshold": 2,
                            "amount_condition": 5000,
                            "extra_amount": 500
                        }
                    ]
                }
            ]
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
            ['unit'],
            check_sum_second=True,
        )

        data3 = {  # noqa
            "title": "Chi phí vận chuyển tiêu chuẩn",
            "margin": 5,
            "currency": currency[0]['id'],
            "cost_method": 0,
            "formula_condition": [
                {
                    "formula": [
                        {
                            "unit": unit[0]['id'],
                            "comparison_operators": 1,
                            "threshold": 2,
                            "amount_condition": 5000,
                            "extra_amount": 500
                        }
                    ]
                }
            ]
        }
        response3 = self.client.post(url, data3, format='json')
        self.assertResponseList(
            response3,
            status_code=status.HTTP_400_BAD_REQUEST,
            key_required=['errors', 'status'],
            all_key=['errors', 'status'],
            all_key_from=response3.data,
            type_match={'errors': dict, 'status': int},
        )
        self.assertCountEqual(
            response3.data['errors'],
            ['location'],
            check_sum_second=True,
        )
        return None

    def test_create_not_UUID(self):
        currency = ExpenseTestCase.get_currency(self)  # noqa
        unit = self.get_shipping_unit()
        location = self.get_location()

        data = {  # noqa
            "title": "Chi phí vận chuyển tiêu chuẩn",
            "margin": 5,
            "currency": '1111',
            "cost_method": 0,
            "fixed_price": 30000,
            "formula_condition": []
        }
        url = reverse('ShippingList')  # noqa
        response = self.client.post(url, data, format='json')

        self.assertResponseList(
            response,
            status_code=status.HTTP_400_BAD_REQUEST,
            key_required=['errors', 'status'],
            all_key=['errors', 'status'],
            all_key_from=response.data,
            type_match={'errors': dict, 'status': int},
        )
        self.assertCountEqual(
            response.data['errors'],
            ['currency'],
            check_sum_second=True,
        )

        data1 = {
            "title": "Chi phí vận chuyển tiêu chuẩn",
            "margin": '',
            "currency": currency[0]['id'],
            "cost_method": 0,
            "formula_condition": []
        }
        response1 = self.client.post(url, data1, format='json')  # noqa
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
            ['margin'],
            check_sum_second=True,
        )

        data2 = {
            "title": "Chi phí vận chuyển tiêu chuẩn",
            "margin": 5,
            "currency": currency[0]['id'],
            "cost_method": 1,
            "formula_condition": [
                {
                    "location": [
                        "string"
                    ],
                    "formula": [
                        {
                            "unit": unit[0]['id'],
                            "comparison_operators": 1,
                            "threshold": 2,
                            "amount_condition": 5000,
                            "extra_amount": 500
                        }
                    ]
                }
            ]
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
            ['location'],
            check_sum_second=True,
        )

        data3 = {  # noqa
            "title": "Chi phí vận chuyển tiêu chuẩn",
            "margin": 5,
            "currency": currency[0]['id'],
            "cost_method": 0,
            "formula_condition": [
                {
                    "location": [
                        location[1]['id']
                    ],
                    "formula": [
                        {
                            "unit": "string",
                            "comparison_operators": 1,
                            "threshold": 2,
                            "amount_condition": 5000,
                            "extra_amount": 500
                        }
                    ]
                }
            ]
        }
        response3 = self.client.post(url, data3, format='json')
        self.assertResponseList(
            response3,
            status_code=status.HTTP_400_BAD_REQUEST,
            key_required=['errors', 'status'],
            all_key=['errors', 'status'],
            all_key_from=response3.data,
            type_match={'errors': dict, 'status': int},
        )
        self.assertCountEqual(
            response3.data['errors'],
            ['unit'],
            check_sum_second=True,
        )
        return None

    def test_get_list(self):
        self.test_create_new_shipping()
        url = reverse("ShippingList")
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
            ['id', 'title', 'code', 'margin', 'is_active', 'currency', 'cost_method', 'fixed_price',
             'formula_condition'],
            check_sum_second=True,
        )
        return response

    def test_get_detail(self, data_id=None):
        data_created = None
        if not data_id:
            data_created = self.test_create_new_shipping()
            data_id = data_created.data['result']['id']
        url = reverse("ShippingDetail", kwargs={'pk': data_id})
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
            ['id', 'title', 'code', 'margin', 'is_active', 'currency', 'cost_method', 'fixed_price',
             'formula_condition'],
            check_sum_second=True,
        )
        if not data_id:
            self.assertEqual(response.data['result']['id'], data_created.data['result']['id'])
            self.assertEqual(response.data['result']['title'], data_created.data['result']['title'])
        else:
            self.assertEqual(response.data['result']['id'], data_id)
        return response

    def test_shipping_update(self):
        currency = ExpenseTestCase.get_currency(self)
        unit = self.get_shipping_unit()
        location = self.get_location()
        title_change = 'Chi phí vận chuyển theo khối lượng'
        fixed_price_change = 25000
        data_created = self.test_create_new_shipping()
        url = reverse("ShippingDetail", kwargs={'pk': data_created.data['result']['id']})
        data = {
            "title": title_change,
            "margin": 0,
            "currency": currency[0]['id'],
            "cost_method": 0,
            "fixed_price": fixed_price_change,
            "is_change_condition": False,
            "formula_condition": [
                {
                    "location": [
                        location[1]['id']
                    ],
                    "formula": [
                        {
                            "unit": unit[0]['id'],
                            "comparison_operators": 1,
                            "threshold": 2,
                            "amount_condition": 5000,
                            "extra_amount": 500
                        }
                    ]
                }
            ]
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data_changed = self.test_get_detail(data_id=data_created.data['result']['id'])
        self.assertEqual(data_changed.data['result']['title'], title_change)
        self.assertEqual(data_changed.data['result']['fixed_price'], fixed_price_change)
        return response
