from django.urls import reverse
from rest_framework.test import APITestCase
from apps.core.auths.tests import AuthTestCase


#
# class AccountTestCase(APITestCase):
#     def setUp(self):
#
#         AuthTestCase.call_login(self)
#         # create industry
#         url_create_industry = reverse('IndustryList')
#         response_industry = self.client.post(
#             url_create_industry,
#             {
#                 'code': 'I01',
#                 'title': 'Banking',
#             },
#             format='json'
#         )
#
#         url_create_account_type = reverse('AccountTypeList')
#         response_account_type = self.client.post(
#             url_create_account_type,
#             {
#                 'code': 'AT01',
#                 'title': 'customer',
#             },
#             format='json'
#         )
#
#         self.industry = response_industry.data['result']
#         self.account_type = response_account_type.data['result']
#
#     def test_create_new_account(self):
#         data = {
#             'name': 'Công Ty H?t Gi?ng Trúc Phu?ng',
#             'code': 'PM002',
#             'website': 'trucphuong.com.vn',
#             'tax_code': '81H1',
#             'annual_revenue': '10-20 billions',
#             'total_employees': '< 20 people',
#             'phone': '0903608494',
#             'email': 'cuong@gmail.com',
#             'industry': self.industry['id'],
#             'manager': ['a2c0cf06-5221-417c-8d4d-149c015b428e',
#                         'ca3f9aae-884f-4791-a1b9-c7a33d51dbdf'],
#             'account_type': [str(self.account_type['id'])],
#             'customer_type': 'individual',
#         }
#         url = reverse('AccountList')
#         response = self.client.post(url, data, format='json')
#         self.assertEqual(response.status_code, 201)
#         return response
#
#     def test_create_account_duplicate_code(self):
#         self.test_create_new_account()
#         data = {
#             'name': 'Công Ty H?t Gi?ng Trúc Phu?ng',
#             'code': 'PM002',
#             'website': 'trucphuong.com.vn',
#             'tax_code': '81H1',
#             'annual_revenue': '10-20 billions',
#             'total_employees': '< 20 people',
#             'phone': '0903608494',
#             'email': 'cuong@gmail.com',
#             'industry': self.industry['id'],
#             'manager': ['a2c0cf06-5221-417c-8d4d-149c015b428e',
#                         'ca3f9aae-884f-4791-a1b9-c7a33d51dbdf'],
#             'account_type': [str(self.account_type['id'])],
#             'customer_type': 'individual',
#         }
#         url = reverse('AccountList')
#         response = self.client.post(url, data, format='json')
#         self.assertEqual(response.status_code, 400)
#         return response
#
#     def test_create_missing_data(self):
#         data = {
#             'website': 'trucphuong.com.vn',
#             'tax_code': '81H1',
#             'annual_revenue': '10-20 billions',
#             'total_employees': '< 20 people',
#             'phone': '0903608494',
#             'email': 'cuong@gmail.com',
#             'industry': self.industry['id'],
#             'manager': ['a2c0cf06-5221-417c-8d4d-149c015b428e',
#                         'ca3f9aae-884f-4791-a1b9-c7a33d51dbdf'],
#             'account_type': [str(self.account_type['id'])],
#             'customer_type': 'individual',
#         }
#         url = reverse('AccountList')
#         response = self.client.post(url, data, format='json')
#         self.assertEqual(response.status_code, 400)
#         return response
#
#     def test_data_not_UUID(self):
#         data = {
#             'name': 'Công Ty H?t Gi?ng Trúc Phu?ng',
#             'code': 'PM002',
#             'website': 'trucphuong.com.vn',
#             'tax_code': '81H1',
#             'annual_revenue': '10-20 billions',
#             'total_employees': '< 20 people',
#             'phone': '0903608494',
#             'email': 'cuong@gmail.com',
#             'industry': '1',
#             'manager': ['a2c0cf06-5221-417c-8d4d-149c015b428e',
#                         'ca3f9aae-884f-4791-a1b9-c7a33d51dbdf'],
#             'account_type': '1',
#             'customer_type': 'individual',
#         }
#         url = reverse('AccountList')
#         response = self.client.post(url, data, format='json')
#         self.assertEqual(response.status_code, 400)
#         return response


class ContactTest(APITestCase):
    def setUp(self):
        AuthTestCase.call_login(self)
        # create salutation
        url_create_salutation = reverse('SalutationList')
        response_salutation = self.client.post(
            url_create_salutation,
            {
                'code': 'S01',
                'title': 'Mr',
            },
            format='json'
        )

        url_create_interest = reverse('InterestsList')
        response_interest = self.client.post(
            url_create_interest,
            {
                'code': 'I001',
                'title': 'Travelling',
            },
            format='json'
        )

        self.salutation = response_salutation.data['result']
        self.interest = response_interest.data['result']

    def test_create_contact(self):
        """
        Create a Contact
        Returns: Object
        """
        data = {
            'owner': 'a2c0cf06-5221-417c-8d4d-149c015b428e',
            'bio': '03/11/2001',
            'salutation': self.salutation['id'],
            'fullname': "Nguyen Thi Hong",
            'phone': '0987654321',
            'mobile': '0123456789',
            'email': 'nguyenthihong@gmail.com',
            'job_title': 'Manager',
            'address_infor': {"home_address": "S? 10/67, Xã Ð?c Lân, Huy?n M? Ð?c, T?nh Qu?ng Ngãi", "work_address": "S? 22/20, Th? Tr?n B?ng Son, Huy?n Hoài Nhon, T?nh Bình Ð?nh"},
            'additional_infor': {"tags": "tag", "gmail": "nth@gmail.com", "twitter": "nth.twitter", "facebook": "nth.facebook", "linkedln": "nth.linkedln", "interests": [self.interest['id']]}
        }

        url = reverse('ContactList')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        return response
