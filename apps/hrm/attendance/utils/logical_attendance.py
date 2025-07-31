from datetime import datetime
from apps.shared import DisperseModel


HOLIDAY = ["2025-04-30", "2025-05-01", "2025-09-02"]


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
                "timestamp": "2025-07-25 08:21:42",
                "event_type": "IN",
                "status": "success"
            },
            {
                "employee_id": "e37c69ca-c5a0-45ff-9c55-dc0bc37b476e",
                "card_number": "00034567",
                "device_id": "HIK-01",
                "device_name": "HIKVISION_GATE1",
                "timestamp": "2025-07-25 18:50:00",
                "event_type": "OUT",
                "status": "success"
            },
            {
                "employee_id": "e37c69ca-c5a0-45ff-9c55-dc0bc37b476e",
                "card_number": "00034567",
                "device_id": "HIK-01",
                "device_name": "HIKVISION_GATE1",
                "timestamp": "2025-07-29 11:29:42",
                "event_type": "IN",
                "status": "success"
            },
            {
                "employee_id": "e37c69ca-c5a0-45ff-9c55-dc0bc37b476e",
                "card_number": "00034567",
                "device_id": "HIK-01",
                "device_name": "HIKVISION_GATE1",
                "timestamp": "2025-07-29 18:28:14",
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
        data_push = {
            'employee_id': employee_id,
            'date': date,
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
                if log['employee_id'] == employee_id and log['timestamp'].startswith(date)
            ]
            for shift_assign in shift_assigns:
                data_push = {}
                shift_check = shift_assign.shift
                if shift_check:
                    data_push.update({
                        'shift_id': shift_check.id,
                    })
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
                        checkin_time, checkout_time = AttendanceHandler.parse_checkin_checkout_grace(
                            shift_check=shift_check,
                            check_type=0,
                        )
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
        if checkin_time and checkout_time:
            keys = ['from', 'to']
            if all(key in checkin_time for key in keys) and all(key in checkout_time for key in keys):
                for log in logs_on_day:
                    is_checkin = False
                    is_checkout = False
                    log_time = datetime.strptime(log['timestamp'], "%Y-%m-%d %H:%M:%S").time()
                    if log['event_type'] == "IN":
                        is_checkin = AttendanceHandler.check_normal_is_checkin(
                            log_time=log_time,
                            checkin_time_from=checkin_time['from'],
                            checkin_time_to=checkin_time['to'],
                        )
                    if log['event_type'] == "OUT":
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
            prev_time = datetime.strptime(check_log['timestamp'], "%Y-%m-%d %H:%M:%S").time()
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
