from django.apps import AppConfig


class ProcessConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core.process'

    def ready(self):
        # pylint: disable=import-outside-toplevel / C0415, unused-import / W0611
        from apps.core.process.signals import update_process_members, destroy_process_member
