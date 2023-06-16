from django.utils.translation import gettext_lazy as _


class PriceMsg:
    TITLE_EXIST = _('Name is already exist.')
    CODE_EXIST = _('Code is already exist.')
    ABBREVIATION_EXIST = _('Abbreviation is already exist.')
    RATIO_MUST_BE_GREATER_THAN_ZERO = _('Rate must be > 0')
    FACTOR_MUST_BE_GREATER_THAN_ZERO = _('Factor must be > 0')
    PRICE_MUST_BE_GREATER_THAN_ZERO = _('Price must be > 0')
    CURRENCY_IS_NOT_NULL = _('Currency is not null.')
    GENERAL_PRICE_LIST_NOT_EXIST = _('General price list does not exist.')
    PRICE_LIST_OR_CURRENCY_NOT_EXIST = _('Price or Currency list does not exist.')
    CURRENCY_NOT_EXIST = _('Currency does not exist.')
    PRICE_LIST_NOT_EXIST = _('Price list does not exist.')
    SALE_INFORMATION_MISSING_PRICE_LIST = _('Sale information is missing price list.')
    PRICE_LIST_IS_MISSING_VALUE = _('Price list is missing value.')
    PRODUCT_NOT_EXIST_IN_THIS_PRICE_LIST = _('Product does not exist in this Price List.')
    PRICE_LIST_IS_ARRAY = _('Price list must be array.')
    DIFFERENT_PRICE_LIST_TYPE = _('New Price List and Source Price List have different type.')
    PARENT_PRICE_LIST_CANT_BE_DELETE = _('Source Price List can not be deleted.')
    NON_EMPTY_PRICE_LIST_CANT_BE_DELETE = _('Non-empty Price List can not be deleted.')
    PRICE_LIST_EXPIRED = _('Price List is expired.')
    ITEM_EXIST = _('Item already exists')
