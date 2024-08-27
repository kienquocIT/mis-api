from django.apps import AppConfig


class TasksConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.sales.task'

    def ready(self):
        from .signals import opp_task_pre_save, opp_task_changes, post_save_opp_task_summary
