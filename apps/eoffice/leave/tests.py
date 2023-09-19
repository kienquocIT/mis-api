from django.urls import reverse
from rest_framework.test import APIClient

from apps.eoffice.leave.models import LeaveConfig, LeaveType
from apps.shared.extends.tests import AdvanceTestCase


class LeaveTestCase(AdvanceTestCase):
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
        leave_cf = LeaveConfig.objects.get_or_create(
            company_id=company_req.data['result']['id'],
            defaults={},
        )
        self.config = leave_cf[0]

    def get_employee(self):
        url = reverse("EmployeeList")
        response = self.client.get(url, format='json')
        return response

    def test_create_leave_type_01(self):
        lv_type = {
            'code': 'CODE.TEST.SC', 'title': 'Sick yours child-social insurance', 'paid_by': 2,
            'balance_control': False, 'is_check_expiration': False,
            'leave_config': str(self.config.id), 'company_id': str(self.config.company_id)
        }
        response_lv_type = self.client.post(reverse('LeaveTypeConfigCreate'), lv_type, format='json')
        self.assertEqual(response_lv_type.status_code, 201)
        return response_lv_type

    def test_update_leave_type_01(self):
        res = self.test_create_leave_type_01()
        leave = res.data.get('result')
        url_update = reverse('LeaveTypeConfigUpdate', args=[leave["id"]])
        leave_upd = {
            'no_of_paid': 12,
            'leave_config': str(leave["leave_config"])
        }
        response_leave = self.client.put(url_update, leave_upd, format='json')
        self.assertEqual(response_leave.status_code, 200)

    def test_delete_detail_leave(self):
        res = self.test_create_leave_type_01()
        leave = res.data.get('result')
        url = reverse('LeaveTypeConfigUpdate', args=[leave['id']])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(LeaveType.objects.filter(id=leave['id'], is_delete=False).exists())
