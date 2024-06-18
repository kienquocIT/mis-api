from uuid import uuid4

from apps.core.hr.models import DistributionApplication
from apps.shared import DisperseModel
from .models import ProjectMapTasks


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


def get_prj_mem_of_crt_user(prj_obj, employee_current):
    crt_user = None
    model_cls = DisperseModel(app_model='project_ProjectMapMember').get_model()
    if model_cls:
        temp = model_cls.objects.filter_current(
            project=prj_obj,
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
    prj_obj = task['project']
    pj_member_current_user = get_prj_mem_of_crt_user(prj_obj=prj_obj, employee_current=emp_crt)
    if str(prj_obj.employee_inherit_id) == str(emp_id) or pj_member_current_user.permit_add_gaw or (
            pj_member_current_user.permit_add_gaw is False and hasattr(task, 'parent_n') and not hasattr(
            task, 'id')
    ):
        return True
    return False


def calc_update_task(task_obj):
    if task_obj.project and hasattr(task_obj, 'id'):
        task_map = task_obj.project_projectmaptasks_task.all()
        if task_map.count():
            work = task_map.first().work
            list_task = ProjectMapTasks.objects.filter(work=work)
            if list_task:
                # check percent complete of work by task
                total_w = 0
                for item in list_task:
                    total_w += item.task.percent_completed
                if total_w > 0:
                    work.w_rate = round(total_w / list_task.count(), 1)
                    work.work_status = 1
                    work.save()
                # calc rate group
                if hasattr(work, 'project_groupmapwork_work'):
                    group_map = work.project_groupmapwork_work.all()
                    group = group_map.first().group
                    list_work = group.works.all()
                    rate_w = 0
                    for work in list_work:
                        rate_w += work.w_rate
                    if rate_w > 0:
                        group.gr_rate = round(rate_w / list_work.count(), 1)
                        group.save()


def re_calc_work_group(work):
    list_task = ProjectMapTasks.objects.filter(work=work)
    if list_task:
        total_w = 0
        for item in list_task:
            total_w += item.task.percent_completed
        if total_w > 0:
            work.w_rate = round(total_w / list_task.count(), 1)
            work.work_status = 1
            work.save()
    # calc rate group
    group_map = work.project_groupmapwork_work.all()
    if group_map.exists():
        group = group_map.first().group
        list_work = group.works.all()
        rate_w = 0
        for work_item in list_work:
            rate_w += work_item.w_rate
        if rate_w > 0:
            group.gr_rate = round(rate_w / list_work.count(), 1)
            group.save()
