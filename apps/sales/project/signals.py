from django.db.models.signals import post_delete
from django.dispatch import receiver

from apps.sales.project.models import ProjectWorks
from apps.sales.project.tasks import create_project_news
from apps.shared import call_task_background, ProjectMsg


@receiver(post_delete, sender=ProjectWorks)
def post_delete_prj_work(sender, instance, **kwargs):
    # create news feed
    call_task_background(
        my_task=create_project_news,
        **{
            'project_id': str(instance.project.id),
            'employee_inherit_id': str(instance.employee_inherit.id),
            'employee_created_id': str(instance.employee_created.id),
            'application_id': str('49fe2eb9-39cd-44af-b74a-f690d7b61b67'),
            'document_id': str(instance.id),
            'document_title': str(instance.title),
            'title': ProjectMsg.DELETED_A,
            'msg': '',
        }
    )
