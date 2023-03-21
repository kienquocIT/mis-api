from django.urls import reverse
from rest_framework.test import APITestCase


# Create your tests here.


class AuthTestCase(APITestCase):
    def call_login(self):
        new_tenant = {
            "tenant_data": {
                "title": "Công ty Tài Chính F88",
                "code": "F88",
                "sub_domain": "F88",
                "representative_fullname": "string",
                "representative_phone_number": "string",
                "auto_create_company": True,
                "company_quality_max": 5,
                "user_request_created": {
                    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    "full_name": "string",
                    "email": "string",
                    "phone": "string"
                },
                "plan": {}
            },
            "user_data": {
                "first_name": "Nam",
                "last_name": "Trinh Tuan",
                "email": "namt9@gmail.com",
                "phone": "01976741334",
                "username": "admin",
                "password": "111111"
            },
            "create_admin": True,
            "create_employee": False,
            "plan_data": {}
        }
        url_tenant = reverse('NewTenant')
        a = self.client.post(url_tenant, new_tenant, format='json')

        # login
        url_login = reverse('AuthLogin')
        data = {
            "tenant_code": "F88",
            "username": "admin",
            "password": "111111"
        }
        response_login = self.client.post(url_login, data, format='json')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + response_login.data['result']['token']['access_token'])
        return response_login
