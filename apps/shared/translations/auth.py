from django.utils.translation import gettext_lazy as _


class AuthMsg:
    USERNAME_OR_PASSWORD_INCORRECT = _('Username and password are incorrect.')
    USERNAME_ALREADY_EXISTS = _('A user with that username already exists.')
    USERNAME_REQUIRE = _('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.')

    EMPLOYEE_REQUIRE = _('The feature require employee information in your account.')

    TENANT_NOT_FOUND = _('The tenant "{}" not found.')
    TENANT_RETURN_MULTIPLE = _('The tenant "{}" was found return more than one records.')
