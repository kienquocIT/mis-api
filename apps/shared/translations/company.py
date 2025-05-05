from django.utils.translation import gettext_lazy as _

__all__ = ['CompanyMsg']


class CompanyMsg:
    VALID_NEED_TENANT_DATA = _('Valid company maximum raise errors.')
    MAXIMUM_COMPANY_LIMITED = _('Maximum company is {} companies.')
    CURRENCY_NOT_EXIST = _("Currency either does not exist or unsupported for company.")
    LANGUAGE_NOT_SUPPORT = _("Language isn't support.")
    SUB_DOMAIN_EXIST = _("Sub domain already exists. Please choose another name.")
    INVALID_COMPANY_SETTING_DATA = _("Invalid company setting data.")
    INVALID_COMPANY_FUNCTION_NUMBER_DATA = _("Invalid company function number data.")
    COMPANY_FUNCTION_NUMBER_EXISTED = _("Function number is duplicated.")
    INVALID_BASE_CURRENCY = _("Invalid currency.")
    PRIMARY_CURRENCY_IS_NOT_NULL = _("Primary currency is not NULL.")
    DIV_NOT_VALID = _("Definition inventory valuation not valid.")
    DIV_METHOD_NOT_VALID = _("Definition inventory value method not valid.")
    CANNOT_UPDATE_COMPANY_CFG = _(
        "This company setting can't be updated because there are already transactions in the current fiscal year."
    )
    CANNOT_CHANGE_PRIMARY_CURRENCY = _('Can not change primary currency in the current fiscal year.')
