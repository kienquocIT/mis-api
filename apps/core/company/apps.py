from django.apps import AppConfig
from django.db.models.signals import post_save


class CompanyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core.company'

    def ready(self):
        from apps.shared.extends.signals import update_stock
        post_save.connect(update_stock, sender=self.get_model('Company'))
