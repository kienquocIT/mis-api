from django.utils.translation import gettext_lazy as _

__all__ = ['LeaveMsg']


class LeaveMsg:
    PAID_BY_ONE = _('Company salary')
    PAID_BY_TWO = _('Social insurance')
    PAID_BY_THREE = _('Unpaid')
    ERROR_UPDATE_LEAVE_TYPE = _('Some leave type can not edit please verify again')
    ERROR_ID_CONFIG = _('Can not find config of your company please contact customer maintain this feature.')
    ERROR_LEAVE_TYPE_CODE = _('This code is available please choice other code.')
    ERROR_LEAVE_TITLE = _('Title is required.')
    ERROR_DELETE_LEAVE_TYPE = _('This type can\'t delete')
