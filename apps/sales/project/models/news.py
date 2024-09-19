from django.db import models

from apps.shared import MasterDataAbstractModel


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

    def __str__(self):
        return f'{self.msg} - {self.employee_inherit_id}'

    class Meta:
        verbose_name = 'Project News Comment'
        verbose_name_plural = 'Project News Comment'
        ordering = ('-date_created',)
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
