from django.utils.translation import gettext_lazy as _

__all__ = ['CompanyMsg']


class CompanyMsg:
    VALID_NEED_TENANT_DATA = _('Valid company maximum raise errors.')
    MAXIMUM_COMPANY_LIMITED = _('Maximum company is {} companies.')
