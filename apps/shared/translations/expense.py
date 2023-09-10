from django.utils.translation import gettext_lazy as _


class ExpenseMsg:
    EXPENSE_TYPE_NOT_EXIST = _('Expense type not exist.')
    TAX_CODE_NOT_EXIST = _('Tax code not exist.')
    UOM_NOT_EXIST = _('unit of measure not exist.')
    UOM_GROUP_NOT_EXIST = _('unit of measure group not exist.')
    CODE_EXIST = _('Expense code is already exist.')
    CURRENCY_NOT_EXIST = _('Currency not exist')
    UOM_NOT_MAP_UOM_GROUP = _('unit of measure not in unit of measure group')
    IS_REQUIRED = _('must be required')

    PARENT_NOT_EXIST = _('Expense parent does not exist.')
