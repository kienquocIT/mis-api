from django.apps import AppConfig


class CompanyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core.company'

    def ready(self):
        # noinspection PyUnresolvedReferences
        import apps.shared.extends.signals
