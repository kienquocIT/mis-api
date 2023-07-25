from django.utils.translation import gettext_lazy as _


class BaseMsg:
    PLAN_NOT_EXIST = _('Plan does not exist.')
    APPLICATIONS_NOT_EXIST = _('Some applications do not exist.')
    APPLICATION_IS_ARRAY = _('Application must be array.')
    PROPERTY_NOT_EXIST = _('Application property does not exist.')
    USER_NOT_MAP_EMPLOYEE = _('User still not map with The employee please contact your Admin')
    UPLOAD_FILE_ERROR = _('Upload file is failure. Please refresh and try again.')


class PermissionMsg:
    PERMISSION_INCORRECT = _('Permission format is incorrect')
