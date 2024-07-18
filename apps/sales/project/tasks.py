import json
import ast
from uuid import UUID

from celery import shared_task

from apps.shared import DisperseModel, FORMATTING


def get_group(group_lst):
    group = []
    for item in group_lst:
        group.append(
            {
                "id": str(item.group.id),
                "title": item.group.title,
                "date_from": FORMATTING.parse_datetime(item.group.gr_start_date),
                "date_end": FORMATTING.parse_datetime(item.group.gr_end_date),
                "order": item.group.order,
                "progress": item.group.gr_rate,
                "weight": item.group.gr_weight
            }
        )
    return group


def get_work_and_expense(work_lst):
    work_map_expense_mds = DisperseModel(app_model='project.WorkMapExpense').get_model()
    get_work_lst = []
    get_expense_lst = {}
    for item in work_lst:
        temp = {
            "id": str(item.work.id),
            "title": item.work.title,
            "work_status": item.work.work_status,
            "date_from": FORMATTING.parse_datetime(item.work.w_start_date),
            "date_end": FORMATTING.parse_datetime(item.work.w_end_date),
            "order": item.work.order,
            "group": "",
            "relationships_type": None,
            "dependencies_parent": "",
            "progress": item.work.w_rate,
            "weight": item.work.w_weight,
            "expense_data": item.work.expense_data,
        }
        group_mw = item.work.project_groupmapwork_work.all()
        if group_mw:
            group_mw = group_mw.first()
            temp['group'] = str(group_mw.group.id)
        if item.work.work_dependencies_type is not None:
            temp['relationships_type'] = item.work.work_dependencies_type
        if item.work.work_dependencies_parent:
            temp['dependencies_parent'] = str(item.work.work_dependencies_parent.id)
        get_work_lst.append(temp)

        list_of_expense = work_map_expense_mds.objects.filter(work=item.work)
        for work in list_of_expense:
            if str(work.work.id) not in get_expense_lst:
                get_expense_lst[str(work.work.id)] = []
            get_expense_lst[str(work.work.id)].append(
                {
                    'id': str(work.id),
                    'title': work.title if not work.is_labor else '',
                    'expense_name': {
                        'id': str(work.expense_name.id),
                        'title': work.expense_name.title,
                    } if work.expense_name else {},
                    'expense_item': {
                        'id': str(work.expense_item.id),
                        'title': work.expense_item.title,
                    },
                    'uom': {
                        'id': str(work.uom.id),
                        'title': work.uom.title,
                        'code': work.uom.code
                    },
                    'quantity': work.quantity,
                    'expense_price': work.expense_price,
                    'tax': {
                        "id": str(work.tax.id),
                        "title": work.tax.title,
                        "rate": work.tax.rate
                    } if work.tax else {},
                    'sub_total': work.sub_total,
                    'sub_total_after_tax': work.sub_total_after_tax,
                    'is_labor': work.is_labor,
                }
            )
    return get_work_lst, get_expense_lst


def get_task_in_work(task_lst):
    get_task_lst = []
    if task_lst.exists():
        for item in task_lst:
            task = item.task
            temp = {
                'id': str(item.id),
                'task': {
                    'id': str(task.id),
                    'title': task.title,
                    'code': task.code
                }if task and hasattr(task, 'id') else {},
                'work': str(item.work.id) if item.work else '',
                'percent': task.percent_completed if task.percent_completed > 0 else 0,
                'assignee': {
                    "id": str(task.employee_inherit_id),
                    "full_name": task.employee_inherit.get_full_name(),
                    "first_name": task.employee_inherit.first_name,
                    "last_name": task.employee_inherit.last_name
                } if task and hasattr(task, 'employee_inherit') else {},
                'work_before': item.work_before,
            }
            get_task_lst.append(temp)
    return get_task_lst


def get_member_and_perm(member_lst):
    member = []
    perm = {}
    for item in member_lst:
        member.append(
            {
                "id": str(item.member.id),
                "first_name": item.member.first_name,
                "last_name": item.member.last_name,
                "full_name": item.member.get_full_name(),
                "email": item.member.email,
                "avatar": item.member.avatar,
                "is_active": item.member.is_active,
            }
        )
        perm[str(item.member.id)] = {
            'id': str(item.id),
            'date_modified': FORMATTING.parse_datetime(item.date_modified),
            'permit_view_this_project': item.permit_view_this_project,
            'permit_add_member': item.permit_add_member,
            'permit_add_gaw': item.permit_add_gaw,
            'permission_by_configured': item.permission_by_configured,
        }
    return member, perm


@shared_task
def create_baseline_data(baseline_id: UUID or str, project_id: UUID or str):
    baseline_mds = DisperseModel(app_model='project.ProjectBaseline').get_model()
    project_mds = DisperseModel(app_model='project.Project').get_model()
    group_mds = DisperseModel(app_model='project.ProjectMapGroup').get_model()
    work_mds = DisperseModel(app_model='project.ProjectMapWork').get_model()
    member_mds = DisperseModel(app_model='project.ProjectMapMember').get_model()
    task_map_work_mds = DisperseModel(app_model='project.ProjectMapTasks').get_model()

    if baseline_mds and project_mds:
        try:
            prj_obj = project_mds.objects.get(id=project_id)
        except project_mds.DoesNotExist:
            return 'PROJECT NOT FOUND: ' + project_id
        try:
            baseline_obj = baseline_mds.objects.get(id=baseline_id)
        except baseline_mds.DoesNotExist:
            return 'BASELINE NOT FOUND: ' + baseline_id

        try:
            prj_data_temp = ast.literal_eval(baseline_obj.project_data)
        except json.JSONDecodeError:
            return 'PARSE_DATA_ERROR'
        del prj_data_temp['groups']
        del prj_data_temp['works']

        # get GROUP list
        group = group_mds.objects.select_related('group').filter(project=prj_obj)
        prj_data_temp['group'] = get_group(group)

        # get WORK list and EXPENSE list map with WORK
        work = work_mds.objects.select_related('work').filter(project=prj_obj)
        prj_data_temp['work'], baseline_obj.work_expense_data = get_work_and_expense(work)
        baseline_obj.project_data = prj_data_temp

        # get TASK list assign for WORK in PROJECT
        proj_map_task_all = task_map_work_mds.objects.select_related('task', 'work').filter(project=prj_obj)
        baseline_obj.work_task_data = get_task_in_work(proj_map_task_all)

        # get EMPLOYEE MEMBER list and PERM of MEMBER in PROJECT
        employee_lst_perm = member_mds.objects.select_related('member').filter(project=prj_obj)
        baseline_obj.member_data, baseline_obj.member_perm_data = get_member_and_perm(employee_lst_perm)

        baseline_obj.baseline_version = baseline_mds.objects.filter(project_related=prj_obj).count()
        baseline_obj.save()
        return 'Success'
    return 'CREATE_BASELINE_ERROR'
