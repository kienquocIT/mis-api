from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.core.log.tasks import force_new_notify_many
from apps.shared import MasterDataAbstractModel, CommentMSg, call_task_background


class ProjectNews(MasterDataAbstractModel):
    project = models.ForeignKey('project.Project', on_delete=models.CASCADE)
    application = models.ForeignKey('base.Application', null=True, on_delete=models.SET_NULL)
    document_id = models.UUIDField(null=True, verbose_name='Doc related to news')
    document_title = models.CharField(max_length=255, blank=True, null=True)
    msg = models.TextField(blank=True, verbose_name='Message')
    employee_inherit = models.ForeignKey(
        'hr.Employee', null=True, on_delete=models.SET_NULL,
        help_text='',
        related_name='%(app_label)s_%(class)s_employee_inherit',
    )
    count_comment = models.IntegerField(
        verbose_name="Count comment",
        default=0,
        null=True
    )

    def __str__(self):
        return f'{self.msg} - {self.document_title} - {self.project_id}'

    class Meta:
        verbose_name = 'Project News'
        verbose_name_plural = 'Project News'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class ProjectNewsComment(MasterDataAbstractModel):
    news = models.ForeignKey('project.ProjectNews', on_delete=models.CASCADE, related_name='comments_of_project_news')
    msg = models.TextField(blank=True, verbose_name='Message')
    mentions = models.JSONField(default=list, verbose_name='Mention person in comment')
    employee_inherit = models.ForeignKey(
        'hr.Employee', null=True, on_delete=models.SET_NULL,
        help_text='',
        related_name='%(app_label)s_%(class)s_employee_inherit',
    )
    reply_from = models.ForeignKey('self', on_delete=models.CASCADE, null=True)
    message_reply_count = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.msg} - {self.employee_inherit_id}'

    class Meta:
        verbose_name = 'Project News Comment'
        verbose_name_plural = 'Project News Comment'
        ordering = ('date_created',)
        default_permissions = ()
        permissions = ()


class ProjectNewsCommentMentions(MasterDataAbstractModel):
    employee = models.ForeignKey(
        'hr.Employee',
        on_delete=models.CASCADE,
        related_name='comments_has_mention_of'
    )
    comment = models.ForeignKey(
        'project.ProjectNewsComment',
        on_delete=models.CASCADE,
        related_name='mention_person_by_comment',
    )

    def __str__(self):
        return f'{self.employee_id} - {self.comment_id}'

    class Meta:
        verbose_name = 'Project News Mentions'
        verbose_name_plural = 'Project News Mentions'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


@receiver(post_save, sender=ProjectNewsComment)
def save_comment_prj(sender, instance, created, **kwargs):  # pylint: disable=W0613
    if created:
        # resolve mentions data
        if instance.mentions:
            task_kwargs = []
            for employee_id in instance.mentions:
                if str(employee_id) != str(instance.employee_created_id):
                    task_kwargs.append({
                        'tenant_id': instance.tenant_id,
                        'company_id': instance.company_id,
                        'title': CommentMSg.have_been_mentioned_msg.format(instance.employee_created.get_full_name()),
                        'msg': instance.msg,
                        'notify_type': 20,
                        'date_created': instance.date_created,
                        'doc_id': str(instance.id),
                        'doc_app': 'project.activities',
                        'employee_id': employee_id,
                        'employee_sender_id': instance.employee_created_id,
                    })
            if len(task_kwargs) > 0:
                call_task_background(
                    my_task=force_new_notify_many,
                    **{
                        'data_list': task_kwargs
                    }
                )
