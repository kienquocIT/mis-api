import sys
from colorama import Fore

from django.core.management.base import BaseCommand
from django.db.models import Model

from apps.core.base.models import SubscriptionPlan, Application, PlanApplication, PermissionApplication, \
    ApplicationProperty
from apps.core.workflow.models import Node
from ...data.base import SubscriptionPlan_data, Application_data, PlanApplication_data, PermissionApplication_data, \
    ApplicationProperty_data
from ...data.workflow import Node_data


class Command(BaseCommand):
    help = 'Initials data for all apps.'

    def handle(self, *args, **options):
        # sys.stdout.write(
        #     f'{sys.style.WARNING(str(item[0]))}: {self.style.SUCCESS(str(item[1]))} loaded, '
        #     f'{sys.style.ERROR(str(item[2]))} diff'
        # )
        InitialsData().loads()
        self.stdout.write(self.style.SUCCESS('Successfully initials data.'))


class InitialsData:
    MAPPING = (
        # ('Model Class', Data)
        # Data      "id": {...more...}
        (SubscriptionPlan, SubscriptionPlan_data),
        (Application, Application_data),
        (PlanApplication, PlanApplication_data),
        (PermissionApplication, PermissionApplication_data),
        (ApplicationProperty, ApplicationProperty_data),
        (Node, Node_data),
    )

    def loads(self):
        for cls_model, data in self.MAPPING:
            sys.stdout.write(cls_model.__name__ + "... " + Fore.CYAN + ' PROCESSING... ' + Fore.RESET)
            self.active_loads(cls_model, data)
            sys.stdout.write("\n")
        return True

    @classmethod
    def active_loads(cls, cls_model: Model, data: dict) -> any:
        for idx, more_fields in data.items():
            obj, _created = cls_model.objects.get_or_create(pk=idx, defaults=more_fields)
            if _created is False:
                for field, data_field in more_fields.items():
                    setattr(obj, field, data_field)
                obj.save()
        count_diff = cls_model.objects.all().exclude(id__in=data.keys()).count()
        sys.stdout.write(
            f'{Fore.CYAN + "DONE... " + Fore.RESET}'
            f'{Fore.GREEN + str(len(data.keys())) + " loaded" + Fore.RESET}'
            f' - '
            f'{Fore.RED + str(count_diff) + " diff" + Fore.RESET}'
        )
        return True
