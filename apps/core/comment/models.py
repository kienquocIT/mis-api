from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from apps.shared import MasterDataAbstractModel


class Comments(MasterDataAbstractModel):
    doc_id = models.UUIDField()
    application = models.ForeignKey('base.Application', on_delete=models.CASCADE)

    mentions = models.JSONField(default=dict)
    contents = models.TextField()

    parent_n = models.ForeignKey('self', on_delete=models.CASCADE, null=True)
    children_count = models.SmallIntegerField(default=0)

    def save(self, *args, **kwargs):
        if self.parent_n:
            if self.parent_n.parent_n:
                raise ValueError('Comments support only up to 1 level of replies')
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Comments'
        verbose_name_plural = 'Comments'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()
        indexes = [
            models.Index(fields=['tenant', 'company', 'doc_id'], name='company_tenant_room'),
            models.Index(fields=['tenant', 'company', 'doc_id', 'parent_n'], name='company_tenant_room_parent_n'),
        ]


@receiver(post_save, sender=Comments)
def save_comment(sender, instance, created, **kwargs):  # pylint: disable=W0613
    if created:
        if instance.parent_n:
            instance.parent_n.children_count += 1
            instance.parent_n.save(update_fields=['children_count'])


@receiver(post_delete, sender=Comments)
def destroy_comment(sender, instance, **kwargs):  # pylint: disable=W0613
    if instance.parent_n:
        instance.parent_n.children_count -= 1
        instance.parent_n.save(update_fields=['children_count'])
