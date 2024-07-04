from django.utils.translation import gettext_lazy as _


class BaseMsg:
    PLAN_NOT_EXIST = _('Plan does not exist.')
    APPLICATIONS_NOT_EXIST = _('Some applications do not exist.')
    APPLICATION_IS_ARRAY = _('Application must be array.')
    PROPERTY_NOT_EXIST = _('Application property does not exist.')
    USER_NOT_MAP_EMPLOYEE = _('User still not map with The employee please contact your Admin')
    UPLOAD_FILE_ERROR = _('Upload file is failure. Please refresh and try again.')
    SYSTEM_STATUS_INCORRECT = _('The document status is incorrect')
    NOT_IS_HTML = _('The content is not HTML')
    BLOCK_PHISHING_CODE = _('The content has been blocked because contains phishing code')
    CAUSE_DUPLICATE = _("The records cause duplicate errors")
    CODE_IS_EXISTS = _('Code is exists')
    CODE_NOT_EXIST = _('Code is not exist')
    CODE_NOT_NULL = _('Code must not null')
    NOT_EXIST = _('do not exist.')
    REQUIRED = _('This field is required')
    FORMAT_NOT_MATCH = _('The value formatting is incorrect')
    PROPERTY_IS_ARRAY = _('Application property must be array')
    APPLICATION_NOT_EXIST = _('Application does not exist.')
    ZONE_NOT_EXIST = _('Zone does not exist.')
    ZONE_IS_ARRAY = _('Zone property must be array')


class PermissionMsg:
    PERMISSION_INCORRECT = _('Permission format is incorrect')
    SOME_PLAN_WAS_EXPIRED_OR_NOT_FOUND = _('Some subscription is expired or not found')
    CONFIG_AUTH_VIEW_INCORRECT = _('View config is enable authenticated checking but not provide value of permit')


class AttachmentMsg:
    ERROR_VERIFY = _('Attachment can not verify please try again or contact your admin')
    SOME_FILES_NOT_CORRECT = _('Some attachments are being used by another document or do not exist')


class MailMsg:
    USE_OUR_SERVER = _('Use our server is enabled')
    CONNECT_ERROR = _('Connection errors')
    CONNECT_FAILURE = _('Connect to your mail server is failure')
    CONNECT_DATA_NOT_ENOUGH = _('Config must be fill enough value')
    MAIL_DEACTIVATE_OT_NOT_FOUND = _('The mail server config is deactivate or not found')
