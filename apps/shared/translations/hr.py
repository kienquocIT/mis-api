from django.utils.translation import gettext_lazy as _


class HRMsg:
    GROUP_LEVEL_NOT_EXIST = _('Group level does not exist.')
    GROUP_CODE_EXIST = _('Group code is exist.')
    GROUP_NOT_EXIST = _('Group does not exist.')
    ROLES_NOT_EXIST = _('Some roles do not exist.')
    ROLE_IS_ARRAY = _('Role must be array.')
    EMPLOYEE_PLAN_APP_CHECK = _('Licenses used of "{}" plan is over total licenses.')
    EMPLOYEE_NOT_EXIST = _('Employee does not exist.')
    EMPLOYEES_NOT_EXIST = _('Employees do not exist.')
    EMPLOYEE_IS_ARRAY = _('Employee must be array.')
    ROLE_CODE_EXIST = _('Role code is exist.')
    ROLE_DATA_VALID = _('Data is not valid')

    PERMISSIONS_BY_CONFIGURED_INCORRECT = _("Permissions is incorrect.")
    PERMISSIONS_BY_CONFIGURED_CHILD_INCORRECT = _("Permission item is incorrect.")

    FILTER_COMPANY_ID_REQUIRED = _('The data must be filter by company.')
