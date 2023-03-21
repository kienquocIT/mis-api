from django.urls import reverse
from rest_framework.test import APITestCase
from apps.core.auths.tests import AuthTestCase


class AccountTestCase(APITestCase):
    def setUp(self):

        AuthTestCase.call_login(self)
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
            'name': 'Cong ty Hat Giong Truc Phuong',
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
            'name': 'Cong ty Hat Giong Truc Phuong',
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
            'name': 'Cong ty Hat Giong Truc Phuong',
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

        url_create_employee = reverse('EmployeeList')
        response_employee = self.client.post(
            url_create_employee,
            {
                "first_name": "string",
                "last_name": "string",
                "date_joined": "2023-03-21T04:55:25.254Z",
            },

            format='json'
        )

        self.salutation = response_salutation.data['result']
        self.interest = response_interest.data['result']
        self.employee = response_employee.data['result']

    def test_create_contact(self):
        """
        Create a Contact
        Returns: Object
        """
        data = {
            'owner': self.employee['id'],
            'bio': '03/11/2001',
            'salutation': self.salutation['id'],
            'fullname': "Nguyen Thi Hong",
            'phone': '0987654321',
            'mobile': '0123456789',
            'email': 'nguyenthihong@gmail.com',
            'job_title': 'Manager',
            'address_infor': {
                "home_address": "So 10/11, Xa Duc Lan, Hyen Mo Duc, Tinh Quang Ngai",
                "work_address": "So 20/22, Xa Binh Hung, Huyen Binh Chanh, TP Ho Chi Minh"
            },
            'additional_infor': {
                "tags": "tag",
                "gmail": "nth@gmail.com",
                "twitter": "nth.twitter",
                "facebook": "nth.facebook",
                "linkedln": "nth.linkedln",
                "interests": [self.interest['id']]
            }
        }

        url = reverse('ContactList')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        return response
