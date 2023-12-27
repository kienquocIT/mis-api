from django.utils.translation import gettext_lazy as _

__all__ = [
    'AttMsg',
]


class AttMsg:
    FILE_SIZE_SHOULD_BE_LESS_THAN_X = _('File size should be less than {}')
    IMAGE_TYPE_SHOULD_BE_IMAGE_TYPE = _('File type should be image type: {}')
    FILE_TYPE_DETECT_DANGER = _('The file has been flagged as a security risk.')
    FILE_NO_DETECT_SIZE = _("The size of the file cannot be determined.")
    FILE_SUM_NOT_RETURN = _("The functionality to check available size is not working.")
    FILE_SUM_EXCEED_LIMIT = _("The file size exceeds the limit.")
