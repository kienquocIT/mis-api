from celery import shared_task

from apps.shared import TypeCheck, DisperseModel

__all__ = ['reset_cache_employee_n_group']


# Cache:
#   1. Chi tiet nhan vien (groups, groups my manager)
#   2. Chi tiet group (nhan vien of group)
# Thay doi manager:
#   1. Reset cache nhan vien manager cu
#   2. Reset cache nhan vien manager moi
#   3. Reset cache group
# sample cache:
#   hr.employee.id : {"group: "ID", "groups_my_manager": [...]}
#   hr.group.id : {"employees": [...]}


def reset_cache_employee(employee_id, cls_model=None) -> bool:
    """
    Reset cache by force_cache from object model
    """
    if employee_id and TypeCheck.check_uuid(employee_id):
        if not cls_model:
            cls_model = DisperseModel(app_model='hr.employee').get_model()
        if cls_model and hasattr(cls_model, 'objects'):
            try:
                obj = cls_model.objects.get(pk=employee_id)
                obj.force_cache()
                return True
            except cls_model.DoesNotExist:
                pass
    return False


def reset_cache_group(group_id, cls_model=None):
    """
    Reset cache by force_cache from object model
    """
    if group_id and TypeCheck.check_uuid(group_id):
        if not cls_model:
            cls_model = DisperseModel(app_model='hr.group').get_model()
        if cls_model and hasattr(cls_model, 'objects'):
            try:
                obj = cls_model.objects.get(pk=group_id)
                obj.force_cache()
                return True
            except cls_model.DoesNotExist:
                pass
    return False


@shared_task
def reset_cache_employee_n_group(employee_id_list, group_id_list):
    """
    Support one task call any reset cache of employee and group
    """
    result = {
        'in': {'employee': employee_id_list, 'group': group_id_list},
        'out': {'employee': {}, 'group': {}},
    }
    cls_employee_model = DisperseModel(app_model='hr.employee').get_model()
    if cls_employee_model and hasattr(cls_employee_model, 'objects'):
        for employee_id in employee_id_list:
            result['out']['employee'][employee_id] = reset_cache_employee(employee_id, cls_model=cls_employee_model)

    cls_group_model = DisperseModel(app_model='hr.group').get_model()
    if cls_group_model and hasattr(cls_group_model, 'objects'):
        for group_id in group_id_list:
            result['out']['group'][group_id] = reset_cache_group(group_id, cls_model=cls_group_model)
    return result
