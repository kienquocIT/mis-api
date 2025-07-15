from django.utils.translation import gettext_lazy as _

__all__ = [
    'AttMsg',
]


class AttMsg:
    FILE_SIZE_SHOULD_BE_LESS_THAN_X = _('File size should be less than {}')
    IMAGE_TYPE_SHOULD_BE_IMAGE_TYPE = _('File type should be image type: {}')
    FILE_TYPE_DETECT_DANGER = _('The file has been flagged as a security risk.')
    FILE_NO_DETECT_SIZE = _("The size of the file cannot be determined.")
    FILE_SUM_NOT_RETURN = _("The functionality to check available size is not working.")
    FILE_SUM_EXCEED_LIMIT = _("The file size exceeds the limit.")
    FILE_IS_NOT_IMAGE = _('The file is not images type.')
    WEB_BUILDER_USED_OVER_SIZE = _('This builder function has exhausted the allocated {used_size} license capacity')
    FOLDER_NOT_EXIST = _('Folder does not exist.')
    EMPLOYEE_LIST_NOT_EXIST = _('Employee list does not exist')
    GROUP_LIST_NOT_EXIST = _('Group list does not exist')
    CAPABILITY_NOT_EXIST = _('Capability list does not exist')
    FOLDER_PERMISSION_ERROR = _('Update permission error')
    FOLDER_DELETE_ERROR = _('Delete folder error')
    FILE_DELETE_ERROR = _('Delete file error')
    FOLDER_SYSTEM_ERROR = _('Can not delete system folder')
    FOLDER_PERM_UPDATE_ERROR = _('You do not have permission to update this shared record')
    FOLDER_PERM_CREATE_ERROR = _('You do not have permission to create this shared record')
    FOLDER_PERM_DELETE_ERROR = _('You do not have permission to delete')
    FOLDER_PARENT_ERROR = _('A folder cannot reference itself as a parent')
