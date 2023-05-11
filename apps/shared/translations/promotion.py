from django.utils.translation import gettext_lazy as _


class PromoMsg:
    ERROR_NAME = _('Name is required')
    ERROR_VALID_DATE = _('Valid date is required')
    ERROR_CUSTOMER_LIST = _('Customer select from list was not selected!, please verify again.')
    ERROR_CUSTOMER_COND = _('Customer filter by conditions was not added!, please verify again.')
    ERROR_DISCOUNT_METHOD = _('Missing discount method, please verify again.')
    ERROR_PERCENT_VALUE = _('Percent value is empty, please verify again.')
    ERROR_FIXED_AMOUNT = _('Fixed amount value is empty, please verify again.')
    ERROR_MINIMUM_PURCHASE = _('Minimum purchase value is empty, please verify again.')
    ERROR_PRO_SELECTED = _('Special product is empty or product selected not found, please verify again.')
    ERROR_MINIMUM_QUANTITY = _('Minimum quantity value is empty, please verify again.')
    ERROR_GIFT = _('Missing gift method, please verify again.')
    ERROR_FREE_PRODUCT = _('Missing free product setup, please verify again.')
    ERROR_MIN_PURCHASE_TOTAL = _('Minimum purchase total is missing, please verify again.')
    ERROR_PRODUCT_PURCHASE = _('Purchase product is missing, please verify again.')
    ERROR_MISSING_METHOD = _('Missing method, please verify again.')
