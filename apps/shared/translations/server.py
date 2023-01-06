from django.utils.translation import gettext_lazy as _


class ServerMsg:
    UNDEFINED_ERR = _('Undefined error raises.')
    SERVER_ERR = _("Internal Server Error")
    ERR_KEY_DATA = _("key_data == '' must be require data is dictionary.")
    VERIFY_AUTH_REQUIRE_USER = _("Can't check permission of the user if verify user identity don't required.")
