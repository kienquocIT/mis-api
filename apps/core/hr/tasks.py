__all__ = [
    'sync_plan_app_employee',
    'uninstall_plan_app_employee',
]

from celery import shared_task
from django.conf import settings

from apps.core.hr.models import Employee
from apps.core.hr.models.utils import PlanAppDistributionController


@shared_task
def sync_plan_app_employee(employee_ids: list[str]):
    state_false = False
    result = []
    for employee_id in employee_ids:
        try:
            employee_obj = Employee.objects.get(pk=employee_id)
            sync_state = PlanAppDistributionController(
                employee_obj=employee_obj,
            ).sync_all()
            result.append(
                {
                    'employee_id': str(employee_id),
                    'sync_state': sync_state,
                }
            )
        except Exception as errs:
            # get exception at here because should continue sync data of behind it
            state_false = True
            result.append(
                {
                    'employee_id': str(employee_id),
                    'sync_state': 'ERR',
                    'errs': str(errs)
                }
            )
    if state_false is True:
        # task failure always push notify to telegram
        raise ValueError('Raise exception: ' + str(result))
    return result


@shared_task
def uninstall_plan_app_employee(employee_id: str, tenant_id: str, company_id: str):
    return PlanAppDistributionController.uninstall_all(
        employee_id=employee_id, tenant_id=tenant_id, company_id=company_id,
    )
