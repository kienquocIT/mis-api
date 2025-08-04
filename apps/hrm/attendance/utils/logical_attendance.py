from datetime import datetime

import requests
from requests.auth import HTTPDigestAuth
from apps.shared import DisperseModel


HOLIDAY = ["2025-04-30", "2025-05-01", "2025-09-02"]


class AttendanceHandler:
    @classmethod
    def check_attendance(cls, employee_id, date):
        data_logs = DeviceIntegrate.get_attendance(
            device_ip="192.168.0.40",
            username="admin",
            password="mts@2025",
            date=date
        )

        model_employee = DisperseModel(app_model='hr.Employee').get_model()
        if model_employee and hasattr(model_employee, 'objects'):
            employee_obj = model_employee.objects.filter_on_company(id=employee_id).first()
            if employee_obj:
                leaves = employee_obj.leave_leaverequestdatelistregister_employee_inherit.filter_on_company(
                    date_from__lte=date, date_to__gte=date, leave__system_status=3,
                )
                businesses = [item.business_mapped for item in employee_obj.businessrequestemployeeontrip_set.filter(
                    business_mapped__date_f__date__lte=date,
                    business_mapped__date_t__date__gte=date,
                    business_mapped__system_status=3,
                )]
                shift_assigns = employee_obj.shift_assignment_employee.filter_on_company(date=date)
                return AttendanceHandler.active_check(
                    date=date,
                    employee_obj=employee_obj,
                    data_logs=data_logs,
                    leaves=leaves,
                    businesses=businesses,
                    shift_assigns=shift_assigns
                )
        return []

    @classmethod
    def active_check(cls, date, employee_obj, data_logs, leaves, businesses, shift_assigns):
        data_push_list = []
        integrate = employee_obj.device_integrate_employee.filter_on_company().first()
        if integrate:
            data_push = {
                'employee_id': employee_obj.id,
                'date': date,
                'tenant_id': employee_obj.tenant_id,
                'company_id': employee_obj.company_id,
            }
            if date in HOLIDAY:
                print(f"[{date}] Holiday")
                data_push.update({'attendance_status': 5})
                data_push_list.append(data_push)
                return data_push_list
            if not shift_assigns:
                print(f"[{date}] Weekend")
                data_push.update({'attendance_status': 4})
                data_push_list.append(data_push)
                return data_push_list
            if shift_assigns:
                # Lọc logs theo ngày và employee_id
                logs_on_day = [
                    log for log in data_logs
                    if log['employeeNoString'] == integrate.device_employee_id and log['time'].startswith(date)
                ]
                for log in logs_on_day:
                    log.update({
                        'timestamp': datetime.fromisoformat(log['time'])
                    })
                for shift_assign in shift_assigns:
                    data_push = AttendanceHandler.check_by_cases(
                        date=date,
                        logs_on_day=logs_on_day,
                        shift_assign=shift_assign,
                        leaves=leaves,
                        businesses=businesses,
                        data_push=data_push,
                    )
                    if data_push:
                        data_push_list.append(data_push)
        return data_push_list

    @classmethod
    def check_by_cases(cls, date, logs_on_day, shift_assign, leaves, businesses, data_push):
        data_check = {}
        shift_check = shift_assign.shift
        if shift_check:
            data_push.update({
                'shift_id': str(shift_check.id),
            })
            # Kiểm tra nghỉ phép
            if leaves:
                data_check = AttendanceHandler.run_check_leave(
                    date=date,
                    logs_on_day=logs_on_day,
                    leaves=leaves,
                    shift_check=shift_check
                )
            # Kiểm tra công tác
            if businesses:
                data_check = AttendanceHandler.run_check_business(
                    date=date,
                    businesses=businesses
                )
            if not leaves and not businesses:
                checkin_time, checkout_time = AttendanceHandler.parse_checkin_checkout_grace(
                    shift_check=shift_check,
                    check_type=0,
                )
                data_check = AttendanceHandler.run_check_normal(
                    date=date,
                    logs_on_day=logs_on_day,
                    checkin_time=checkin_time,
                    checkout_time=checkout_time
                )
            for key, value in data_check.items():
                if key not in data_push:
                    data_push.update({key: value})
        return data_push

    @classmethod
    def run_check_normal(cls, date, logs_on_day, checkin_time, checkout_time):
        checkin_log = None
        checkout_log = None
        if checkin_time and checkout_time:
            keys = ['from', 'to']
            if all(key in checkin_time for key in keys) and all(key in checkout_time for key in keys):
                for log in logs_on_day:
                    # is_checkin = False
                    # is_checkout = False
                    log_time = log['timestamp'].time()
                    # if log['event_type'] == "IN":
                    is_checkin = AttendanceHandler.check_normal_is_checkin(
                        log_time=log_time,
                        checkin_time_from=checkin_time['from'],
                        checkin_time_to=checkin_time['to'],
                    )
                    # if log['event_type'] == "OUT":
                    is_checkout = AttendanceHandler.check_normal_is_checkout(
                        log_time=log_time,
                        checkout_time_from=checkout_time['from'],
                        checkout_time_to=checkout_time['to'],
                    )
                    if is_checkin is True:
                        checkin_log = AttendanceHandler.check_normal_set_log(
                            check_log=checkin_log,
                            log_time=log_time,
                            log=log,
                            check_type='in',
                        )
                    if is_checkout is True:
                        checkout_log = AttendanceHandler.check_normal_set_log(
                            check_log=checkout_log,
                            log_time=log_time,
                            log=log,
                            check_type='out',
                        )
        return AttendanceHandler.check_normal_push_data(
            date=date,
            checkin_log=checkin_log,
            checkout_log=checkout_log
        )

    @classmethod
    def check_normal_is_checkin(cls, log_time, checkin_time_from, checkin_time_to):
        if checkin_time_from == checkin_time_to:
            if log_time <= checkin_time_from:
                return True
        if checkin_time_from != checkin_time_to:
            if checkin_time_from <= log_time <= checkin_time_to:
                return True
        return False

    @classmethod
    def check_normal_is_checkout(cls, log_time, checkout_time_from, checkout_time_to):
        if checkout_time_from == checkout_time_to:
            if log_time >= checkout_time_from:
                return True
        if checkout_time_from != checkout_time_to:
            if checkout_time_to >= log_time >= checkout_time_from:
                return True
        return False

    @classmethod
    def check_normal_set_log(cls, check_log, log_time, log, check_type):
        if check_log is None:
            check_log = log
        else:
            prev_time = log['timestamp'].time()
            if check_type == 'in':
                if log_time > prev_time:
                    check_log = log
            if check_type == 'out':
                if log_time < prev_time:
                    check_log = log
        return check_log

    @classmethod
    def check_normal_push_data(cls, date, checkin_log, checkout_log):
        data_push = {}
        if checkin_log:
            checkin_time = checkin_log['timestamp'].time()
            data_push.update({
                # 'is_checkin': True,
                'checkin_time': checkin_time,
            })
            print(f"[{date}] Check-in OK: {checkin_time}")
        else:
            print(f"[{date}] ❌ Không có check-in đúng giờ")

        if checkout_log:
            checkout_time = checkout_log['timestamp'].time()
            data_push.update({
                # 'is_checkout': True,
                'checkout_time': checkout_time,
            })
            print(f"[{date}] Check-out OK: {checkout_time}")
        else:
            print(f"[{date}] ❌ Không có check-out đúng giờ")

        if checkin_log and checkout_log:
            data_push.update({
                'attendance_status': 1,
            })
            print(f"[{date}] Present")
        else:
            data_push.update({
                'attendance_status': 0,
            })
            print(f"[{date}] Absent")
        return data_push

    @classmethod
    def run_check_leave(cls, date, logs_on_day, leaves, shift_check):
        data_push = {}
        for leave in leaves:
            if leave.subtotal >= 1:
                data_push.update({
                    'attendance_status': 2,
                    'leave_id': leave.leave_id,
                    'leave_data': {
                        'id': str(leave.leave_id),
                        'title': str(leave.leave.title),
                        'code': str(leave.leave.code),
                        'date_from': str(leave.date_from),
                        'date_to': str(leave.date_to),
                        'total_day': leave.subtotal,
                    } if leave.leave else {},
                })
                print(f"[{date}] Leave")
            if leave.subtotal == 0.5:
                if leave.morning_shift_f is True and leave.morning_shift_t is True:
                    checkin_time, checkout_time = AttendanceHandler.parse_checkin_checkout_grace(
                        shift_check=shift_check,
                        check_type=1,
                        is_first_shift=True,
                    )
                    data_push = AttendanceHandler.run_check_normal(
                        date=date,
                        logs_on_day=logs_on_day,
                        checkin_time=checkin_time,
                        checkout_time=checkout_time
                    )
                if leave.morning_shift_f is False and leave.morning_shift_t is False:
                    checkin_time, checkout_time = AttendanceHandler.parse_checkin_checkout_grace(
                        shift_check=shift_check,
                        check_type=1,
                        is_second_shift=True,
                    )
                    data_push = AttendanceHandler.run_check_normal(
                        date=date,
                        logs_on_day=logs_on_day,
                        checkin_time=checkin_time,
                        checkout_time=checkout_time
                    )
                data_push.update({
                    'leave_id': leave.leave_id,
                    'leave_data': {
                        'id': str(leave.leave_id),
                        'title': str(leave.leave.title),
                        'code': str(leave.leave.code),
                        'date_from': str(leave.date_from),
                        'date_to': str(leave.date_to),
                        'total_day': leave.subtotal,
                    } if leave.leave else {},
                })
        return data_push

    @classmethod
    def run_check_business(cls, date, businesses):
        data_push = {}
        for business in businesses:
            if business.total_day >= 1:
                data_push.update({
                    'attendance_status': 3,
                    'business_id': business.id,
                    'business_data': {
                        'id': str(business.id),
                        'title': str(business.title),
                        'code': str(business.code),
                        'date_from': str(business.date_f.date()),
                        'date_to': str(business.date_t.date()),
                        'total_day': business.total_day,
                    },
                })
                print(f"[{date}] Business")
        return data_push

    # @classmethod
    # def parse_checkin_checkout(cls, shift_check, check_type, is_first_shift=False, is_second_shift=False):
    #     checkin_time = None
    #     checkout_time = None
    #     if check_type == 0:
    #         checkin_time = (
    #                 datetime.combine(
    #                     datetime.today(), shift_check.checkin_time
    #                 ) + timedelta(minutes=shift_check.checkin_threshold)
    #         ).time()
    #         checkout_time = (
    #                 datetime.combine(
    #                     datetime.today(), shift_check.checkout_time
    #                 ) - timedelta(minutes=shift_check.checkout_threshold)
    #         ).time()
    #     if check_type == 1:
    #         if is_first_shift is True:
    #             checkin_time = (
    #                     datetime.combine(
    #                         datetime.today(), shift_check.break_out_time
    #                     ) + timedelta(minutes=shift_check.break_out_threshold)
    #             ).time()
    #             checkout_time = (
    #                     datetime.combine(
    #                         datetime.today(), shift_check.checkout_time
    #                     ) - timedelta(minutes=shift_check.checkout_threshold)
    #             ).time()
    #         if is_second_shift is True:
    #             checkin_time = (
    #                     datetime.combine(
    #                         datetime.today(), shift_check.checkin_time
    #                     ) + timedelta(minutes=shift_check.checkin_threshold)
    #             ).time()
    #             checkout_time = (
    #                     datetime.combine(
    #                         datetime.today(), shift_check.break_in_time
    #                     ) - timedelta(minutes=shift_check.break_in_threshold)
    #             ).time()
    #     return checkin_time, checkout_time

    @classmethod
    def parse_checkin_checkout(cls, shift_check, check_type, is_first_shift=False, is_second_shift=False):
        checkin_time = None
        checkout_time = None
        if check_type == 0:
            checkin_time = shift_check.checkin_time
            checkout_time = shift_check.checkout_time
        if check_type == 1:
            if is_first_shift is True:
                checkin_time = shift_check.break_out_time
                checkout_time = shift_check.checkout_time
            if is_second_shift is True:
                checkin_time = shift_check.checkin_time
                checkout_time = shift_check.break_in_time
        return checkin_time, checkout_time

    @classmethod
    def parse_checkin_checkout_grace(cls, shift_check, check_type, is_first_shift=False, is_second_shift=False):
        checkin_time = None
        checkout_time = None
        # Kiểm tra bình thường
        if check_type == 0:
            checkin_time = {'from': shift_check.checkin_time, 'to': shift_check.checkin_time}
            checkout_time = {'from': shift_check.checkout_time, 'to': shift_check.checkout_time}
            if shift_check.checkin_gr_start and shift_check.checkin_gr_end:
                checkin_time = {'from': shift_check.checkin_gr_start, 'to': shift_check.checkin_gr_end}
            if shift_check.checkout_gr_start and shift_check.checkout_gr_end:
                checkout_time = {'from': shift_check.checkout_gr_start, 'to': shift_check.checkout_gr_end}
        # Kiểm tra có nghỉ phép
        if check_type == 1:
            if is_first_shift is True:
                checkin_time = {'from': shift_check.break_out_time, 'to': shift_check.break_out_time}
                checkout_time = {'from': shift_check.checkout_time, 'to': shift_check.checkout_time}
                if shift_check.break_out_gr_start and shift_check.break_out_gr_end:
                    checkin_time = {'from': shift_check.break_out_gr_start, 'to': shift_check.break_out_gr_end}
                if shift_check.checkout_gr_start and shift_check.checkout_gr_end:
                    checkout_time = {'from': shift_check.checkout_gr_start, 'to': shift_check.checkout_gr_end}
            if is_second_shift is True:
                checkin_time = {'from': shift_check.checkin_time, 'to': shift_check.checkin_time}
                checkout_time = {'from': shift_check.break_in_time, 'to': shift_check.break_in_time}
                if shift_check.checkin_gr_start and shift_check.checkin_gr_end:
                    checkin_time = {'from': shift_check.checkin_gr_start, 'to': shift_check.checkin_gr_end}
                if shift_check.break_in_gr_start and shift_check.break_in_gr_end:
                    checkout_time = {'from': shift_check.break_in_gr_start, 'to': shift_check.break_in_gr_end}
        return checkin_time, checkout_time


class DeviceIntegrate:

    # Cấu hình minor cho từng thiết bị
    DEVICE_MINOR_CODES = {
        "192.168.0.40": [38, 75],
    }

    @classmethod
    def get_user(cls, device_ip, username, password):
        """
        # post data:

        searchID:
            ID tìm kiếm, dùng khi chia kết quả thành nhiều trang. Mỗi lần gọi mới có thể để "1".	"1"
        searchResultPosition:
            Vị trí bắt đầu lấy kết quả. Dùng để phân trang (page offset).	0 = bắt đầu từ kết quả đầu tiên
        maxResults:
            Số bản ghi tối đa trả về trong 1 lần gọi.	50 = trả tối đa 50 bản ghi

        # return data:
        [
            {
                "employeeNo": "3",
                "name": "quannm",
                "userType": "normal",
                "onlyVerify": false,
                "closeDelayEnabled": false,
                "Valid": {
                  "enable": true,
                  "beginTime": "2025-07-31T00:00:00",
                  "endTime": "2035-07-30T23:59:59",
                  "timeType": "local"
                },
                "belongGroup": "",
                "password": "",
                "doorRight": "1",
                "RightPlan": [
                  {
                      "doorNo": 1,
                      "planTemplateNo": "1"
                  }
                ],
                "maxOpenDoorTime": 0,
                "openDoorTime": 0,
                "roomNumber": 0,
                "floorNumber": 0,
                "localUIRight": false,
                "gender": "unknown",
                "numOfCard": 0,
                "numOfFP": 1,
                "numOfFace": 1,
                "groupId": 1,
                "localAtndPlanTemplateId": 0,
                "PersonInfoExtends": [
                  {
                      "value": ""
                  }
                ],
                "faceURL": "http://192.168.0.40/LOCALS/pic/enrlFace/0/0000000003.jpg@WEB000000000112"
                },
        ]
        """

        url = f"http://{device_ip}/ISAPI/AccessControl/UserInfo/Search?format=json"
        all_results = []
        position = 0
        max_results = 50

        while True:
            payload = {
                "UserInfoSearchCond": {
                    "searchID": "1",
                    "searchResultPosition": position,
                    "maxResults": max_results,
                }
            }
            res = requests.post(
                url,
                json=payload,
                auth=HTTPDigestAuth(username, password),
                headers={"Content-Type": "application/json"},
                timeout=10
            )

            if res.status_code != 200:
                print("Error:", res.status_code, res.text)
                break

            data = res.json()
            infos = data.get("UserInfoSearch", {}).get("UserInfo", [])

            if not infos:
                break  # Không còn dữ liệu

            all_results.extend(infos)
            print(f"Lấy được {len(infos)} bản ghi từ offset {position}")

            # Nếu số bản ghi trả về < max_results → hết dữ liệu
            if len(infos) < max_results:
                break

            position += max_results  # Sang trang tiếp theo

        return all_results

    @classmethod
    def get_attendance(cls, device_ip, username, password, date):
        """
        # post data:

        searchID:
            ID tìm kiếm, dùng khi chia kết quả thành nhiều trang. Mỗi lần gọi mới có thể để "1".	"1"
        searchResultPosition:
            Vị trí bắt đầu lấy kết quả. Dùng để phân trang (page offset).	0 = bắt đầu từ kết quả đầu tiên
        maxResults:
            Số bản ghi tối đa trả về trong 1 lần gọi.	50 = trả tối đa 50 bản ghi
        major:
            Mã loại sự kiện lớn. 5 = Access Control Events (sự kiện kiểm soát ra/vào).	5
        minor:
            Mã loại sự kiện nhỏ. 75 = Face/Fingerprint/Card Verified (chấm công thành công).	75
        startTime:
            Thời gian bắt đầu tìm kiếm (ISO 8601 + múi giờ).	"2025-08-01T00:00:00+07:00"
        endTime:
            Thời gian kết thúc tìm kiếm (ISO 8601 + múi giờ).	"2025-08-01T23:59:59+07:00"

        # response data:
        [
            {'major': 5, 'minor': 75, 'time': '2025-08-01T09:27:57+08:00', 'cardType': 1, 'name': 'quannm',
             'cardReaderNo': 1, 'doorNo': 1, 'employeeNoString': '3', 'serialNo': 132, 'userType': 'normal',
             'currentVerifyMode': 'faceOrFpOrCardOrPw', 'mask': 'no',
             'pictureURL': 'http://192.168.0.40/LOCALS/pic/acsLinkCap/202508_00/01_012757_30075_0.jpeg@WEB000000000009',
             'FaceRect': {'height': 0.336, 'width': 0.19, 'x': 0.391, 'y': 0.644}
             }
        ]
        """

        url = f"http://{device_ip}/ISAPI/AccessControl/AcsEvent?format=json"
        all_results = []

        # Lấy danh sách minor cho thiết bị, nếu không có thì báo lỗi
        minors = DeviceIntegrate.DEVICE_MINOR_CODES.get(device_ip)
        if not minors:
            print(f"[ERROR] Không tìm thấy cấu hình minor cho thiết bị {device_ip}")
            return []

        for minor in minors:
            print(f"📌 Đang lấy dữ liệu cho minor={minor}")
            position = 0
            max_results = 50

            while True:
                payload = {
                    "AcsEventCond": {
                        "searchID": "1",
                        "searchResultPosition": position,
                        "maxResults": max_results,
                        "major": 5,
                        "minor": minor,
                        "startTime": f"{date}T00:00:00+07:00",
                        "endTime": f"{date}T23:59:59+07:00"
                    }
                }
                res = requests.post(
                    url,
                    json=payload,
                    auth=HTTPDigestAuth(username, password),
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )

                if res.status_code != 200:
                    print("Error:", res.status_code, res.text)
                    break

                data = res.json()
                events = data.get("AcsEvent", {}).get("InfoList", [])

                if not events:
                    break  # Không còn dữ liệu

                all_results.extend(events)
                print(f"Lấy được {len(events)} bản ghi từ offset {position}")

                # Nếu số bản ghi trả về < max_results → hết dữ liệu
                if len(events) < max_results:
                    break

                position += max_results  # Sang trang tiếp theo

        return all_results
