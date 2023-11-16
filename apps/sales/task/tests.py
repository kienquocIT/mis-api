from django.urls import reverse
from rest_framework import status

from apps.core.company.models import Company
from apps.sales.opportunity.tests import TestCaseOpportunity
from apps.shared.extends.signals import ConfigDefaultData
from apps.shared.extends.tests import AdvanceTestCase
from rest_framework.test import APIClient


class TaskTestCase(AdvanceTestCase):
    def setUp(self):
        self.maxDiff = None
        self.client = APIClient()
        self.authenticated()

    def create_new_currency(self):
        data = {
            "abbreviation": "CAD",
            "title": "CANADIAN DOLLAR",
            "rate": 0.45
        }
        response = self.client.post(reverse("CurrencyList"), data, format='json')
        self.assertEqual(response.status_code, 201)
        return response

    def create_company(self):
        company_data = {
            'title': 'Cty TNHH one member',
            'code': 'MMT',
            'representative_fullname': 'Mike Nguyen',
            'address': '7826 avenue, Victoria Street, California, American',
            'email': 'mike.nguyen.7826@gmail.com',
            'phone': '0983875345',
            'primary_currency': self.create_new_currency().data['result']['id']
        }
        company_req = self.client.post(reverse("CompanyList"), company_data, format='json')
        self.assertEqual(company_req.status_code, 201)
        company_obj = Company.objects.get(id=company_req.data['result']['id'])
        return company_obj

    def get_employee(self):
        response = self.client.get(reverse("EmployeeList"), format='json')
        return response

    def test_create_task_config(self, is_create_company=True):
        if is_create_company:
            company = TaskTestCase.create_company(self)
            ConfigDefaultData(company).task_config()
        task_status_res = self.client.get(reverse("OpportunityTaskStatusList"), format='json')
        self.assertEqual(task_status_res.status_code, status.HTTP_200_OK)
        return task_status_res

    def test_create_task(self):
        opps = TestCaseOpportunity.test_create_opportunity(self)
        employee = TaskTestCase.get_employee(self).data['result']
        data = {
            "title": "test create task",
            "task_status": TaskTestCase.test_create_task_config(self).data['result'][0]['id'],
            "start_date": "2024-09-08",
            "end_date": "2024-09-20",
            "estimate": "1d",
            "opportunity": opps.data['result']['id'],
            "priority": 0,
            "label": ["lorem", "ipsum", "dolor"],
            "assign_to": employee[0]['id'],
            "checklist": [
                {"name": "checklist 01", "done": False}
            ],
            "remark": "lorem ipsum dolor sit amet",
            "employee_created": employee[0]['id'],
        }
        task_response = self.client.post(reverse("OpportunityTaskList"), data, format='json')
        self.assertEqual(task_response.status_code, 201)
        return task_response

    def test_get_list_task(self):
        TaskTestCase.test_create_task(self)
        url = reverse('OpportunityTaskList')
        response = self.client.get(url, format='json')
        self.assertResponseList( # noqa
            response,
            status_code=status.HTTP_200_OK,
            key_required=['result', 'status', 'next', 'previous', 'count', 'page_size'],
            all_key=['result', 'status', 'next', 'previous', 'count', 'page_size'],
            all_key_from=response.data,
            type_match={'result': list, 'status': int, 'next': int, 'previous': int, 'count': int, 'page_size': int},
        )

    def test_get_detail_task(self):
        res = TaskTestCase.test_create_task(self)
        url = reverse('OpportunityTaskDetail', args=[res.data['result'].get('id', '')])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, res.data['result'].get('id', ''), None, response.status_code)
        self.assertContains(response, res.data['result'].get('title', ''), None, response.status_code)

    def test_update_task(self):
        task = TaskTestCase.test_create_task(self).data['result']
        task['task_status'] = TaskTestCase.test_create_task_config(
            self, is_create_company=False
        ).data['result'][1]['id']
        del [task['parent_n'], task['attach']]
        url = reverse('OpportunityTaskDetail', args=[task.get('id', '')])
        self.client.put(url, task, format='json')
        response = self.client.get(url, task, format='json')
        self.assertEqual(response.status_code, 200)

    def test_update_stt_task(self):
        task = TaskTestCase.test_create_task(self).data['result']
        data = {
            "task_status": TaskTestCase.test_create_task_config(
                self, is_create_company=False
            ).data['result'][2]['id']
        }
        url = reverse('OpportunityTaskSwitchSTT', args=[task.get('id', '')])
        self.client.put(url, data, format='json')
        response = self.client.get(reverse('OpportunityTaskDetail', args=[task.get('id', '')]), format='json')
        self.assertEqual(response.status_code, 200)
