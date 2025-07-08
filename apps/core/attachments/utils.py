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


def check_folder_perm(lst, url_type, crt_emp, folder_perm_check):
    folder = DisperseModel(app_model='attachments.Folder').get_model()
    folder_lst = folder.objects.filter(id__in=lst)
    group_id = str(crt_emp.group.id) if hasattr(crt_emp, 'group') else None

    employee_filter = Q(employee_list__icontains=f'"{str(crt_emp.id)}"') & Q(
        folder_perm_list__contains=folder_perm_check
    ) & Q(employee_or_group=True)
    group_filter = Q(group_list__icontains=f'"{group_id}"') & Q(
        folder_perm_list__contains=folder_perm_check
    ) & Q(employee_or_group=False) if group_id else Q()

    fol_check = folder_lst.filter(is_owner=True, employee_inherit=crt_emp).values_list('id', flat=True)
    is_check = [str(val) for val in fol_check] == lst
    if is_check:
        return True

    if url_type in ['my_shared', 'None']:
        is_check = True

        for fol in folder_lst:
            perm = fol.folder_permission_folder.all()
            accessible_folder_ids = perm.filter(
                employee_filter | group_filter
            )
            if accessible_folder_ids.exists() is False:
                is_check = False
                break
        if is_check is False and url_type == 'None':
            uuid_lst = folder_lst.filter(Q(is_admin=True) | Q(is_system=True)).values_list('id', flat=True).distinct()
            is_check = [str(item) for item in uuid_lst] == lst
    else:
        # case là admin thêm xóa sửa folder
        fol_check = folder_lst.filter(is_admin=True, empployee_inherit=crt_emp).values_list('id', flat=True)
        is_check = [str(item) for item in fol_check] == lst
    if is_check:
        return True
    return False


def check_file_perm(lst, url_type, crt_empl):
    files = DisperseModel(app_model='attachments.Files').get_model()
    files_lst = files.objects.filter(id__in=lst)
    if url_type == 'my_space':
        # case 1: nếu file chưa approved và hiển thị trong my space
        is_check = files_lst.filter(is_approved=False, employee_created=crt_empl).count() == len(lst)
    else:
        # case 2: file dc chia sẻ và chưa approved và
        # kiểm tra xem employee có trong file_permission và employee có quyền delete ko
        # adhoc case: file của chủ sở hữu nhưng ko nằm trong my space (tạm thời ko cho xóa)
        is_check = True
        group_id = str(crt_empl.group.id) if hasattr(crt_empl, 'group') else None

        employee_filter = Q(employee_list__icontains=f'"{str(crt_empl.id)}"') & Q(file_perm_list__contains=[7]) & Q(
            is_approved=False
        ) & Q(employee_or_group=True)
        group_filter = Q(group_list__icontains=f'"{group_id}"') & Q(
            file_in_perm_list__contains=[7]
        ) & Q(is_approved=False) & Q(employee_or_group=False) if group_id else Q()

        for file in files_lst:
            perm_file = file.file_permission_file.all()
            accessible_file_ids = perm_file.filter(employee_filter | group_filter)
            if accessible_file_ids.exists() is False:
                is_check = False
                break
    if is_check:
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
        if str(crt_employee.id) in list({str(instance_owner.id), str(obj_r.employee_created.id)}):
            return True
    print('Delete Permission folder error:    core > attachments > utils')
    logger.error(msg='Delete Permission folder error')
    return False


def check_create_sub_folder(parent_n_id, crt_employee):
    # logic check
    # - get folder -> get list permission
    # - if any record in permission list has the permission, then the transmitted "current user" parameter will have
    # permission "create sub folder"
    folder_md = DisperseModel(app_model='attachments.Folder').get_model()
    folder_lst = folder_md.objects.filter(id=parent_n_id)
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
