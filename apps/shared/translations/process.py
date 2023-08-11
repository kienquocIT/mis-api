from django.utils.translation import gettext_lazy as _


class SaleProcessMsg:
    NOT_EXIST = _('Does not exist.')
    STEP_NOT_CURRENT = _('This step is not current so can not skip')
    STEP_COMPLETED = _('This step is completed')

    STEP_CURRENT = _('This step is current')
    NOT_SET_CURRENT_STEP_COMPLETED = _('This step is completed, can not set current')
