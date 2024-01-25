from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from apps.core.log.tasks import force_new_notify_many
from apps.shared import MasterDataAbstractModel, call_task_background, CommentMSg, DisperseModel


class Comments(MasterDataAbstractModel):
    doc_id = models.UUIDField()
    application = models.ForeignKey('base.Application', on_delete=models.CASCADE)

    mentions = models.JSONField(default=list)
    mentions_data = models.JSONField(default=dict)
    contents = models.TextField()

    parent_n = models.ForeignKey('self', on_delete=models.CASCADE, null=True)
    children_count = models.SmallIntegerField(default=0)
    replies_persons = models.JSONField(default=dict)
    replies_latest = models.DateTimeField(null=True)

    def get_mentions_data(self):
        if self.mentions:
            return {
                str(obj.id): {
                    'full_name': obj.get_full_name(),
                    'avatar_img': str(obj.avatar_img.url) if obj.avatar_img else '',
                    'group__title': obj.group.title if obj.group else ''
                }
                for obj in
                DisperseModel(app_model='hr.Employee').get_model().objects.select_related('group').filter_current(
                    id__in=self.mentions, fill__tenant=True, fill__company=True
                )
            }
        return {}

    def get_employee_created_data(self):
        if self.employee_created:
            return {
                'full_name': str(self.employee_created.get_full_name()),
                'avatar_img': str(self.employee_created.avatar_img.url) if self.employee_created.avatar_img else '',
                'group__title': self.employee_created.group.title if self.employee_created.group else ''
            }
        return {}

    def save(self, *args, **kwargs):
        if kwargs.get('force_insert', False) is True:
            self.mentions_data = self.get_mentions_data()
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
        parent_n_update_fields = []
        # resolve parent when has new child
        if instance.parent_n:
            # child count
            instance.parent_n.children_count += 1
            parent_n_update_fields.append('children_count')

            # replies_person
            if str(instance.employee_created_id) not in instance.parent_n.replies_persons:
                instance.parent_n.replies_persons.update({
                    str(instance.employee_created_id): instance.get_employee_created_data()
                })
                parent_n_update_fields.append('replies_persons')

            # latest date
            instance.parent_n.replies_latest = instance.date_created
            parent_n_update_fields.append('replies_latest')

        # resolve mentions data
        if instance.mentions:
            task_kwargs = []
            parent_n__mentions_idx = []
            for employee_id in instance.mentions:
                if instance.parent_n:
                    parent_n__mentions_idx.append(str(employee_id))

                if str(employee_id) != str(instance.employee_created_id):
                    task_kwargs.append({
                        'tenant_id': instance.tenant_id,
                        'company_id': instance.company_id,
                        'title': CommentMSg.have_been_mentioned_title,
                        'msg': CommentMSg.have_been_mentioned_msg.format(instance.employee_created.get_full_name()),
                        'date_created': instance.date_created,
                        'doc_id': instance.doc_id,
                        'doc_app': instance.application.get_prefix_permit(),
                        'employee_id': employee_id,
                        'employee_sender_id': instance.employee_created_id,
                        'application_id': instance.application_id,
                        'comment_mentions_id': instance.id,
                    })
            if len(task_kwargs) > 0:
                call_task_background(
                    my_task=force_new_notify_many,
                    **{
                        'data_list': task_kwargs
                    }
                )
            if len(parent_n__mentions_idx) > 0:
                instance.parent_n.mentions = list(set(parent_n__mentions_idx + instance.parent_n.mentions))
                instance.parent_n.mentions_data = instance.parent_n.get_mentions_data()
                parent_n_update_fields += ['mentions', 'mentions_data']

        if len(parent_n_update_fields) > 0:
            instance.parent_n.save(update_fields=parent_n_update_fields)


@receiver(post_delete, sender=Comments)
def destroy_comment(sender, instance, **kwargs):  # pylint: disable=W0613
    if instance.parent_n:
        instance.parent_n.children_count -= 1
        instance.parent_n.save(update_fields=['children_count'])
