__all__ = [
    'update_process_members',
    'destroy_process_member',
]

from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from apps.core.process.models import ProcessMembers


@receiver(post_save, sender=ProcessMembers)
def update_process_members(sender, instance, created, **kwargs):
    if created and instance.process and instance.employee:
        instance.process.members = list(
            set(
                list(instance.process.members) + [str(instance.employee.id)]
            )
        )
        instance.process.save(update_fields=['members'])


@receiver(pre_delete, sender=ProcessMembers)
def destroy_process_member(sender, instance, **kwargs):
    if instance.process and instance.employee:
        members = list(instance.process.members)
        if str(instance.employee.id) in members:
            members.remove(str(instance.employee.id))
            instance.process.members = members
            instance.process.save(update_fields=['members'])
