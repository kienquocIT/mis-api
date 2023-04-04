from django.utils.translation import gettext_lazy as _


class PriceMsg:
    TITLE_EXIST = _('Name is already exist.')
    CODE_EXIST = _('Code is already exist.')
    ABBREVIATION_EXIST = _('Abbreviation is already exist.')
    RATIO_MUST_BE_GREATER_THAN_ZERO = _('Rate must be > 0')
    FACTOR_MUST_BE_GREATER_THAN_ZERO = _('Factor must be > 0')
    CURRENCY_IS_NOT_NULL = _('Currency is not null')
