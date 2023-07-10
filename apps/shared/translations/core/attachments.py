from django.utils.translation import gettext_lazy as _

__all__ = [
    'AttMsg',
]


class AttMsg:
    FILE_SIZE_SHOULD_BE_LESS_THAN_X = _('File size should be less than {}')
    IMAGE_TYPE_SHOULD_BE_IMAGE_TYPE = _('File type should be image type: {}')
