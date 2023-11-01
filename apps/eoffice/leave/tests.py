from datetime import timedelta

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.utils import timezone

from apps.eoffice.leave.models import LeaveConfig, LeaveType, WorkingCalendarConfig, WorkingYearConfig
from apps.shared.extends.tests import AdvanceTestCase


class LeaveTestCase(AdvanceTestCase):
    def setUp(self):
        self.maxDiff = None  # noqa
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
            defaults={  # noqa
                'working_days':
                    {
                        0: {
                            'work': False,
                            'mor': {'from': '8:00 AM', 'to': '12:00 AM'},
                            'aft': {'from': '1:30 PM', 'to': '5:30 PM'}
                        },
                        1: {
                            'work': True,
                            'mor': {'from': '8:00 AM', 'to': '12:00 AM'},
                            'aft': {'from': '1:30 PM', 'to': '5:30 PM'}
                        },
                        2: {
                            'work': True,
                            'mor': {'from': '8:00 AM', 'to': '12:00 AM'},
                            'aft': {'from': '1:30 PM', 'to': '5:30 PM'}
                        },
                        3: {
                            'work': True,
                            'mor': {'from': '8:00 AM', 'to': '12:00 AM'},
                            'aft': {'from': '1:30 PM', 'to': '5:30 PM'}
                        },
                        4: {
                            'work': True,
                            'mor': {'from': '8:00 AM', 'to': '12:00 AM'},
                            'aft': {'from': '1:30 PM', 'to': '5:30 PM'}
                        },
                        5: {
                            'work': True,
                            'mor': {'from': '8:00 AM', 'to': '12:00 AM'},
                            'aft': {'from': '1:30 PM', 'to': '5:30 PM'}
                        },
                        6: {
                            'work': False,
                            'mor': {'from': '8:00 AM', 'to': '12:00 AM'},
                            'aft': {'from': '1:30 PM', 'to': '5:30 PM'}
                        },
                    }
            },
        )
        self.working_calendar = working_calendar[0]
        self.company = company_req

    def get_employee(self):
        url = reverse("EmployeeList")
        response = self.client.get(url, format='json')
        return response

    def test_create_leave_type_01(self):
        lv_type = {
            'code': 'CODE.TEST.SC',
            'title': 'Sick yours child-social insurance',
            'paid_by': 2,
            'balance_control': False,
            'is_check_expiration': False,
            'leave_config': str(self.config.id),
            'company_id': str(self.config.company_id),
            'prev_year': 0
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
            'leave_config': str(leave["leave_config"]),
            'balance_control': leave["balance_control"]
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

    def test_delete_working_year(self):
        res = self.test_create_working_year()
        year = res.data.get('result')
        url = reverse('WorkingYearDetail', args=[year["id"]])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(WorkingYearConfig.objects.filter(id=year['id']).exists())

    def test_create_leave_request(self):
        leave_type = LeaveType.objects.filter_current(
            company_id=self.company.data['result']['id'],
            code='ANPY'
        ).first()
        time_now = timezone.now().strftime('%Y-%m-%d')
        data = {
            'title': 'xin nghỉ làm việc nhà',
            'employee_inherit_id': self.get_employee().data['result'][0]['id'],
            'request_date': time_now,
            'detail_data': [{
                "order": 0,
                "remark": "lorem ipsum",
                "date_to": time_now,
                "subtotal": 1,
                "date_from": time_now,
                "leave_type": {
                    "leave_type": {
                        "id": str(leave_type.id),
                        "code": str(leave_type.code),
                    }
                },
                "morning_shift_f": True,
                "morning_shift_t": False
            }],
            'start_day': time_now,
            'total': 1
        }
        response = self.client.post(reverse('LeaveRequestList'), data, format='json')
        self.assertEqual(response.status_code, 201)
        return response

    def test_get_list_leave_request(self):
        self.test_create_leave_request()
        url = reverse('LeaveRequestList')
        response = self.client.get(url, format='json')
        self.assertResponseList(  # noqa
            response,
            status_code=status.HTTP_200_OK,
            key_required=['result', 'status', 'next', 'previous', 'count', 'page_size'],
            all_key=['result', 'status', 'next', 'previous', 'count', 'page_size'],
            all_key_from=response.data,
            type_match={'result': list, 'status': int, 'next': int, 'previous': int, 'count': int, 'page_size': int},
        )

    def test_get_detail_leave_request(self):
        res = self.test_create_leave_request()
        url = reverse('LeaveRequestDetail', args=[res.data['result'].get('id', '')])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, res.data['result'].get('id', ''), None, response.status_code)
        self.assertContains(response, res.data['result'].get('title', ''), None, response.status_code)

    def test_update_detail_leave_request(self):
        res = self.test_create_leave_request()
        url = reverse('LeaveRequestDetail', args=[res.data['result'].get('id', '')])
        get_detail = self.client.get(url, format='json')
        data = get_detail.data['result']
        time_now = (timezone.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        data_update = {
            'title': 'xin nghỉ làm việc nhà update',
            'start_day': time_now
        }
        self.client.put(url, data_update, format='json')
        response = self.client.get(url, data, format='json')
        self.assertEqual(response.status_code, 200)
