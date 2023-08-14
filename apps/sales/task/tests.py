from django.urls import reverse

from apps.core.company.models import Company
from apps.sales.opportunity.tests import TestCaseOpportunity
from apps.shared.extends.tests import AdvanceTestCase
from rest_framework.test import APIClient


class TaskTestCase(AdvanceTestCase):
    def setUp(self):
        self.maxDiff = None
        self.client = APIClient()
        self.authenticated()

        company_data = {
            'title': 'Cty TNHH one member',
            'code': 'MMT',
            'representative_fullname': 'Mike Nguyen',
            'address': '7826 avenue, Victoria Street, California, American',
            'email': 'mike.nguyen.7826@gmail.com',
            'phone': '0983875345',
        }
        company_req = self.client.post(reverse("CompanyList"), company_data, format='json')
        self.assertEqual(company_req.status_code, 201)
        company_obj = Company.objects.get(id=company_req.data['result']['id'])
        self.company_obj = company_obj

    def test_create_opps(self):
        response = TestCaseOpportunity.test_create_opportunity(self)
        return response

    # def test_create_task_config(self):
    #     ConfigDefaultData(self.company_obj).task_config()
    #     task_status_res = self.client.get(reverse("OpportunityTaskStatusList"), format='json')
    #     self.assertEqual(task_status_res.status_code, status.HTTP_200_OK)
    #     return task_status_res

    # def test_create_task(self):
    #     opps = PickingDeliveryTestCase.create_opps()
    #     data = {
    #         "title": "test create task",
    #         "task_status": PickingDeliveryTestCase.test_create_task_config().data['result'][0]['id'],
    #         "start_date": "2024-09-08",
    #         "end_date": "2024-09-20",
    #         "estimate": "1d",
    #         "opportunity": opps,
    #         "priority": 0,
    #         "label": ["lorem", "ipsum", "dolor"],
    #         "assign_to": self.get_employee().data['result']['id'],
    #         "checklist": [
    #             {"name": "checklist 01", "done": False}
    #         ],
    #         "parent_n": "",
    #         "remark": "lorem ipsum dolor sit amet",
    #         "employee_created": self.get_employee().data['result']['id'],
    #     }
    #     task_response = self.client.post(reverse("OpportunityTaskList"), data, format='json')
    #     self.assertEqual(task_response.status_code, 201)
