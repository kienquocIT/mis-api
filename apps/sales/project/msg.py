__all__ = [
    'ProjectMsg',
]

from django.utils.translation import gettext_lazy as _


class ProjectMsg:
    MENTIONS_NOT_FOUND = _("The person mentioned could not be found")
    REPLY_NOT_SUPPORT = _("Comment replies are not supported")
    NEWS_NOT_FOUND = _("Activities not found")
