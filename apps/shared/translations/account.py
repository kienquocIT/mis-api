from django.utils.translation import gettext_lazy as _


class AccountMsg:
    CODE_EXIST = _('Code is not exist.')
    CODE_NOT_NULL = _('Code must not null.')
    USER_NOT_EXIST = _('User does not exist.')
    PHONE_CONTAIN_CHARACTER = _('Phone number can not contain characters')
    USER_DATA_VALID = _('Data is not valid')
    VALID_PASSWORD = _('Password must contain both numbers and letters')
    COMPANY_NOT_EXIST = _('Company is not exist')
    USERNAME_EXISTS = _('Username is exist, please choose another user name')
