from django.db.models.signals import post_save, pre_delete, post_delete
from django.dispatch import receiver

from apps.core.forms.models import FormPublishAuthenticateEmail
from apps.core.forms.tasks import form_send_otp
from apps.shared import call_task_background


@receiver(post_save, sender=FormPublishAuthenticateEmail)
def new_form_auth(sender, instance, created, **kwargs):
    if created is True:
        call_task_background(
            my_task=form_send_otp,
            task_config={
                'expires': instance.otp_expires,
                'retry': True,
                'priority': 1,
            },
            **{
                'form_auth_id': str(instance.id),
            }
        )
