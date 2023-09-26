from django.urls import reverse
from rest_framework.test import APIClient

from apps.eoffice.leave.models import LeaveConfig, LeaveType, WorkingCalendarConfig, WorkingYearConfig
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

        working_calendar = WorkingCalendarConfig.objects.get_or_create(
            company_id=company_req.data['result']['id'],
            defaults={
                'working_days':
                    {
                        'mon': {
                            'work': True,
                            'mor': {'from': '08:00 AM', 'to': '12:00 AM'},
                            'aft': {'from': '13:30 PM', 'to': '17:30 PM'}
                        },
                        'tue': {
                            'work': True,
                            'mor': {'from': '08:00 AM', 'to': '12:00 AM'},
                            'aft': {'from': '13:30 PM', 'to': '17:30 PM'}
                        },
                        'wed': {
                            'work': True,
                            'mor': {'from': '08:00 AM', 'to': '12:00 AM'},
                            'aft': {'from': '13:30 PM', 'to': '17:30 PM'}
                        },
                        'thu': {
                            'work': True,
                            'mor': {'from': '08:00 AM', 'to': '12:00 AM'},
                            'aft': {'from': '13:30 PM', 'to': '17:30 PM'}
                        },
                        'fri': {
                            'work': True,
                            'mor': {'from': '08:00 AM', 'to': '12:00 AM'},
                            'aft': {'from': '13:30 PM', 'to': '17:30 PM'}
                        },
                        'sat': {
                            'work': False,
                            'mor': {'from': '08:00 AM', 'to': '12:00 AM'},
                            'aft': {'from': '13:30 PM', 'to': '17:30 PM'}
                        },
                        'sun': {
                            'work': False,
                            'mor': {'from': '08:00 AM', 'to': '12:00 AM'},
                            'aft': {'from': '13:30 PM', 'to': '17:30 PM'}
                        }
                    }
            },
        )
        self.working_calendar = working_calendar[0]

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

    def test_create_working_year(self):
        data_w_year = {
            "working_calendar": self.working_calendar.id,
            "config_year": 2023
        }
        response = self.client.post(reverse('WorkingYearCreate'), data_w_year, format='json')
        self.assertEqual(response.status_code, 201)
        return response

    def test_create_working_holiday(self):
        res = self.test_create_working_year()
        year = res.data.get('result')
        data_w_holiday = {
            "holiday_date_to": "2023-09-26",
            "remark": "Lễ ngày nhà giáo Việt Nam 20-11",
            "year": year["id"]
        }
        response = self.client.post(reverse('WorkingHolidayCreate'), data_w_holiday, format='json')
        self.assertEqual(response.status_code, 201)
        return response

    def test_update_working_holiday(self):
        res = self.test_create_working_holiday()
        holiday = res.data.get('result')
        url_update = reverse('WorkingHolidayDetail', args=[holiday["id"]])
        data_w_holiday = {
            "holiday_date_to": "2023-09-02",
            "remark": "Nghĩ lễ ngày quốc khánh 2-9",
            "year": holiday["year"]
        }
        response_leave = self.client.put(url_update, data_w_holiday, format='json')
        self.assertEqual(response_leave.status_code, 200)

    def test_delete_working_holiday(self):
        res = self.test_create_working_holiday()
        holiday = res.data.get('result')
        url = reverse('WorkingHolidayDetail', args=[holiday["id"]])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(WorkingYearConfig.objects.filter(id=holiday['id']).exists())

    def test_delete_detail_leave(self):
        res = self.test_create_working_year()
        year = res.data.get('result')
        url = reverse('WorkingYearDetail', args=[year["id"]])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(WorkingYearConfig.objects.filter(id=year['id']).exists())
