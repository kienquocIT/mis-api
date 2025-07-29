from datetime import datetime
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
                "timestamp": "2025-07-24 08:19:42",
                "event_type": "IN",
                "status": "success"
            },
            {
                "employee_id": "e37c69ca-c5a0-45ff-9c55-dc0bc37b476e",
                "card_number": "00034567",
                "device_id": "HIK-01",
                "device_name": "HIKVISION_GATE1",
                "timestamp": "2025-07-24 17:48:14",
                "event_type": "OUT",
                "status": "success"
            },
            {
                "employee_id": "e37c69ca-c5a0-45ff-9c55-dc0bc37b476e",
                "card_number": "00034567",
                "device_id": "HIK-01",
                "device_name": "HIKVISION_GATE1",
                "timestamp": "2025-07-29 13:55:15",
                "event_type": "IN",
                "status": "success"
            },
            {
                "employee_id": "e37c69ca-c5a0-45ff-9c55-dc0bc37b476e",
                "card_number": "00034567",
                "device_id": "HIK-01",
                "device_name": "HIKVISION_GATE1",
                "timestamp": "2025-07-29 13:58:15",
                "event_type": "IN",
                "status": "success"
            },
            {
                "employee_id": "e37c69ca-c5a0-45ff-9c55-dc0bc37b476e",
                "card_number": "00034567",
                "device_id": "HIK-01",
                "device_name": "HIKVISION_GATE1",
                "timestamp": "2025-07-29 17:28:22",
                "event_type": "OUT",
                "status": "success"
            },
            {
                "employee_id": "e37c69ca-c5a0-45ff-9c55-dc0bc37b476e",
                "card_number": "00034567",
                "device_id": "HIK-01",
                "device_name": "HIKVISION_GATE1",
                "timestamp": "2025-07-29 17:29:22",
                "event_type": "OUT",
                "status": "success"
            }
        ]
        data_push_list = []
        model_employee = DisperseModel(app_model='hr.Employee').get_model()
        if model_employee and hasattr(model_employee, 'objects'):
            employee_obj = model_employee.objects.filter_on_company(id=employee_id).first()
            if employee_obj:
                leaves = employee_obj.leave_leaverequestdatelistregister_employee_inherit.filter_on_company(
                    date_from__lte=date, date_to__gte=date, leave__system_status=3
                )
                shift_assigns = employee_obj.shift_assignment_employee.filter_on_company(date=date)
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
                            checkin_time = shift_check.checkin_time
                            checkout_time = shift_check.checkout_time

                            data_push = {
                                'employee_id': employee_id,
                                'date': date,
                                'shift_id': shift_check.id,
                            }
                            # Kiểm tra nghỉ phép
                            if leaves:
                                data_push = AttendanceHandler.check_leave(
                                    date=date,
                                    logs_on_day=logs_on_day,
                                    leaves=leaves,
                                    shift_check=shift_check
                                )
                            if not leaves:
                                data_push = AttendanceHandler.check_base(
                                    date=date,
                                    logs_on_day=logs_on_day,
                                    checkin_time=checkin_time,
                                    checkout_time=checkout_time
                                )
                        if data_push:
                            data_push_list.append(data_push)
        return str(data_push_list)

    @classmethod
    def check_leave(cls, date, logs_on_day, leaves, shift_check):
        data_push = {}
        for leave in leaves:
            if leave.subtotal >= 1:
                data_push.update({
                    'status_attendance': 1,
                })
            if leave.subtotal == 0.5:
                if leave.morning_shift_f is True and leave.morning_shift_t is True:
                    checkin_time = shift_check.break_out_time
                    checkout_time = shift_check.checkout_time
                    data_push = AttendanceHandler.check_base(
                        date=date,
                        logs_on_day=logs_on_day,
                        checkin_time=checkin_time,
                        checkout_time=checkout_time
                    )
                if leave.morning_shift_f is False and leave.morning_shift_t is False:
                    checkin_time = shift_check.break_out_time
                    checkout_time = shift_check.break_in_time
                    data_push = AttendanceHandler.check_base(
                        date=date,
                        logs_on_day=logs_on_day,
                        checkin_time=checkin_time,
                        checkout_time=checkout_time
                    )
        return data_push

    @classmethod
    def check_base(cls, date, logs_on_day, checkin_time, checkout_time):
        data_push = {}
        checkin_log = None
        checkout_log = None
        for log in logs_on_day:
            log_time = datetime.strptime(log['timestamp'], "%Y-%m-%d %H:%M:%S").time()
            if log['event_type'] == "IN" and log_time <= checkin_time:
                if checkin_log is None or log_time > datetime.strptime(checkin_log['timestamp'],
                                                                       "%Y-%m-%d %H:%M:%S").time():
                    checkin_log = log
            if log['event_type'] == "OUT" and log_time >= checkout_time:
                if checkout_log is None or log_time < datetime.strptime(checkout_log['timestamp'],
                                                                        "%Y-%m-%d %H:%M:%S").time():
                    checkout_log = log

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
