from copy import deepcopy
from datetime import datetime, timedelta
import pytz

from celery import shared_task
from django.conf import settings
from django.utils import timezone

from apps.shared import LEAVE_YEARS_SENIORITY

from apps.core.hr.models import Employee
from .models import LeaveAvailable


@shared_task
def create_new_available_end_year():
    # 12h khuya đầu năm mới sẽ run task
    # loop all employee => lấy ds available theo employee
    # Step 2: từ mỗi ds trên filter ra 'ANPY', check nếu là năm cũ nhất gán năm cũ gần nhất (năm ngoái)cho ANPY này.
    # Step 3: filter ra các loại # nếu hết hạn chuyển qua năm mới và reset về 0
    # step 4: reset 'AN' về 0 và chuyển qua năm mới
    current_date = timezone.now().replace(year=2024, month=1, day=1)
    current_year = current_date.year
    list_update = []
    for employee in Employee.objects.filter(is_active=True, is_delete=False):
        current_list = LeaveAvailable.objects.filter(check_balance=True, employee_inherit=employee)
        past_an = current_list.filter(leave_type__code='AN').first()
        for item in current_list.filter(leave_type__code='ANPY'):  # (step 2)
            if item.open_year == current_year - 3:
                item.open_year = deepcopy(current_year - 2)
                item.total = past_an.total
                item.used = past_an.used
                item.available = past_an.available
                item.expiration_date = datetime.strftime(datetime(deepcopy(current_year - 2), 12, 31), '%Y-%m-%d')
                list_update.append(item)
            else:
                item.open_year = deepcopy(current_year - 3)
                item.expiration_date = datetime.strftime(datetime(deepcopy(current_year - 3), 12, 31), '%Y-%m-%d')
                list_update.append(item)

        for item in current_list.exclude(leave_type__code__in=['ANPY', 'AN']):  # (Step 3)
            expirate_date = pytz.timezone(settings.TIME_ZONE).localize(
                datetime.strptime(item.expiration_date, "%Y-%m-%d")
            )
            if expirate_date <= current_date:
                item.open_year = current_year
                item.total = 0
                item.used = 0
                item.available = 0
                item.expiration_date = datetime.strftime(datetime(current_year, 12, 31), '%Y-%m-%d')
                item.check_balance = past_an.check_balance
                list_update.append(item)
        # setup 4
        past_an.open_year = current_year
        past_an.total = 0
        past_an.used = 0
        past_an.available = 0
        past_an.expiration_date = datetime.strftime(datetime(current_year, 12, 31), '%Y-%m-%d')
        list_update.append(past_an)
    LeaveAvailable.objects.bulk_update(
        list_update, fields=['open_year', 'total', 'used', 'available', 'expiration_date', 'check_balance']
    )
    return {'apps.eoffice.leave.tasks.create_new_available_end_year': 'run task finished!'}


def diff_months_counter(dt_now, dt_begin):
    if dt_now.month > dt_begin.month:
        if dt_now.day >= dt_begin.day:
            return (dt_now.year - dt_begin.year) * 12 + (dt_now.month - dt_begin.month)
        return (dt_now.year - dt_begin.year) * 12 + (dt_now.month - dt_begin.month) - 1
    if dt_now.day >= dt_begin.day:
        return (dt_now.year - dt_begin.year) * 12 - (dt_begin.month - dt_now.month)
    return (dt_now.year - dt_begin.year) * 12 - (dt_begin.month - dt_now.month) - 1


# return number of added days for current month
def leave_months_calc(dt_now, dt_begin):
    # năm thâm niên
    year_senior = (dt_now - dt_begin) // timedelta(days=365)

    # tính ngày added theo thâm niên
    added_days = 1
    for item in LEAVE_YEARS_SENIORITY:
        if item['from_range'] <= year_senior <= item['to_range']:
            added_days = item['added']

    # tính tháng làm việc thực tế
    months = diff_months_counter(dt_now, dt_begin)
    calc = months * (12 + added_days) / 12

    # làm tròn
    number = deepcopy(calc) % 1
    decimal_part = str(number).split(".")
    decimal_part_check = decimal_part[1][0]
    final = 0
    if int(decimal_part_check) >= 6:
        integer_part, decimal_part = str(calc).split(".")
        final = float(int(integer_part) + 1)
    elif int(decimal_part_check) <= 4:
        integer_part, decimal_part = str(calc).split(".")
        final = float(f'{integer_part}.0')
    else:
        integer_part, decimal_part = str(calc).split(".")
        final = float(str(integer_part) + "." + str(5))
    return final


@shared_task
def update_annual_leave_each_month():
    dt_crt = timezone.now()
    crt_moth = dt_crt.month
    new_year = crt_moth <= 1
    for employee in Employee.objects.filter(is_active=True, is_delete=False):
        emp_date_join = employee.date_joined
        if not emp_date_join:
            continue
        crt_added = leave_months_calc(dt_crt, emp_date_join)
        if not new_year:
            minus_1_month = deepcopy(dt_crt.month) - 1
            past_added = leave_months_calc(dt_crt.replace(month=minus_1_month), emp_date_join)
            crt_added -= past_added
        leave = LeaveAvailable.objects.get(employee_inherit=employee, leave_type__code='AN')
        leave.total += crt_added
        leave.available = leave.total - leave.used
        leave.save(update_fields=['total', 'available', 'used'])
    return {'apps.eoffice.leave.tasks.update_annual_leave_each_month': 'run task finished!'}
