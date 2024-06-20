from django.apps import AppConfig


class FormsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core.forms'

    def ready(self):
        # pylint: disable=import-outside-toplevel / C0415, unused-import / W0611
        from apps.shared.extends.signals import form_post_save
