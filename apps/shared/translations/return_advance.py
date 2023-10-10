from django.utils.translation import gettext_lazy as _


class ReturnAdvanceMsg:
    NOT_MAP_AP = _('Not map with Advance Payment')
    GREATER_THAN_ZERO = _('must be greater than zero')
    RETURN_GREATER_THAN_REMAIN = _('must be less than or by remain ')
    ADVANCE_PAYMENT_NOT_EXIST = _('Advance Payment does not exist')
