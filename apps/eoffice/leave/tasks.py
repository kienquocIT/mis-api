from copy import deepcopy
from datetime import datetime, timedelta
import pytz
from dateutil.relativedelta import relativedelta

from celery import shared_task
from django.conf import settings
from django.utils import timezone

from apps.shared import LEAVE_YEARS_SENIORITY

from apps.core.hr.models import Employee
from apps.core.company.models import Company
from .models import LeaveAvailable, LeaveType, LeaveAvailableHistory


@shared_task
def create_new_available_end_year():
    # 12h khuya đầu năm mới sẽ run task
    # loop all employee => lấy ds available theo employee
    # Step 2: từ mỗi ds trên filter ra 'ANPY', check nếu là năm cũ nhất gán năm cũ gần nhất (năm ngoái)cho ANPY này.
    # Step 3: filter ra các loại # nếu hết hạn chuyển qua năm mới và reset về 0
    # step 4: reset 'AN' về 0 và chuyển qua năm mới
    current_date = timezone.now()
    current_year = current_date.year
    list_update = []
    for company in Company.objects.all():
        anpy_config = LeaveType.objects.get(company=company, code='ANPY')
        for employee in Employee.objects.filter(is_active=True, is_delete=False, company=company):
            current_list = LeaveAvailable.objects.filter(check_balance=True, employee_inherit=employee)
            past_an = current_list.filter(leave_type__code='AN').first()
            for item in current_list.filter(leave_type__code='ANPY'):  # (step 2)
                if item.open_year == current_year - 3:
                    item.open_year = deepcopy(current_year) - 1
                    item.total = past_an.total
                    item.used = past_an.used
                    item.available = past_an.available
                    date_current = timezone.now().replace(year=item.open_year, month=12, day=31)
                    item.expiration_date = datetime.strftime(
                        date_current + relativedelta(months=anpy_config.prev_year), '%Y-%m-%d'
                    )
                    list_update.append(item)
                else:
                    item.open_year = deepcopy(current_year) - 2
                    date_current = timezone.now().replace(year=item.open_year, month=12, day=31)
                    item.expiration_date = datetime.strftime(
                        date_current + relativedelta(months=anpy_config.prev_year), '%Y-%m-%d'
                    )
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
def leave_months_calc(dt_now, dt_begin, an_number):
    # năm thâm niên
    year_senior = (dt_now - dt_begin) // timedelta(days=365)

    # tính ngày added theo thâm niên
    added_days = 1
    for item in LEAVE_YEARS_SENIORITY:
        if item['from_range'] <= year_senior <= item['to_range']:
            added_days = item['added']

    # tính tháng làm việc thực tế
    months = diff_months_counter(dt_now, dt_begin)
    calc = months * (an_number + added_days) / an_number

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


def update_history(leave, total, quantity):
    LeaveAvailableHistory.objects.create(
        employee_inherit=leave.employee_inherit,
        tenant=leave.tenant,
        company=leave.company,
        leave_available=leave,
        total=total,
        action=1,
        quantity=quantity,
        adjusted_total=total + quantity,
        type_arises=3
    )


@shared_task
def update_annual_leave_each_month():
    dt_crt = timezone.now()
    crt_moth = dt_crt.month
    new_year = crt_moth <= 1
    for company in Company.objects.all():
        an_config = LeaveType.objects.get(company=company, code='AN')
        for employee in Employee.objects.filter(is_active=True, is_delete=False, company=company):
            emp_date_join = employee.date_joined
            if not emp_date_join:
                continue
            crt_added = leave_months_calc(dt_crt, emp_date_join, an_config.no_of_paid)
            if not new_year:
                minus_1_month = deepcopy(dt_crt.month) - 1
                past_added = leave_months_calc(dt_crt.replace(month=minus_1_month), emp_date_join, an_config.no_of_paid)
                crt_added -= past_added
            leave = LeaveAvailable.objects.get(employee_inherit=employee, leave_type__code='AN')
            clone_total = deepcopy(leave.total)
            leave.total += crt_added
            leave.available = leave.total - leave.used
            leave.save(update_fields=['total', 'available', 'used'])
            update_history(leave, clone_total, crt_added)
    return {'apps.eoffice.leave.tasks.update_annual_leave_each_month': 'run task finished!'}
