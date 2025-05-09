from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.core.firebase.utils import FCMNotify
from apps.core.log.models import Notifications


@receiver(post_save, sender=Notifications)
def new_notify(sender, instance, created, **kwargs):
    if created is True and instance.employee_id:
        company = instance.company
        user = instance.employee.user
        if company and user:
            FCMNotify.send_fcm_notification(
                user=user,
                title=f"""[{company.title or ''}] {instance.title}""",
                body=instance.msg,
            )
