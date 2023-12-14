from django.utils.translation import gettext_lazy as _


class AdvancePaymentMsg:
    TYPE_ERROR = _('Type is not valid.')
    SALE_CODE_TYPE_ERROR = _('Sale code type is not valid.')
    SALE_CODE_NOT_EXIST = _('Sale code is not exist.')
    SALE_CODE_IS_NOT_NULL = _('Sale code is not null.')
    STATUS_ERROR = _('Status is not valid.')
    SUPPLIER_IS_NOT_NULL = _('Supplier employee is not null.')
    EMPLOYEE_IS_NOT_NULL = _('Payment employee is not null.')
    ROW_ERROR = _('Sum value != Real value + Converted value.')
