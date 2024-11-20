from django.contrib import admin
from apps.core.log.models import Notifications, MailLog
from apps.sharedapp.admin import AbstractAdmin


@admin.register(Notifications)
class NotificationsAdmin(AbstractAdmin):
    list_display = [
        'employee', 'title', 'msg', 'doc_id', 'application', 'is_done', 'notify_type',
    ]
    list_filter = ['is_done', 'notify_type', 'employee', 'company', 'application']


@admin.register(MailLog)
class MailLogAdmin(AbstractAdmin):
    list_display = [field.name for field in MailLog._meta.fields if field.name != 'id']
    list_filter = [
        'is_sent', 'company', 'employee',
    ]
    ordering = ['-date_created']
    date_hierarchy = 'date_created'
