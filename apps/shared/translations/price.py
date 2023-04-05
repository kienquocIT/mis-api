from django.utils.translation import gettext_lazy as _


class PriceMsg:
    TITLE_EXIST = _('Name is already exist.')
    CODE_EXIST = _('Code is already exist.')
    ABBREVIATION_EXIST = _('Abbreviation is already exist.')
    RATIO_MUST_BE_GREATER_THAN_ZERO = _('Rate must be > 0')
    FACTOR_MUST_BE_GREATER_THAN_ZERO = _('Factor must be > 0')
    PRICE_MUST_BE_GREATER_THAN_ZERO = _('Price must be > 0')
    CURRENCY_IS_NOT_NULL = _('Currency is not null.')
    PRICE_LIST_IS_MISSING_VALUE = _('Missing value for Price list.')
    GENERAL_PRICE_LIST_NOT_EXIST = _('General price list does not exist.')
    PRICE_LIST_OR_CURRENCY_NOT_EXIST = _('Price or Currency list does not exist.')
    CURRENCY_NOT_EXIST = _('Currency does not exist.')
