from django.utils.translation import gettext_lazy as _

__all__ = ['CompanyMsg']


class CompanyMsg:
    VALID_NEED_TENANT_DATA = _('Valid company maximum raise errors.')
    MAXIMUM_COMPANY_LIMITED = _('Maximum company is {} companies.')
    CURRENCY_NOT_EXIST = _("Currency isn't support for company.")
    LANGUAGE_NOT_SUPPORT = _("Language isn't support.")
    SUB_DOMAIN_EXIST = _("Sub domain already exists. Please choose another name.")
    INVALID_COMPANY_SETTING_DATA = _("Invalid company setting data.")
    INVALID_COMPANY_FUNCTION_NUMBER_DATA = _("Invalid company function number data.")
    INVALID_BASE_CURRENCY = _("Invalid currency.")
    PRIMARY_CURRENCY_IS_NOT_NULL = _("Primary currency is not NULL.")
    DIV_NOT_VALID = _("Definition inventory valuation not valid.")
    DIV_METHOD_NOT_VALID = _("Definition inventory value method not valid.")
