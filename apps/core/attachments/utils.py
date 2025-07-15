import logging

from django.db.models import Q

from apps.shared import DisperseModel, AttachmentMsg

logger = logging.getLogger(__name__)

# permission cheat
#   (1, 'See'),
#   (2, 'Upload'),
#   (3, 'Download'),
#   (4, 'Create sub folders'),
#   (5, 'Delete'),
#   (6, 'Share'),


# FILE_LIST = (
#     (1, 'Review'),
#     (2, 'Download'),
#     (3, 'Edit file attributes'),
#     (4, 'Share'),
#     (5, 'Upload version'),
#     (6, 'Duplicate'),
#     (7, 'Edit file'),
# )


def check_folder_perm(lst, crt_emp, folder_perm_check):
    # return False
    folder_lst = DisperseModel(app_model='attachments.Folder').get_model().objects.filter(id__in=lst)
    group_id = str(crt_emp.group.id) if hasattr(crt_emp, 'group') else None
    employee_filter = Q(employee_list__icontains=f'"{str(crt_emp.id)}"') & Q(
        folder_perm_list__contains=folder_perm_check
    ) & Q(employee_or_group=True)
    group_filter = Q(group_list__icontains=f'"{group_id}"') & Q(
        folder_perm_list__contains=folder_perm_check
    ) & Q(employee_or_group=False) if group_id else Q()

    #  kiểm tra xem user là owner của folder ko
    owner_ids = set(map(str, folder_lst.filter(is_owner=True, employee_inherit=crt_emp).values_list('id', flat=True)))
    if owner_ids == set(lst):
        return True

    # kiểm tra xem có dc share quyền trong folder ko
    perm_condition = Q(employee_filter) | Q(group_filter)
    has_share_perm = True
    for fol in folder_lst:
        count = fol.folder_permission_folder.all().filter(perm_condition)
        if not count.exists():
            has_share_perm = False
    if has_share_perm:
        return True

    # kt xem có phải là folder admin tạo or folder system ko
    uuid_lst = set(
        map(str, folder_lst.filter(Q(is_admin=True) | Q(is_system=True)).values_list('id', flat=True).distinct())
    )
    if uuid_lst == set(lst):
        return True

    return False


def check_file_perm(lst, crt_emp, permission):
    files_lst = DisperseModel(app_model='attachments.Files').get_model().objects.filter(id__in=lst, is_approved=False)
    group_id = str(crt_emp.group.id) if hasattr(crt_emp, 'group') else None
    employee_filter = Q(employee_list__icontains=f'"{str(crt_emp.id)}"') & Q(
        file_perm_list__contains=permission
    ) & Q(employee_or_group=True)
    group_filter = Q(group_list__icontains=f'"{group_id}"') & Q(
        file_perm_list__contains=permission
    ) & Q(employee_or_group=False) if group_id else Q()

    # case 1: nếu file chưa approved và file thuộc owner
    is_check = set(
        map(str, files_lst.filter(employee_created=crt_emp).values_list('id', flat=True))
    )
    if is_check == set(lst):
        return True

    perm_check = True
    perm_condition = Q(employee_filter) | Q(group_filter)
    for file in files_lst:
        perm_file = file.file_permission_file.all().filter(perm_condition)
        if not perm_file.exists():
            perm_check = False
    if perm_check:
        return True

    return False


def check_perm_delete_access_list(lst, crt_employee, model_type: str = 'folder'):
    # phát biểu ai có quyền xóa các quyền trong thư mục được chia sẻ
    # người tạo record perm đó or owner của file/folder đó
    obj_models = DisperseModel(app_model='attachments.FolderPermission').get_model()
    if model_type != 'folder':
        obj_models = DisperseModel(app_model='attachments.FilePermission').get_model()
    obj = obj_models.objects.filter(id=lst[0])
    if obj.exists():
        obj_r = obj.first()
        if model_type != 'folder':
            instance_owner = obj_r.file.employee_created
        else:
            instance_owner = obj_r.folder.employee_created
        if str(crt_employee.id) in list(str(instance_owner.id), str(obj_r.employee_created.id)):
            return True
    print('Delete Permission folder error: core > attachments > utils')
    logger.error(msg='Delete Permission folder error')
    return False


def check_create_sub_folder(parent_n_id, crt_employee):
    # logic check
    # - get folder -> get list permission
    # - if any record in permission list has the permission, then the transmitted "current user" parameter will have
    # permission "create sub folder"
    folder_lst = DisperseModel(app_model='attachments.Folder').get_model().objects.filter(id=parent_n_id)
    employee_group = crt_employee.group
    if folder_lst.exists():
        folder = folder_lst.first()
        perm_lst = folder.folder_permission_folder.all()
        employee_filter = Q(employee_list__icontains=f'"{str(crt_employee.id)}"') & Q(folder_perm_list__contains=4)
        emp_lst = perm_lst.filter(employee_filter)
        folder_owner = folder.employee_inherit == crt_employee
        if emp_lst.exists() or folder_owner:
            return True
        if employee_group:
            g_filter = Q(group_list__contains=f'"{str(employee_group.id)}"') & Q(folder_perm_list__contains=4)
            group_lst = perm_lst.filter(g_filter)
            if group_lst.exists():
                return True
        return False
    raise ValueError(AttachmentMsg.PARENT_NOT_EXISTS)
