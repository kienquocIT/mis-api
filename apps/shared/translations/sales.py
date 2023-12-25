from django.utils.translation import gettext_lazy as _


class SaleMsg:
    OPPORTUNITY_NOT_EXIST = _('Opportunity does not exist.')
    OPPORTUNITY_CODE_EXIST = _('Opportunity code is exist.')
    QUOTATION_NOT_EXIST = _('Quotation does not exist.')
    SALE_ORDER_NOT_EXIST = _('Sale order does not exist.')
    OPPORTUNITY_QUOTATION_USED = _('Opportunity is already used for quotation')
    OPPORTUNITY_SALE_ORDER_USED = _('Opportunity is already used for sale order')
    OPPORTUNITY_HAS_SALE_ORDER = _('Opportunity already has sale order')
    OPPORTUNITY_HAS_QUOTATION_NOT_DONE = _('Opportunity has quotation is not finished')
    OPPORTUNITY_CLOSED = _('Opportunity is closed')
    INDICATOR_ORDER_OUT_OF_RANGE = _('Order is out of range')
    SALE_ORDER_PRODUCT_NOT_EXIST = _('Sale order product does not exist.')
    ADVANCE_PAYMENT_NOT_FINISH = _('This advance payment have not finish yet.')
    WRONG_TIME = _('From time must be < To time.')


class SaleTask:
    TITLE_REQUIRED = _('Title is required.')
    STT_REQUIRED = _('Status is required')
    ERROR_ASSIGNER = _('Assigner not found')
    VALID_PARENT_N = _('Can not create another sub-task form sub-task')
    ERROR_COMPLETE_SUB_TASK = _('Please complete Sub-task before')
    ERROR_UPDATE_SUB_TASK = _('Data request is missing please reload and try again.')
    ERROR_LOGTIME_BEFORE_COMPLETE = _('Please Log time before complete task')
    ERROR_TIME_SPENT = _('Time spent is wrong format.')
    ERROR_NOT_PERMISSION = _('You do not permission to log time this task')
    ERROR_NOT_CHANGE = _('You do not permission to change Opportunity or Project')
    ERROR_NOT_LOGWORK = _('You do not permission to change start/end date')
    NOT_CHANGE_ESTIMATE = _('You do not permission to change estimate')
    NOT_CONFIG = _('Missing default info please contact with admin')


class PurchaseRequestMsg:
    DOES_NOT_EXIST = _('Object does not exist')
    PR_NOT_NULL = _('Purchase Request must not null.')
    PRODUCT_NOT_NULL = _('Products must not null.')
    GREATER_THAN_ZERO = _('Value must be greater than zero')
    NOT_PURCHASE = _('Has not been configured for purchase')
    NOT_IN_SALE_ORDER = _('Not in Sale Order')
    PURCHASE_REQUEST_NOT_EXIST = _('Purchase request does not exist')
    PURCHASE_REQUEST_IS_ARRAY = _('Purchase request must be array')
    EMPLOYEE_DOES_NOT_EXIST = _('Employee does not exist')


class PurchasingMsg:
    PURCHASE_QUOTATION_NOT_EXIST = _('Purchase quotation does not exist')
    PURCHASE_ORDER_NOT_EXIST = _('Purchase order does not exist')
    PURCHASE_ORDER_QUANTITY = _('Quantity order must be greater than 0')


class DeliverMsg:
    ERROR_STATE = _('Can not update when status is Done!')
    ERROR_CONFIG = _('Please setup Leader of Picking/Delivery in config page before create request')
    ERROR_ESTIMATED_DATE = _('Estimated Delivery date is required!')
    ERROR_OUT_STOCK = _('out of stock')
    ERROR_QUANTITY = _('Done quantity not equal remain quantity!')
    ERROR_UPDATE_RULE = _('You can\'t update employee inherit and products stock ready together')


class InventoryMsg:
    GOODS_RECEIPT_NOT_EXIST = _('Goods receipt does not exist')
    INVENTORY_ADJUSTMENT_NOT_EXIST = _('Inventory adjustment does not exist')
    GOODS_RECEIPT_QUANTITY = _('Quantity import must be greater than 0')
