from django.utils.translation import gettext_lazy as _


class HttpMsg:
    DELETE_SUCCESS = _("The information was successfully deleted.")
    DATA_INCORRECT = _("Some data is incorrect.")
    LOGIN_EXPIRES = _("Login was expired. Please login and try again.")
    FORBIDDEN = _("Don't have permission.")
    NOT_FOUND = _("Not found")