from django.apps import AppConfig


class CompanyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core.company'

    def ready(self):
        from apps.shared.extends.signals import update_stock  # pylint: disable=import-outside-toplevel / C0415
        # pylint: disable=W0611
