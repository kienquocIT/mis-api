from django.utils.translation import gettext_lazy as _


class HRMMsg:
    EMPLOYEE_MAPPED = _('Employee has mapped, please choice another user.')
    RUNTIME_CONTRACT_FIELD_ERROR = _("Contract not found please reload page")
    EMPLOYEE_PERMISSION_DENIED = _('You do not permissions in this contract')

    # shift master data
    FORMAT_ERROR = _('is not in correct format')
    BREAK_IN_TIME_ERROR = _('Break in time must be later than check-in time.')
    BREAK_OUT_TIME_ERROR = _('Break out time must be later than break-in time.')
    CHECKOUT_TIME_ERROR = _('Checkout time must be later than break-out time.')
