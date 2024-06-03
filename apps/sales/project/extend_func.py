from uuid import uuid4

from apps.core.hr.models import DistributionApplication
from apps.shared import DisperseModel


def pj_get_alias_permit_from_app(employee_obj):
    result = []
    app_id_get = [
        "e66cfb5a-b3ce-4694-a4da-47618f53de4c",  # Task
        "57725469-8b04-428a-a4b0-578091d0e4f5",  # Advanced Payment
        "1010563f-7c94-42f9-ba99-63d5d26a1aca",  # Payment
        "65d36757-557e-4534-87ea-5579709457d7",  # Return Payment
    ]

    for obj in DistributionApplication.objects.select_related('app').filter(  # noqa
            employee=employee_obj, app_id__in=app_id_get
    ):
        permit_has_1_range = []
        permit_has_4_range = []
        for permit_code, permit_config in obj.app.permit_mapping.items():
            if '1' in permit_config.get('range', []):
                permit_has_1_range.append(permit_code)
            elif '4' in permit_config.get('range', []):
                permit_has_4_range.append(permit_code)

        has_1 = False
        data_tmp_for_1 = {
            'id': str(uuid4()),
            'app_id': str(obj.app_id),
            'view': False,
            'create': False,
            'edit': False,
            'delete': False,
            'range': '1',
            'space': '0',
        }
        has_4 = False
        data_tmp_for_4 = {
            'id': str(uuid4()),
            'app_id': str(obj.app_id),
            'view': False,
            'create': False,
            'edit': False,
            'delete': False,
            'range': '4',
            'space': '0',
        }

        for key in ['view', 'create', 'edit', 'delete']:
            if key in permit_has_1_range:
                has_1 = True
                data_tmp_for_1[key] = True
            elif key in permit_has_4_range:
                has_4 = True
                data_tmp_for_4[key] = True

        if has_1 is True:
            result.append(data_tmp_for_1)
        if has_4 is True:
            result.append(data_tmp_for_4)
    return result


def get_prj_mem_of_crt_user(pj_obj, employee_current):
    crt_user = None
    model_cls = DisperseModel(app_model='project_ProjectMapMember').get_model()
    if model_cls:
        temp = model_cls.objects.filter_current(
            project=pj_obj,
            member=employee_current,
            fill__tenant=True, fill__company=True,
        )
        if temp.exists():
            crt_user = temp.first()
    return crt_user


def check_permit_add_member_pj(task, emp_crt):
    # special case skip with True if current user is employee_inherit
    # check is user create prj
    # or user in team member and have permission
    # or user in team member with do not have permit but create sub-task
    emp_id = emp_crt.id
    pj_obj = task['project']
    pj_member_current_user = get_prj_mem_of_crt_user(pj_obj=pj_obj, employee_current=emp_crt)
    if str(pj_obj.employee_inherit_id) == str(emp_id) or pj_member_current_user.permit_add_gaw or (
            pj_member_current_user.permit_add_gaw is False and hasattr(task, 'parent_n') and not hasattr(
            task, 'id')
    ):
        return True
    return False
