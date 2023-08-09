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
    SALE_ORDER_PRODUCT_NOT_EXIST = _('Sale order product does not exist.')


class SaleTask:
    ERROR_ASSIGNER = _('Assigner not found')
    ERROR_CONFIG_NOT_FOUND = _('Config not found please contact admin')
    ERROR_TEAM_MEMBER_EMPTY = _('Team member is empty')
    ERROR_NOT_IN_MEMBER = _('Assignee not in team member')
    ERROR_NOT_IN_DEPARTMENT = _('Assignee not in department')
    ERROR_1_OR_2_OPT = _('Assignee not in department or not in team member')
    ERROR_NOT_STAFF = _('Assignee is not staff of the assigner')


class PurchaseRequestMsg:
    DOES_NOT_EXIST = _('Object does not exist')
    PR_NOT_NULL = _('Purchase Request must not null.')
    PRODUCT_NOT_NULL = _('Products must not null.')
    GREATER_THAN_ZERO = _('Value must be greater than zero')
    NOT_PURCHASE = _('Has not been configured for purchase')
    NOT_IN_SALE_ORDER = _('Not in Sale Order')
    PURCHASE_REQUEST_NOT_EXIST = _('Purchase request does not exist')
    PURCHASE_REQUEST_IS_ARRAY = _('Purchase request must be array')


class PurchasingMsg:
    PURCHASE_QUOTATION_NOT_EXIST = _('Purchase quotation does not exist')
