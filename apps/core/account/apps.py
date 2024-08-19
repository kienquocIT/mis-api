from django.apps import AppConfig


class AccountConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core.account'

    def ready(self):
        from .signals import change_totp_user, delete_totp_user
