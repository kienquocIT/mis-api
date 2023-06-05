from django.apps import AppConfig


class SaledataConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.masterdata.saledata'

    def ready(self):
        # pylint: disable=import-outside-toplevel / C0415, unused-import / W0611
        from apps.shared.extends.signals import entry_run_workflow
