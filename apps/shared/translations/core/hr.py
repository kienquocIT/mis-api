from django.utils.translation import gettext_lazy as _

__all__ = ['HrMsg']


class HrMsg:
    LICENSE_OVER_TOTAL = _("Licenses used of {} plan is over total licenses.")

    PERMISSIONS_BY_CONFIGURED_DICT_TYPE = _('Permissions type is incorrect.')
    PERMISSIONS_BY_CONFIGURED_CHILD_REQUIRED = _('Permissions item configurations is incorrect.')
    PERMISSIONS_BY_CONFIGURED_OPTION_INCORRECT = _('Permissions item option is incorrect.')
    PERMISSIONS_BY_CONFIGURED_NOT_EXIST = _('Permissions does not exist.')

    EMPLOYEE_NOT_FOUND = _('Employee is not exists')
    EMPLOYEE_REQUIRED = _('Employee must be required')
    EMPLOYEE_WAS_LINKED = _('User still not map with The employee please contact your Admin!')
    EMPLOYEE_SOME_NOT_FOUND = _('Some employee is not available')
