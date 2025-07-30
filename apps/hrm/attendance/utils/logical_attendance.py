from datetime import datetime, timedelta, time
from apps.shared import DisperseModel


class AttendanceHandler:
    @classmethod
    def check_attendance(cls, employee_id, date):
        data_logs = [
            {
                "employee_id": "e37c69ca-c5a0-45ff-9c55-dc0bc37b476e",
                "card_number": "00034567",
                "device_id": "HIK-01",
                "device_name": "HIKVISION_GATE1",
                "timestamp": "2025-07-25 08:15:42",
                "event_type": "IN",
                "status": "success"
            },
            {
                "employee_id": "e37c69ca-c5a0-45ff-9c55-dc0bc37b476e",
                "card_number": "00034567",
                "device_id": "HIK-01",
                "device_name": "HIKVISION_GATE1",
                "timestamp": "2025-07-25 17:25:14",
                "event_type": "OUT",
                "status": "success"
            },
            {
                "employee_id": "e37c69ca-c5a0-45ff-9c55-dc0bc37b476e",
                "card_number": "00034567",
                "device_id": "HIK-01",
                "device_name": "HIKVISION_GATE1",
                "timestamp": "2025-07-29 12:59:42",
                "event_type": "IN",
                "status": "success"
            },
            {
                "employee_id": "e37c69ca-c5a0-45ff-9c55-dc0bc37b476e",
                "card_number": "00034567",
                "device_id": "HIK-01",
                "device_name": "HIKVISION_GATE1",
                "timestamp": "2025-07-29 17:28:14",
                "event_type": "OUT",
                "status": "success"
            },
            {
                "employee_id": "e37c69ca-c5a0-45ff-9c55-dc0bc37b476e",
                "card_number": "00034567",
                "device_id": "HIK-01",
                "device_name": "HIKVISION_GATE1",
                "timestamp": "2025-07-30 08:28:15",
                "event_type": "IN",
                "status": "success"
            },
            {
                "employee_id": "e37c69ca-c5a0-45ff-9c55-dc0bc37b476e",
                "card_number": "00034567",
                "device_id": "HIK-01",
                "device_name": "HIKVISION_GATE1",
                "timestamp": "2025-07-30 08:29:15",
                "event_type": "IN",
                "status": "success"
            },
            {
                "employee_id": "e37c69ca-c5a0-45ff-9c55-dc0bc37b476e",
                "card_number": "00034567",
                "device_id": "HIK-01",
                "device_name": "HIKVISION_GATE1",
                "timestamp": "2025-07-30 17:28:22",
                "event_type": "OUT",
                "status": "success"
            },
            {
                "employee_id": "e37c69ca-c5a0-45ff-9c55-dc0bc37b476e",
                "card_number": "00034567",
                "device_id": "HIK-01",
                "device_name": "HIKVISION_GATE1",
                "timestamp": "2025-07-30 17:30:22",
                "event_type": "OUT",
                "status": "success"
            }
        ]
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
                    employee_id=employee_id,
                    data_logs=data_logs,
                    leaves=leaves,
                    businesses=businesses,
                    shift_assigns=shift_assigns
                )
        return []

    @classmethod
    def active_check(cls, date, employee_id, data_logs, leaves, businesses, shift_assigns):
        data_push_list = []
        if not shift_assigns:
            print(f"[{date}] Không có ca áp dụng")
            return True
        if shift_assigns:
            # Lọc logs theo ngày và employee_id
            logs_on_day = [
                log for log in data_logs
                if log['employee_id'] == employee_id and log['timestamp'].startswith(date)
            ]
            for shift_assign in shift_assigns:
                data_push = {}
                shift_check = shift_assign.shift
                if shift_check:
                    checkin_time, checkout_time = AttendanceHandler.parse_checkin_checkout(
                        shift_check=shift_check,
                        check_type=0,
                    )

                    data_push = {
                        'employee_id': employee_id,
                        'date': date,
                        'shift_id': shift_check.id,
                    }
                    # Kiểm tra nghỉ phép
                    if leaves:
                        data_push = AttendanceHandler.run_check_leave(
                            date=date,
                            logs_on_day=logs_on_day,
                            leaves=leaves,
                            shift_check=shift_check
                        )
                    # Kiểm tra công tác
                    if businesses:
                        data_push = AttendanceHandler.run_check_business(
                            date=date,
                            businesses=businesses
                        )
                    if not leaves and not businesses:
                        data_push = AttendanceHandler.run_check_normal(
                            date=date,
                            logs_on_day=logs_on_day,
                            checkin_time=checkin_time,
                            checkout_time=checkout_time
                        )
                if data_push:
                    data_push_list.append(data_push)
        return data_push_list

    @classmethod
    def run_check_normal(cls, date, logs_on_day, checkin_time, checkout_time):
        checkin_log = None
        checkout_log = None
        for log in logs_on_day:
            log_time = datetime.strptime(log['timestamp'], "%Y-%m-%d %H:%M:%S").time()
            if log['event_type'] == "IN" and log_time <= checkin_time:
                if checkin_log is None:
                    checkin_log = log
                else:
                    prev_time = datetime.strptime(checkin_log['timestamp'], "%Y-%m-%d %H:%M:%S").time()
                    if log_time > prev_time:
                        checkin_log = log
            if log['event_type'] == "OUT" and log_time >= checkout_time:
                if checkout_log is None:
                    checkout_log = log
                else:
                    prev_time = datetime.strptime(checkout_log['timestamp'], "%Y-%m-%d %H:%M:%S").time()
                    if log_time < prev_time:
                        checkout_log = log
        return AttendanceHandler.check_normal(
            date=date,
            checkin_log=checkin_log,
            checkout_log=checkout_log
        )

    @classmethod
    def check_normal(cls, date, checkin_log, checkout_log):
        data_push = {}
        if checkin_log:
            data_push.update({
                'is_checkin': True,
                'checkin_time': checkin_log['timestamp'],
            })
            print(f"[{date}] Check-in OK: {checkin_log['timestamp']}")
        else:
            print(f"[{date}] ❌ Không có check-in đúng giờ")

        if checkout_log:
            data_push.update({
                'is_checkout': True,
                'checkout_time': checkout_log['timestamp'],
            })
            print(f"[{date}] Check-out OK: {checkout_log['timestamp']}")
        else:
            print(f"[{date}] ❌ Không có check-out đúng giờ")

        if checkin_log and checkout_log:
            data_push.update({
                'status_attendance': 1,
            })
            print(f"[{date}] Present")
        else:
            data_push.update({
                'status_attendance': 0,
            })
            print(f"[{date}] Absent")
        return data_push

    @classmethod
    def run_check_leave(cls, date, logs_on_day, leaves, shift_check):
        data_push = {}
        for leave in leaves:
            if leave.subtotal >= 1:
                data_push.update({
                    'status_attendance': 2,
                    'leave_id': leave.id,
                    'leave_data': {
                        'id': str(leave.id),
                        'title': str(leave.title),
                        'code': str(leave.code),
                        'date_from': str(leave.date_from),
                        'date_to': str(leave.date_to),
                        'total_day': leave.subtotal,
                    },
                })
                print(f"[{date}] Leave")
            if leave.subtotal == 0.5:
                if leave.morning_shift_f is True and leave.morning_shift_t is True:
                    checkin_time, checkout_time = AttendanceHandler.parse_checkin_checkout(
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
                    checkin_time, checkout_time = AttendanceHandler.parse_checkin_checkout(
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
        return data_push

    @classmethod
    def run_check_business(cls, date, businesses):
        data_push = {}
        for business in businesses:
            if business.total_day >= 1:
                data_push.update({
                    'status_attendance': 3,
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

    @classmethod
    def parse_checkin_checkout(cls, shift_check, check_type, is_first_shift=False, is_second_shift=False):
        checkin_time = None
        checkout_time = None
        if check_type == 0:
            checkin_time = (
                    datetime.combine(
                        datetime.today(), shift_check.checkin_time
                    ) + timedelta(minutes=shift_check.checkin_threshold)
            ).time()
            checkout_time = (
                    datetime.combine(
                        datetime.today(), shift_check.checkout_time
                    ) - timedelta(minutes=shift_check.checkout_threshold)
            ).time()
        if check_type == 1:
            if is_first_shift is True:
                checkin_time = (
                        datetime.combine(
                            datetime.today(), shift_check.break_out_time
                        ) + timedelta(minutes=shift_check.break_out_threshold)
                ).time()
                checkout_time = (
                        datetime.combine(
                            datetime.today(), shift_check.checkout_time
                        ) - timedelta(minutes=shift_check.checkout_threshold)
                ).time()
            if is_second_shift is True:
                checkin_time = (
                        datetime.combine(
                            datetime.today(), shift_check.checkin_time
                        ) + timedelta(minutes=shift_check.checkin_threshold)
                ).time()
                checkout_time = (
                        datetime.combine(
                            datetime.today(), shift_check.break_in_time
                        ) - timedelta(minutes=shift_check.break_in_threshold)
                ).time()
        return checkin_time, checkout_time
