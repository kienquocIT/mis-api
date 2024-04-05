from django.utils.translation import gettext_lazy as _


class AccountMsg:
    CODE_EXIST = _('Code is not exist')
    CODE_NOT_NULL = _('Code must not null')
    USER_NOT_EXIST = _('User does not exist.')
    PHONE_CONTAIN_CHARACTER = _('Phone number can not contain characters')
    USER_DATA_VALID = _('Data is not valid')
    VALID_PASSWORD = _('Password must contain both numbers and letters')
    COMPANY_NOT_EXIST = _('Company is not exist')
    USERNAME_EXISTS = _('Username is exist, please choose another user name')
    USERNAME_MUST_BE_SLUGIFY_STRING = _(
        'Enter a valid \"slug\" consisting of letters, numbers, underscores or hyphens'
    )
    USER_NOT_BELONG_TO_COMPANY = _("The user does not belong to this company.")
    TENANT_MANAGE_ADD_USER_TO_COMPANY = _(
        "Please go to the tenant management page feature to add a company for this user."
    )
