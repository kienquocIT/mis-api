__all__ = ['my_admin_site', 'AbstractAdmin']

import os

from django.conf import settings
from django.contrib import admin
from django_celery_results.models import GroupResult, TaskResult
from django_celery_results.admin import GroupResultAdmin, TaskResultAdmin
from django_celery_beat.models import ClockedSchedule, CrontabSchedule, IntervalSchedule, PeriodicTask, SolarSchedule
from django_celery_beat.admin import CrontabScheduleAdmin, ClockedScheduleAdmin, PeriodicTaskAdmin
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken


class AbstractAdmin(admin.ModelAdmin):
    # list_display = [field.name for field in Company._meta.fields if field.name != 'id']
    # list_display = [field.name for field in Company._meta.fields if field.name not in ['id']]

    def has_module_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    class Meta:
        abstract = True


class MyAdminSite(admin.AdminSite):
    site_header = 'Bflow System Admin'
    site_title = 'Bflow'
    password_change_template = os.path.join(
        settings.BASE_DIR, os.path.normpath('apps/sharedapp/templates/admin/change_password.html')
    )

    def get_app_list(self, *args, **kwargs):
        app_list = super().get_app_list(*args, **kwargs)
        try:
            log_app = {}
            mailer_app = {}

            result = []
            for item in app_list:
                if item['app_label'] == 'mailer':
                    mailer_app = item
                elif item['app_label'] == 'log':
                    log_app = item
                else:
                    result.append(item)

            if 'models' in log_app and isinstance(log_app['models'], list):
                log_app['models'] += mailer_app['models']
                log_app['models'] = sorted(log_app['models'], key=lambda d: d['name'])
                result.append(log_app)
            return sorted(result, key=lambda d: d['name'])
        except Exception as err:
            print('err:', err)
        return app_list


my_admin_site = MyAdminSite()


@admin.register(BlacklistedToken, site=my_admin_site)
class BlacklistedTokenAdmin(AbstractAdmin):
    @classmethod
    def jti(cls, obj):
        return obj.token.jti

    @classmethod
    def user(cls, obj):
        return obj.token.user

    @classmethod
    def created_at(cls, obj):
        return obj.token.created_at

    @classmethod
    def expires_at(cls, obj):
        return obj.token.expires_at

    def has_add_permission(self, request):
        return request.user.is_superuser is True

    list_display = ['jti', 'user', 'created_at', 'expires_at', 'blacklisted_at']
    list_filter = ['token__user']
    ordering = ['-blacklisted_at']
    search_fields = ['user__full_name_search', 'user__id']
    date_hierarchy = 'blacklisted_at'


@admin.register(OutstandingToken, site=my_admin_site)
class OutstandingTokenAdmin(AbstractAdmin):
    list_display = ['jti', 'user', 'created_at', 'expires_at']
    list_filter = ['user']
    ordering = ['-created_at']
    search_fields = ['user__full_name_search', 'user__id']
    date_hierarchy = 'created_at'


@admin.register(GroupResult, site=my_admin_site)
class CusTaskResultAdmin(GroupResultAdmin, AbstractAdmin):
    pass


@admin.register(TaskResult, site=my_admin_site)
class CusTaskResultAdmin(TaskResultAdmin, AbstractAdmin):
    pass


@admin.register(IntervalSchedule, site=my_admin_site)
class CusIntervalScheduleAdmin(AbstractAdmin):
    pass


@admin.register(CrontabSchedule, site=my_admin_site)
class CusCrontabScheduleAdmin(CrontabScheduleAdmin, AbstractAdmin):
    pass


@admin.register(SolarSchedule, site=my_admin_site)
class CusSolarScheduleAdmin(AbstractAdmin):
    pass


@admin.register(ClockedSchedule, site=my_admin_site)
class CusClockedScheduleAdmin(ClockedScheduleAdmin, AbstractAdmin):
    pass


@admin.register(PeriodicTask, site=my_admin_site)
class CusPeriodicTaskAdmin(PeriodicTaskAdmin, AbstractAdmin):
    pass
