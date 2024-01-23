from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from apps.core.log.tasks import force_new_notify
from apps.shared import MasterDataAbstractModel, call_task_background, CommentMSg


class Comments(MasterDataAbstractModel):
    doc_id = models.UUIDField()
    application = models.ForeignKey('base.Application', on_delete=models.CASCADE)

    mentions = models.JSONField(default=list)
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
        if instance.mentions:
            for employee_id in instance.mentions:
                if str(employee_id) != str(instance.employee_created_id):
                    call_task_background(
                        my_task=force_new_notify,
                        **{
                            'tenant_id': instance.tenant_id,
                            'company_id': instance.company_id,
                            'title': CommentMSg.have_been_mentioned_title,
                            'msg': CommentMSg.have_been_mentioned_msg.format(instance.employee_created.get_full_name()),
                            'date_created': instance.date_created,
                            'doc_id': instance.doc_id,
                            'doc_app': instance.application.get_prefix_permit(),
                            # 'user_id': '',
                            'employee_id': employee_id,
                            'employee_sender_id': instance.employee_created_id,
                            'application_id': instance.application_id,
                            'comment_mentions_id': instance.id,
                        }
                    )


@receiver(post_delete, sender=Comments)
def destroy_comment(sender, instance, **kwargs):  # pylint: disable=W0613
    if instance.parent_n:
        instance.parent_n.children_count -= 1
        instance.parent_n.save(update_fields=['children_count'])
