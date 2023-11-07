from django.utils.translation import gettext_lazy as _

__all__ = ['LeaveMsg']


class LeaveMsg:
    ERROR_UPDATE_LEAVE_TYPE = _('Some leave type can not edit please verify again')
    ERROR_ID_CONFIG = _('Can not find config of your company please contact Admin maintain this feature.')
    ERROR_LEAVE_TYPE_CODE = _('This code is available.')
    ERROR_LEAVE_TITLE = _('Title is required.')
    ERROR_DELETE_LEAVE_TYPE = _('This type can’t delete')
    ERROR_DUPLICATE_YEAR = _('This year had available')
    ERROR_EMP_REQUEST = _('Employee inherit is empty')
    ERROR_EMP_DAYOFF = _('Detail request day off is required')
    ERROR_UPDATE_AVAILABLE_ERROR = _('Can not update leave available')
    ERROR_DUPLICATE_HOLIDAY = _('This holiday had available in this year')
    ERROR_NO_OF_PAID_ERROR = _('Number of paid annual leave days minimum is 12')
    TYPE_01 = _('By admin')
    TYPE_02 = _('By system')
    TYPE_03 = _('By employee')
