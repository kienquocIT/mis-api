from django.utils.translation import gettext_lazy as _


class ProvisioningMsg:
    TENANT_READY = _('Tenant code "{}" was ready, process canceling...')
    TENANT_NOT_FOUND = _('Tenant have "{}" code that was not found.')
    EMPLOYEE_DEPENDENCIES_ON_COMPANY = _("Option does not supported. Company and Admin is required.")
    FOUND_MULTI_TENANT_ERR = _('The process was canceled because we found more than one tenant have code {}.')
    CONTACT_SUPPORT = _('Please, contact Admin MIS to be helped.')
    TENANT_ADMIN_READY = _("Tenant's admin was ready.")
    SYNC_REQUIRED_USER_DATA = _('Tenant new must be required admin')
