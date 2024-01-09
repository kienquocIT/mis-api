from copy import deepcopy
from datetime import date, timedelta
from uuid import uuid4
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from .models import LeaveType, LeaveAvailable


def leave_available_map_employee(employee, company_obj):
    try:
        list_avai = []
        current_date = timezone.now()
        anpy_config = LeaveType.objects.get(company=company_obj, code='ANPY')

        leave_type = LeaveType.objects.filter(company=company_obj)
        for l_type in leave_type:
            if l_type.code == 'AN' or l_type.code != 'ANPY':  # noqa
                total = 0
                if l_type.code in ['FF', 'MY', 'MC']:
                    total = 1 if l_type.code == 'MC' else 3
                list_avai.append(
                    LeaveAvailable(
                        leave_type=l_type,
                        open_year=current_date.year,
                        total=total,
                        used=0,
                        available=0,
                        expiration_date=date(current_date.date().year + 1, 1, 1) - timedelta(days=1),
                        company=company_obj,
                        tenant=company_obj.tenant,
                        employee_inherit=employee,
                        check_balance=l_type.balance_control
                    )
                )
            if l_type.code == 'ANPY':
                prev_current = date(current_date.date().year, 1, 1)
                last_prev_day = prev_current - timedelta(days=1)
                temp = LeaveAvailable(
                    leave_type=l_type,
                    open_year=current_date.year - 1,
                    total=0,
                    used=0,
                    available=0,
                    expiration_date=last_prev_day + relativedelta(months=anpy_config.prev_year),
                    company=company_obj,
                    tenant=company_obj.tenant,
                    employee_inherit=employee,
                    check_balance=l_type.balance_control
                )
                list_avai.append(temp)
                temp2 = deepcopy(temp)
                temp2.id = uuid4()
                temp2.open_year = deepcopy(current_date.year) - 2
                prev_current_2 = date(deepcopy(current_date).date().year - 1, 1, 1)
                last_prev_day = prev_current_2 - timedelta(days=1)
                temp2.expiration_date = last_prev_day + relativedelta(months=anpy_config.prev_year)
                list_avai.append(temp2)
        LeaveAvailable.objects.bulk_create(list_avai)
    except Exception as err:
        print('create available for employee not complete please verify again', err)
