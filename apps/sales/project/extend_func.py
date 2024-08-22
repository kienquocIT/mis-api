from uuid import uuid4

from apps.core.hr.models import DistributionApplication
from apps.shared import DisperseModel
from .models import ProjectMapTasks, ProjectWorks, ProjectGroups, GroupMapWork, ProjectMapGroup, ProjectMapWork


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
        temp = model_cls.objects.filter(
            project=prj_obj,
            member=employee_current
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
    prj_obj = task['project'] if hasattr(task, 'project') else task
    pj_member_current_user = get_prj_mem_of_crt_user(prj_obj=prj_obj, employee_current=emp_crt)
    if str(prj_obj.employee_inherit_id) == str(emp_id) or pj_member_current_user.permit_add_gaw or (
            pj_member_current_user.permit_add_gaw is False and hasattr(task, 'parent_n') and not hasattr(task, 'id')
    ):
        return True
    return False


def filter_num(num):
    str_num = str(num)
    int_part, dec_part = str_num.split('.')

    # Find the index of the first non-zero digit in the decimal part
    idx = next((i for i, x in enumerate(dec_part) if x != '0'), len(dec_part))

    # Return the number up to the first non-zero digit in the decimal part
    return float(int_part + '.' + dec_part[:idx + 1])


def calc_update_task(task_obj):
    task_map = task_obj.project_projectmaptasks_task.all()
    if task_map.count():
        work = task_map.first().work
        list_task = ProjectMapTasks.objects.filter(work=work)
        if work and list_task:
            # get all task and re-update % complete per work
            total_w = 0
            is_pending = False
            for item in list_task:
                total_w += item.task.percent_completed
                if item.task.task_status.task_kind == 3:
                    is_pending = True

            if total_w > 0:
                work.w_rate = round(total_w / list_task.count(), 1)
                if work.w_rate == 100:
                    work.work_status = 3
                else:
                    work.work_status = 1
                if is_pending:
                    work.work_status = 2
                work.save()
            # calc rate group
            if hasattr(work, 'project_groupmapwork_work'):
                group_map = work.project_groupmapwork_work.all()

                if group_map:
                    group_obj = group_map.first().group
                    list_work = group_obj.works.all()
                    rate_w = 0
                    for work in list_work:
                        rate_w += (work.w_rate / 100) * work.w_weight
                    if rate_w > 0:
                        group_obj.gr_rate = round(rate_w, 1)
                        group_obj.save()


def re_calc_work_group(work):
    list_task = ProjectMapTasks.objects.filter(work=work)
    work.w_rate = 0
    work.work_status = 0
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
        group.gr_rate = 0
        for work_item in list_work:
            rate_w += (work_item.w_rate / 100) * work_item.w_weight
        if rate_w > 0:
            group.gr_rate = round(rate_w, 1)
        group.save()


def group_calc_weight(prj, w_value=0):
    group_lst = prj.project_projectmapgroup_project.all()
    work_lst = prj.project_projectmapwork_project.all()
    weight_not_grp = 0
    for item in work_lst:
        work = item.work.project_groupmapwork_work.all()
        if not work:
            weight_not_grp += item.work.w_weight

    weight_grp = 0
    for item in group_lst:
        weight_grp += item.group.gr_weight
    if weight_not_grp + weight_grp + w_value > 100:
        return False
    if w_value == 0:
        w_value = 100 - (weight_not_grp + weight_grp)
    return w_value


def group_update_weight(prj, w_value, group):
    group_lst = prj.project_projectmapgroup_project.all()
    work_lst = prj.project_projectmapwork_project.all()
    weight_not_grp = 0
    for item in work_lst:
        work = item.work.project_groupmapwork_work.all()
        if not work:
            weight_not_grp += item.work.w_weight

    weight_grp = 0
    for item in group_lst:
        if item.group.id != group.id:
            weight_grp += item.group.gr_weight
    if weight_not_grp + weight_grp + w_value > 100:
        return False
    if w_value == 0:
        w_value = 100 - (weight_not_grp + weight_grp)
    return w_value


def work_calc_weight_h_group(w_value, group, work=None):
    work_lst = group.project_groupmapwork_group.all()
    work_percent = 0
    for item in work_lst:
        if not work or work.id != item.work.id:
            work_percent += item.work.w_weight

    if work_percent + w_value > 100:
        return False
    if w_value == 0 and work_percent != 100:
        w_value = 100 - work_percent
    return w_value


def reorder_work(group=None, prj=None):
    if not group:
        return False
    work_order = group.order + 1

    work_in_group = GroupMapWork.objects.filter(group=group)
    if work_in_group.exists():
        work_order = work_in_group.order_by('work__order').last().work.order + 1

    group_bellow = ProjectMapGroup.objects.filter(project=prj, group__order__gte=work_order)
    work_bellow = ProjectMapWork.objects.filter(project=prj, work__order__gte=work_order)
    merge_lst = []
    for group_obj in group_bellow:
        group_obj.group.order += 1
        merge_lst.append(group_obj.group)
    for work_obj in work_bellow:
        work_obj.work.order += 1
        merge_lst.append(work_obj.work)
    g_update_lst = list(filter(lambda x: hasattr(x, 'gr_weight'), merge_lst))
    w_update_lst = list(filter(lambda x: hasattr(x, 'work_status'), merge_lst))
    ProjectGroups.objects.bulk_update(g_update_lst, fields=['order'])
    ProjectWorks.objects.bulk_update(w_update_lst, fields=['order'])
    return work_order


def calc_rate_project(pro_obj, obj_delete=None):
    # get all group and work and sum total all rate of group and work (exclude work in group)
    group_lst = ProjectMapGroup.objects.filter(project=pro_obj)
    work_lst = ProjectMapWork.objects.filter(project=pro_obj)
    rate_all = 0
    pro_obj.completion_rate = 0
    group_obj = obj_delete.group if hasattr(obj_delete, 'group') else None
    work_obj = obj_delete.work if hasattr(obj_delete, 'work') else None
    for group_m in group_lst:
        group = group_m.group
        if group.gr_rate and group.gr_weight:
            if not group_obj or group_obj.id != group.id:
                rate_all += (group.gr_rate / 100) * group.gr_weight

    for work_m in work_lst:
        work = work_m.work
        bellow_group = work.project_groupmapwork_work.all()
        if not bellow_group.exists():
            if work.w_rate and work.w_weight:
                if not work_obj or work_obj.id != work.id:
                    rate_all += (work.w_rate / 100) * work.w_weight
    if rate_all > 0:
        pro_obj.completion_rate = filter_num(rate_all)
    pro_obj.save()
