from django.db.models import Q

from apps.shared import DisperseModel


def check_folder_perm(lst, url_type, crt_empl):
    Folder = DisperseModel(app_model='attachments.Folder').get_model()
    FolderPermission = DisperseModel(app_model='attachments.FolderPermission').get_model()
    folder_lst = Folder.objects.filter(id__in=lst)
    if url_type == 'my_space':
        is_check = folder_lst.filter(is_owner=True, employee_inherit=crt_empl).count() == len(lst)
    elif url_type == 'my_shared':
        # kiểm tra xem employee có trong folder_permission và employee có quyền delete ko
        group_id = str(crt_empl.group.id) if hasattr(crt_empl, 'group') else None

        employee_filter = Q(employee_list__icontains=f'"{str(crt_empl.id)}"') & Q(folder_perm_list__contains=[5])
        group_filter = Q(group_list__icontains=f'"{group_id}"') & Q(
            file_in_perm_list__contains=[1]
        ) if group_id else Q()

        accessible_folder_ids = FolderPermission.objects.filter(
            employee_filter | group_filter
        ).values_list('folder_id', flat=True).distinct()
        accessible_folder_ids = list(accessible_folder_ids)
        is_check = accessible_folder_ids == lst
    else:
        is_check = folder_lst.filter(is_admin=True, empployee_inherit=crt_empl).count() == len(lst)
    if is_check:
        return True
    return False


def check_file_perm(lst, url_type, crt_empl):
    Files = DisperseModel(app_model='attachments.Files').get_model()
    FilePermission = DisperseModel(app_model='attachments.FilePermission').get_model()
    files_lst = Files.objects.filter(id__in=lst)
    if url_type == 'my_space':
        # case 1: nếu file chưa approved và hiển thị trong my space
        is_check = files_lst.filter(is_approved=False, employee_created=crt_empl).count() == len(lst)
    else:
        # case 2: file dc chia sẻ và chưa approved và
        # kiểm tra xem employee có trong file_permission và employee có quyền delete ko
        # adhoc case: file của chủ sở hữu nhưng ko nằm trong my space (tạm thời ko cho xóa)
        group_id = str(crt_empl.group.id) if hasattr(crt_empl, 'group') else None

        employee_filter = Q(employee_list__icontains=f'"{str(crt_empl.id)}"') & Q(file_perm_list__contains=[7]) & Q(
            is_approved=False
        )
        group_filter = Q(group_list__icontains=f'"{group_id}"') & Q(
            file_in_perm_list__contains=[7]
        ) & Q(is_approved=False) if group_id else Q()

        accessible_file_ids = FilePermission.objects.filter(
            employee_filter | group_filter
        ).values_list('file_id', flat=True).distinct()
        accessible_file_ids = list(accessible_file_ids)
        is_check = accessible_file_ids == lst
    if is_check:
        return True
    return False
