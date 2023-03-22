from django.utils.translation import gettext_lazy as _


class ProductMsg:
    PRODUCT_TYPE_EXIST = _('Product type is already exist.')
    PRODUCT_CATEGORY_EXIST = _('Product category is already exist.')
    EXPENSE_TYPE_EXIST = _('Expense type is already exist.')
    UNIT_OF_MEASURE_GROUP_EXIST = _('Unit of measure group is already exist.')
    UNIT_OF_MEASURE_GROUP_NOT_EXIST = _('Unit of measure group does not exist.')
    UNIT_OF_MEASURE_EXIST = _('Unit of measure is already exist.')
    UNIT_OF_MEASURE_NOT_EXIST = _('Unit of measure does not exist.')
    UNIT_OF_MEASURE_CODE_EXIST = _('Unit of measure code is already exist.')
    PRODUCT_EXIST = _('Product is already exist.')
    PRODUCT_CODE_EXIST = _('Product code is already exist.')
    RATIO_MUST_BE_GREATER_THAN_ZERO = _('Ratio value must be > 0.')
    TITLE_IS_NOT_NONE = _('Title is not null.')
