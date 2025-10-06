from apps.core.attachments.models import processing_folder
from apps.shared import DisperseModel


class ServiceOrderFinishHandler:

    @classmethod
    def re_processing_folder_task_files(cls, instance):
        model_application = DisperseModel(app_model='base.application').get_model()
        if model_application and hasattr(model_application, 'objects'):
            doc_app = model_application.objects.filter(app_label='task', code='opportunitytask').first()
            if doc_app:
                for work_order in instance.work_orders.all():
                    for task in work_order.tasks.all():
                        for task_attachment in task.task_attachment_file_task.all():
                            file = task_attachment.attachment
                            ServiceOrderFinishHandler.run_save_file(
                                file=file, task_id=task.id, doc_app=doc_app
                            )
        return True

    @classmethod
    def run_save_file(cls, file, task_id, doc_app):
        if file:
            if file.folder:
                file.folder.delete()
            folder_obj = processing_folder(doc_id=task_id, doc_app=doc_app)
            if folder_obj:
                file.folder = folder_obj
                file.save(update_fields=['folder'])
        return True
