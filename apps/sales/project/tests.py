from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from apps.core.hr.models import Employee
from apps.shared.extends.tests import AdvanceTestCase
from rest_framework.test import APIClient


class ProjectTestCase(AdvanceTestCase):
    def setUp(self):
        self.maxDiff = None
        self.client = APIClient()
        self.authenticated()
        url_emp = reverse("EmployeeList")
        response = self.client.get(url_emp, format='json')
        employee_obj = Employee.objects.get(id=response.data['result'][0]['id'])
        self.employee = employee_obj

    def test_create_project(self):
        time_now = timezone.now()
        data = {
            'title': 'project test create',
            'project_pm': str(self.employee.id),
            'employee_inherit': str(self.employee.id),
            'start_date': time_now.strftime('%Y-%m-%d'),
            'end_date': (time_now + timedelta(weeks=12)).strftime('%Y-%m-%d'),
        }
        response = self.client.post(reverse('ProjectList'), data, format='json')
        self.assertEqual(response.status_code, 201)
        return response

    def test_get_list_project(self):
        self.test_create_project()
        response = self.client.get(reverse('ProjectList'), format='json')
        self.assertResponseList(
            response,
            status_code=status.HTTP_200_OK,
            key_required=['result', 'status', 'next', 'previous', 'count', 'page_size'],
            all_key=['result', 'status', 'next', 'previous', 'count', 'page_size'],
            all_key_from=response.data,
            type_match={'result': list, 'status': int, 'next': int, 'previous': int, 'count': int, 'page_size': int},
        )

    def test_get_detail_project(self):
        res = self.test_create_project()
        url = reverse('ProjectDetail', args=[res.data['result'].get('id', '')])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, res.data['result'].get('id', ''), None, response.status_code)
        self.assertContains(response, res.data['result'].get('title', ''), None, response.status_code)
        self.assertContains(response, res.data['result'].get('code', ''), None, response.status_code)

    def test_create_group_and_work(self):
        res = self.test_create_project()
        time_now = timezone.now()
        data = {
            'project': res.data['result'].get('id', ''),
            'title': 'group milestone 01',
            'employee_inherit': str(self.employee.id),
            'gr_weight': 10,
            'gr_rate': 0,
            'gr_start_date': time_now.strftime('%Y-%m-%d'),
            'gr_end_date': (time_now + timedelta(weeks=1)).strftime('%Y-%m-%d'),
            'order': 1
        }
        response = self.client.post(reverse('ProjectGroupList'), data, format='json')
        self.assertEqual(response.status_code, 201)
        data_work = {
            'project': res.data['result'].get('id', ''),
            'title': 'work in milestone',
            'group': response.data['result'].get('id', ''),
            'employee_inherit': str(self.employee.id),
            'w_weight': 50,
            'w_rate': 0,
            'w_start_date': time_now.strftime('%Y-%m-%d'),
            'w_end_date': (time_now + timedelta(days=3)).strftime('%Y-%m-%d'),
            'order': 2
        }
        response_work = self.client.post(reverse('ProjectWorkList'), data_work, format='json')
        self.assertEqual(response_work.status_code, 201)
