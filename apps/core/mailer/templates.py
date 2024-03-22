__all__ = ['TEMPLATE_OTP_VALIDATE_DEFAULT', 'TEMPLATE_MAIL_WELCOME_DEFAULT', 'TEMPLATE_CALENDAR_DEFAULT']

from django.utils.translation import gettext_lazy as _

SUBJECT_MAIL_WELCOME_DEFAULT = _('Welcome to our company')
# [__company_title__, __company_sub_domain__]
TEMPLATE_MAIL_WELCOME_DEFAULT = _(
    "<h2><strong> <span style=\"text-align: center;\"> __company_title__ </span></strong></h2>"
    "<p>Welcome to our company.</p>"
    "<p>Your medium account information:</p>"
    "<table border=\"1\" style=\"border-collapse: collapse; width: 80.4688%; height: 24px;\">"
    "<tbody>"
    "<tr style=\"height: 12px;\">"
    "<td style=\"width: 18.2031%; height: 12px;\"> Full name </td>"
    "<td style=\"width: 61.1718%; height: 12px;\"> "
    "<span class=\"params-data\" data-code=\"_user__full_name\" id=\"idx-vIJnYHROCPvB2Zv5\"> #User - Full name </span>"
    "</td>"
    "</tr>"
    "<tr style=\"height: 12px;\">"
    "<td style=\"width: 18.2031%; height: 12px;\"> Username </td>"
    "<td style=\"width: 61.1718%; height: 12px;\">"
    "<span class=\"params-data\" data-code=\"_user__user_name\" id=\"idx-3WNAv9BfwepTamrv\">#User - Username</span>"
    "</td>"
    "</tr>"
    "<tr>"
    "<td style=\"width: 18.2031%;\"> Access path </td>"
    "<td style=\"width: 61.1718%;\">"
    "<a href=\"https://__company_sub_domain__.bflow.vn/\">https://__company_sub_domain__.bflow.vn/</a>"
    "</td>"
    "</tr>"
    "</tbody>"
    "</table>"
    "<p>Note: Due to security policy, please use the \"Forgot password\" feature and receive the OTP authentication "
    " code by this email to get the password to access your account.</p>"
    "<p></p>"
    "<p>Best regards.</p>"
)

SUBJECT_OTP_VALIDATE_DEFAULT = _('OTP validation')
# [__company_title__]
TEMPLATE_OTP_VALIDATE_DEFAULT = _(
    "<h2><strong><span style=\"text-align: center;\"> __company_title__ </span></strong></h2>"
    "<p>Verification code: <span id=\"idx-lIYXOPuVrhxqRB1v\" class=\"params-data\" data-code=\"_otp\"> #OTP </span> ​</p>"
    "<p>Current time: "
    "<span id=\"idx-lhaH4zQNQ9fmblYI\" class=\"params-data\" data-code=\"_current_date_time\">#Current date time</span>"
    "</p>"
    "<p>Expires: 2 minutes</p>"
    "<p>Note: The request to send the verification code will be limited to 5 times within 1 hour. Please contact the administrator for any problems.</p>"
    "<p>Best regards.</p>"
)

SUBJECT_CALENDAR_DEFAULT = _('Calendar')
# [__company_title__]
TEMPLATE_CALENDAR_DEFAULT = _(
    "<h2><strong> <span style=\"text-align: center;\"> __company_title__ </span></strong></h2>"
    "<p>Registered event calendar information:</p>"
    "<p></p>"
    "<p>Best regards.</p>"
)
