from django.utils.translation import gettext_lazy as _


class HRMMsg:
    EMPLOYEE_MAPPED = _('Employee has mapped, please choice another user.')
    RUNTIME_CONTRACT_FIELD_ERROR = _("Contract not found please reload page")
    EMPLOYEE_PERMISSION_DENIED = _('You do not permissions in this contract')
