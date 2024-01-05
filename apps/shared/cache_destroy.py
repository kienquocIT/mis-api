from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from apps.core.hr.models import Employee, Group

from .extends.caching import background_destroy_cache_many_key
from .extends.tasks import call_task_background
__all__ = [
    'destroy_cache',
]


@receiver(post_delete, sender=Group)
@receiver(post_save, sender=Group)
@receiver(post_delete, sender=Employee)
@receiver(post_save, sender=Employee)
def destroy_cache(sender, instance, **kwargs):  # pylint: disable=W0613
    return call_task_background(
        background_destroy_cache_many_key,
        *[f'{instance._meta.app_label}_{str(instance.__class__.__name__)}'.lower()],
    )
