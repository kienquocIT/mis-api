from django.utils.translation import gettext_lazy as _


class AuthMsg:
    USER_DOES_NOT_EXIST = _('The user does not exist')

    USERNAME_OR_PASSWORD_INCORRECT = _('Username and password are incorrect.')
    USERNAME_ALREADY_EXISTS = _('A user with that username already exists.')
    USERNAME_REQUIRE = _('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.')

    EMPLOYEE_REQUIRE = _('The feature require employee information in your account.')

    TENANT_NOT_FOUND = _('The tenant "{}" not found.')
    TENANT_RETURN_MULTIPLE = _('The tenant "{}" was found return more than one records.')

    LANGUAGE_NOT_SUPPORT = _('The language is not support')

    PASSWORD_IS_INCORRECT = _('The password is incorrect.')
    PASSWORD_REQUIRED_CHARACTERS = _(
        'Password must have more than 6 characters and include 2 of the following conditions: contain uppercase '
        'letters, contain numbers, contain special characters.'
    )
    PASSWORD_NOT_SAME_PASSWORD_AGAIN = _('The new password does not match')
    PASSWORD_NEW_NOT_SAME_CURRENT_PASSWORD = _('The new password does not same current password')

    VALIDATE_OTP_EXPIRED = _('The OTP session was expired')
    OTP_NOT_MATCH = _("OTP isn't match")

    MAX_REQUEST_FORGOT = _('Maximum {0} requests in {1} hour')
