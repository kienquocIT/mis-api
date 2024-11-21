from django.contrib import admin
from django.utils.html import mark_safe
from apps.sharedapp.admin import AbstractAdmin, my_admin_site
from apps.core.mailer.models import MailLog


@admin.register(MailLog, site=my_admin_site)
class MailLogAdmin(AbstractAdmin):
    @classmethod
    def pretty_address_to(cls, obj):
        if len(obj.address_to) > 0:
            if len(obj.address_to) > 1:
                html_data = []
                for item in obj.address_to:
                    html_data.append(f'<li>{item}</li>')
                return mark_safe(f'<ol>{"".join(html_data)}</ol>')
            return obj.address_to[0]
        return "-"

    list_display = [
        'pretty_address_to', 'subject', 'status_remark',
        'company', 'date_created', 'date_modified',
        'application', 'system_code', 'doc_id',
        'address_sender', 'address_to', 'address_cc', 'address_bcc', 'reply_from', 'reply_to',
        'status_code', 'errors_data',
    ]
