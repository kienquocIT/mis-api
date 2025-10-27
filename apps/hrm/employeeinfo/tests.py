from uuid import uuid4

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.core.base.models import Country, NProvince
from apps.core.hr.models import Employee
from apps.shared.extends.tests import AdvanceTestCase
from apps.shared.scripts import create_empl_map_hrm


class EmployeeInfoTestCase(AdvanceTestCase):
    def setUp(self):
        self.maxDiff = None
        self.client = APIClient()
        self.authenticated()
        url_emp = reverse("EmployeeList")
        response = self.client.get(url_emp, format='json')
        employee_obj = Employee.objects.get(id=response.data['result'][0]['id'])
        self.employee = employee_obj
        self.company = employee_obj.company
        self.country = Country.objects.first()
        self.city = NProvince.objects.first()
        # run script employee map employee info
        create_empl_map_hrm()
        emp_not_map_res = self.client.get(reverse("EmployeeNotMapHRMList"), format='json')
        self.employee_not_map_hrm = emp_not_map_res.data['result'][0]['employee']['id']

    def test_create_new_employee(self):
        data = {
            # employee data
            'employee_create': uuid4(),
            'code': 'NEWEMP002',
            'first_name': 'Nguyen Van',
            'last_name': 'A',
            'email': 'anv@email.com',
            'phone': '0908060054',
            'date_joined': '2023-10-12',
            'contract': {},
            # employee info data
            'citizen_id': '001081234567',
            'date_of_issue': '2020-10-12',
            'place_of_issue': 'cuc quan ly ve trat tu xa hoi',
            'place_birth': None,
            'nationality': str(self.country.id),
            'place_origin': None,
            'ethnicity': 'kinh',
            'religion': 'khong',
            'gender': 0,
            'marital_status': 4,
            'bank_acc_no': '0123456778901234',
            'bank_name': 9,
            'acc_name': 'Nguyen Van A',
            'tax_code': '1234567890',
            'permanent_address': '1047 Brea Mall #1047 Brea, CA 92821 , California, United States',
            'current_resident': '11170 Long Beach Blvd, Lynwood, California, United States'
        }
        response = self.client.post(reverse('EmployeeInfoList'), data, format='json')
        self.assertEqual(response.status_code, 201)
        return response

    def test_create_employee_exist(self):
        data = {
            # employee data
            'employee': self.employee_not_map_hrm,
            'code': 'NEWEMP003',
            'first_name': 'Nguyen Thi Vo',
            'last_name': 'Tu',
            'email': 'tuntv@email.com',
            'phone': '0933954425',
            'date_joined': '2023-10-13',
            'contract': {},
            # employee info data
            'citizen_id': '001081237890',
            'date_of_issue': '2020-10-14',
            'place_of_issue': 'cuc quan ly ve trat tu xa hoi',
            'place_birth': None,
            'nationality': str(self.country.id),
            'place_origin': None,
            'ethnicity': 'kinh',
            'religion': 'khong',
            'gender': 1,
            'marital_status': 4,
            'bank_acc_no': '0123456778901234',
            'bank_name': 9,
            'acc_name': 'Nguyen Thi Vo Tu',
            'tax_code': '0123456789',
            'permanent_address': '1047 Brea Mall #1047 Brea, CA 92821 , California, United States',
            'current_resident': '11170 Long Beach Blvd, Lynwood, California, United States'
        }
        response = self.client.post(reverse('EmployeeInfoList'), data, format='json')
        self.assertEqual(response.status_code, 201)
        return response

    def test_get_list_employee_info(self):
        self.test_create_new_employee()
        response = self.client.get(reverse('EmployeeInfoList'), format='json')
        self.assertResponseList(
            response,
            status_code=status.HTTP_200_OK,
            key_required=['result', 'status', 'next', 'previous', 'count', 'page_size'],
            all_key=['result', 'status', 'next', 'previous', 'count', 'page_size'],
            all_key_from=response.data,
            type_match={'result': list, 'status': int, 'next': int, 'previous': int, 'count': int, 'page_size': int},
        )

    def test_get_detail_project(self):
        res = self.test_create_new_employee()
        url = reverse('EmployeeInfoDetail', args=[res.data['result'].get('id', '')])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, res.data['result'].get('id', ''), None, response.status_code)

    def test_update_employee_info(self):
        res = self.test_create_new_employee()
        url = reverse('EmployeeInfoDetail', args=[res.data['result'].get('id', '')])
        data_update = {
            'contract': {
                'employee_info': res.data['result'].get('id', ''),
                'contract_type': 0,
                'limit_time': 'true',
                'effected_date': '2023-09-10',
                'expired_date': '2024-09-10',
                'represent': self.employee.id,
                'signing_date': '2023-09-09',
                'file_type': 1,
                'content': '<p>The quick brown fox jumps over the lazy dog.</p>'
            },
        }
        self.client.put(url, data_update, format='json')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
