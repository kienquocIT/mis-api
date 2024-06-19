from celery import shared_task
from django.utils import timezone

from apps.core.forms.models import FormPublished


@shared_task
def check_and_update_active_publish_form():
    now = timezone.now()
    ids_deactivate = []
    for obj in FormPublished.objects.filter(is_active=True):
        if obj.date_publish_finish and obj.date_publish_finish <= now:
            obj.is_active = False
            obj.save(update_fields=['is_active'])
            ids_deactivate.append(str(obj.id))
    return ids_deactivate
