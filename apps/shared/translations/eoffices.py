from django.utils.translation import gettext_lazy as _

__all__ = ['LeaveMsg', 'BusinessMsg', 'MeetingScheduleMsg']


class LeaveMsg:
    ERROR_UPDATE_LEAVE_TYPE = _('Some leave type can not edit please verify again')
    ERROR_ID_CONFIG = _('Can not find config of your company please contact Admin maintain this feature.')
    ERROR_LEAVE_TYPE_CODE = _('This code is available.')
    ERROR_LEAVE_TITLE = _('Title is required.')
    ERROR_DELETE_LEAVE_TYPE = _('This type can’t delete')
    ERROR_DUPLICATE_YEAR = _('This year had available or wrong format')
    ERROR_EMP_REQUEST = _('Employee inherit is empty')
    ERROR_EMP_DAYOFF = _('Detail request day off is required')
    ERROR_UPDATE_AVAILABLE_ERROR = _('Can not update leave available')
    ERROR_DUPLICATE_HOLIDAY = _('This holiday had available in this year')
    ERROR_NO_OF_PAID_ERROR = _('Number of paid annual leave days minimum is 12')
    TYPE_AD = _('By admin')
    TYPE_SYS = _('By system')
    TYPE_EM = _('By employee')
    ERROR_QUANTITY = _('Quantity number is wrong format')
    EMPTY_AVAILABLE_NUMBER = _('Day off large than leave available')
    EMPTY_DATE_EXPIRED = _('Leave available had expired')


class BusinessMsg:
    EMPTY_EXPENSE_ITEMS = _('List expense item is empty')


class MeetingScheduleMsg:
    ROOM_IS_NOT_AVAILABLE = _('This room is not available in this time')
    DUP_CODE = _('Duplicate meeting room code')
    DES_IS_REQUIRED = _('Meeting room description is required')
    SAVE_FILES_ERROR = _('Can not save files.')
