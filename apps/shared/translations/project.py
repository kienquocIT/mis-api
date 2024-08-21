from django.utils.translation import gettext_lazy as _


class ProjectMsg:
    PROJECT_NOT_EXIST = _('Project do not exist')
    PROJECT_REQUIRED = _('Project is required')
    WORK_NOT_EXIST = _('Work do not exist')
    GROUP_NOT_EXIST = _('Group do not exist')
    PERMISSION_ERROR = _('You do not have permission to perform this action')
    PROJECT = _('Project')
    PROJECT_GROUP = _('Project group')
    PROJECT_WORK = _('Project work')
    PROJECT_WORK_ERROR_DATE = _('Make sure date start larger than relationship work date end')
    PROJECT_WORK_ERROR_DATE2 = _('Date work is not followed with date group')
    PROJECT_CREATE_BASELINE = _('Create baseline error please reload and try again')
    PROJECT_DATE_ERROR = _('Error! Date end larger than Date start')
    PROJECT_DEPENDENCIES_ERROR = _('Work dependencies not found!')
    PROJECT_UPDATE_WORK_ERROR = _('Current work is in progress can not select dependencies type "Finish to start"')
    PROJECT_UPDATE_WORK_ERROR = _('Can not add in progress task to work has type "Finish to start"')
    PROJECT_WEIGHT_ERROR = _('Weight is invalid, or total weight of project larger than 100%')
