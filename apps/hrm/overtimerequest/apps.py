from django.apps import AppConfig


class OvertimerequestConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.hrm.overtimerequest'
    
    def ready(self):
        import apps.hrm.overtimerequest.signals
