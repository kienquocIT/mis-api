from django.apps import AppConfig


class CompanyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core.company'

    def ready(self):
        # pylint: disable=import-outside-toplevel / C0415, unused-import / W0611
        from apps.shared.extends.signals import update_stock
