from django.utils.translation import gettext_lazy as _


class PromoMsg:
    PROMO_REQ_TITLE = _('Name is required')
    PROMO_REQ_VALID_DATE = _('Valid date is required')
    PROMO_REQ_VALID_CUSTOMER_LIST = _('Customer select from list was not selected!, please verify again.')
    PROMO_REQ_VALID_CUSTOMER_COND = _('Customer filter by conditions was not added!, please verify again.')
    PROMO_REQ_DISCOUNT_METHOD = _('Missing discount method, please verify again.')
