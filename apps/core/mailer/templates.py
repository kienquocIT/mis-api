__all__ = ['TEMPLATE_OTP_VALIDATE_DEFAULT', 'TEMPLATE_MAIL_WELCOME_DEFAULT', 'TEMPLATE_CALENDAR_DEFAULT',
           'TEMPLATE_PROJECT_NEW_DEFAULT', 'TEMPLATE_REQUEST_CONTRACT_DEFAULT', 'TEMPLATE_REQUEST_LEAVE_DEFAULT',
           'SUBJECT_NEW_COMMENT_DEFAULT', 'TEMPLATE_MENTION_COMMENT_DEFAULT', 'SUBJECT_NEW_TASK_DEFAULT',
           'TEMPLATE_NEW_TASKS_DEFAULT']

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

SUBJECT_WORKFLOW_DEFAULT = _('Workflow')
# [__company_title__]
TEMPLATE_WORKFLOW_DEFAULT = _(
    "<h2><strong><span style=\"text-align: center;\"> __company_title__ </span></strong></h2>"
    "<p><span class=\"params-data\" data-code=\"_workflow__wf_title\"></span></p>"
    "<p><span class=\"params-data\" data-code=\"_workflow__wf_common_text_0\"></span><span class=\"params-data\" data-code=\"_workflow__wf_application_title\"></span></p>"
    "<p><span class=\"params-data\" data-code=\"_workflow__wf_common_text_1\"></span> <a href=\"_workflow__wf_common_text_2\"><span class=\"params-data\" data-code=\"_workflow__wf_common_text_3\"></span></a></p>"
    "<hr/>"
    "<p>Best regards.</p>"
)

SUBJECT_PROJECT_NEW_DEFAULT = _('New Project Created')
# [__company_title__]
TEMPLATE_PROJECT_NEW_DEFAULT = _(
    "<h2><strong><span style=\"text-align: center;\"> __company_title__ </span></strong></h2>"
    "<p>Hi <b><span class=\"params-data\" data-code=\"_project__prj_member\"></span></b></p>"
    "<p><b><span class=\"params-data\" data-code=\"_project__prj_owner\"></span></b> create a project <b><span class=\"params-data\" data-code=\"_project__prj_title\"></span></b>. He/She added you in a member in Project, you might want to take a look.</p>"
    "<p><a href=\"_project__prj_url\" style=\"text-decoration:none;color:#1565c0;\">View here</a></p>"
    "<hr/>"
    "<p>Best regards.</p>"
)

SUBJECT_CONTRACT_NEW_DEFAULT = _('New Contract signature request created')

TEMPLATE_REQUEST_CONTRACT_DEFAULT = _(
    "<h2 style=\"font-weight: 500; font-size: 20px\">Company: <strong><span style=\"text-align: center;\"> __company_title__ </span></strong></h2>"
    "<p style=\"color: #007D88; font-size: 18px\">Hello <b><span class=\"params-data\" data-code=\"_contract__member\"></span></b></p>"
    "<div style=\"background: #f6f6f6;text-align: center;padding: 20px 25px\"><p>You have a document needed signature from:</p>"
    "<p><b><span class=\"params-data\" data-code=\"_contract__created_email\"></span></b></p>"
    "<p><b><span class=\"params-data\" data-code=\"_contract__title\"></span></b></p>"
    "<p><a href=\"_contract__url\" style=\"text-decoration:none;color:#fff;width: 150px;display: inline-block;background: #007D88;padding: 6px;text-transform: uppercase;letter-spacing: .95px;\">View document</a></p></div>"
)

SUBJECT_LEAVE_NEW_DEFAULT = _('New leave request created')

TEMPLATE_REQUEST_LEAVE_DEFAULT = _(
    "<h2 style=\"font-weight: 500; font-size: 20px\">Company: <strong><span style=\"text-align: center;\"> __company_title__ </span></strong></h2>"
    "<p style=\"font-size: 18px\">Hi, </p>"
    "<div><p>Employee <span class=\"params-data\" data-code=\"_leave__employee\"></span> has been granted leave for about <span class=\"params-data\" data-code=\"_leave__day_off\"></span> days, and will return to work on <span class=\"params-data\" data-code=\"_leave__date_back\"></span>.</p>"
    "<p>During this period, please contact <span class=\"params-data\" data-code=\"_leave__leader_name\"></span> at <span class=\"params-data\" data-code=\"_leave__leader_email\"></span> if your email requires immediate attention.</p>"
    "</div>"
)

SUBJECT_NEW_COMMENT_DEFAULT = _('You were mentioned in a comment')

TEMPLATE_MENTION_COMMENT_DEFAULT = _(
    "<h2 style=\"font-weight: 500; font-size: 20px\">Company: <strong><span style=\"text-align: center;\"> __company_title__ </span></strong></h2>"
    "<p style=\"font-size: 18px\">Hi, </p>"
    "<blockquote style=\"font-style: italic;\"><span class=\"params-data\" data-code=\"_mention__comment_msg\"></span></blockquote>"
    "<p><a href=\"_mention__links\" style=\"text-decoration:none;color:#fff;width: 150px;display: inline-block;background: #007D88;padding: 6px;text-transform: uppercase;letter-spacing: .95px; text-align:center;\">View document</a></p>"
)

SUBJECT_NEW_TASK_DEFAULT = _('🔔 Notification: You have new to do tasks')

TEMPLATE_NEW_TASKS_DEFAULT = _(
    "<h2 style=\"font-weight: 500; font-size: 20px\">Company: <strong><span style=\"text-align: center;\"> __company_title__ </span></strong></h2>"
    "<p style=\"font-size: 18px\">Hi, <span class=\"params-data\" data-code=\"_task__employee_inherit\"></span></p>"
    "<p>You have a new task! <strong style=\"font-style: italic;\"><span class=\"params-data\" data-code=\"_task__assigner\"></span></strong> has just sent you a task that needs to be processed. Please check and start working on it.</p>"
    "<p><a href=\"_task__links\" style=\"text-decoration:none;color:#fff;width: 150px;display: inline-block;background: #007D88;padding: 6px;text-transform: uppercase;letter-spacing: .95px; text-align:center;\">View document</a></p>"
)
