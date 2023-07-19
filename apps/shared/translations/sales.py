from django.utils.translation import gettext_lazy as _


class SaleMsg:
    OPPORTUNITY_NOT_EXIST = _('Opportunity does not exist.')
    OPPORTUNITY_CODE_EXIST = _('Opportunity code is exist.')
    QUOTATION_NOT_EXIST = _('Quotation does not exist.')
    SALE_ORDER_NOT_EXIST = _('Sale order does not exist.')
    OPPORTUNITY_QUOTATION_USED = _('Opportunity is already used for quotation')
    OPPORTUNITY_SALE_ORDER_USED = _('Opportunity is already used for sale order')
    OPPORTUNITY_CLOSED = _('Opportunity is closed')
    INDICATOR_ORDER_OUT_OF_RANGE = _('Order is out of range')
