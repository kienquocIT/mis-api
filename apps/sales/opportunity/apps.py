from django.apps import AppConfig


class OpportunityConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.sales.opportunity'

    def ready(self):
        # pylint: disable=import-outside-toplevel / C0415, unused-import / W0611
        from apps.shared.extends.signals import opp_member_event_update, opp_member_event_destroy
