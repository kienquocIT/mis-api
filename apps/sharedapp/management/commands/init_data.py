import sys
from colorama import Fore

from django.core.management.base import BaseCommand
from django.db.models import Model

from apps.core.base.models import (
    SubscriptionPlan, Application, PlanApplication, PermissionApplication, ApplicationProperty,
    Country, City, District, Ward, Currency,
)
from apps.core.company.models import Company, CompanyConfig
from ...data.base import (
    SubscriptionPlan_data, Application_data, PlanApplication_data, PermissionApplication_data,
    Currency_data,
)
from ...data.application_properties import ApplicationProperty_data
from ...data.vietnam_info import (
    Country_data, Cities_VN_data, Districts_VN_data, Wards_VN_data,
)


class Command(BaseCommand):
    help = 'Initials data for all apps.'

    def add_arguments(self, parser):
        parser.add_argument('--limit_wards', type=bool, help='Limit 100 records wards', default=False, required=False)

    def handle(self, *args, **options):
        # sys.stdout.write(
        #     f'{sys.style.WARNING(str(item[0]))}: {self.style.SUCCESS(str(item[1]))} loaded, '
        #     f'{sys.style.ERROR(str(item[2]))} diff'
        # )
        is_limit_wards = options.get('limit_wards', False)
        InitialsData().loads(is_limit_wards=is_limit_wards)
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
        (Country, Country_data),
        (City, Cities_VN_data),
        (District, Districts_VN_data),
        (Ward, Wards_VN_data),
        (Currency, Currency_data),
    )

    def loads(self, is_limit_wards=False):
        for cls_model, data in self.MAPPING:
            sys.stdout.write(cls_model.__name__ + "... " + Fore.CYAN + ' PROCESSING... ' + Fore.RESET)
            if cls_model == City:
                self.active_load_cities()
            elif cls_model == District:
                self.active_load_district()
            elif cls_model == Ward:
                self.active_load_wards(is_limit_wards)
            else:
                self.active_loads(cls_model, data)
            sys.stdout.write("\n")
        self.confirm_company_config()
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

    @classmethod
    def active_load_cities(cls):
        # (City, Cities_VN_data),
        city_ids = []
        for city_data in Cities_VN_data:
            city_ids.append(city_data['id'])
            obj, created = City.objects.get_or_create(
                id=city_data['id'],
                defaults=city_data
            )
            if created is False:
                for field, value in city_data.items():
                    setattr(obj, field, value)
                obj.save()
        count_diff = City.objects.all().exclude(id__in=city_ids).count()
        sys.stdout.write(
            f'{Fore.CYAN + "DONE... " + Fore.RESET}'
            f'{Fore.GREEN + str(len(city_ids)) + " loaded" + Fore.RESET}'
            f' - '
            f'{Fore.RED + str(count_diff) + " diff" + Fore.RESET}'
        )

    @classmethod
    def active_load_district(cls):
        # (District, Districts_VN_data),
        district_ids = []
        for district_data in Districts_VN_data:
            district_ids.append(district_data['id'])
            obj, created = District.objects.get_or_create(
                id=district_data['id'],
                defaults=district_data
            )
            if created is False:
                for field, value in district_data.items():
                    setattr(obj, field, value)
                obj.save()
        count_diff = District.objects.all().exclude(id__in=district_ids).count()
        sys.stdout.write(
            f'{Fore.CYAN + "DONE... " + Fore.RESET}'
            f'{Fore.GREEN + str(len(district_ids)) + " loaded" + Fore.RESET}'
            f' - '
            f'{Fore.RED + str(count_diff) + " diff" + Fore.RESET}'
        )

    @classmethod
    def active_load_wards(cls, is_limit_wards):
        # (Ward, Wards_VN_data),
        counter = 0
        ward_ids = []
        for ward_data in Wards_VN_data:
            if is_limit_wards is True and counter == 100:
                break
            ward_ids.append(ward_data['id'])
            obj, created = Ward.objects.get_or_create(
                id=ward_data['id'],
                defaults=ward_data
            )
            if created is False:
                for field, value in ward_data.items():
                    setattr(obj, field, value)
                obj.save()
            counter += 1
        count_diff = Ward.objects.exclude(id__in=ward_ids).count()
        sys.stdout.write(
            f'{Fore.CYAN + "DONE... " + Fore.RESET}'
            f'{Fore.GREEN + str(len(ward_ids)) + " loaded" + Fore.RESET}'
            f' - '
            f'{Fore.RED + str(count_diff) + " diff" + Fore.RESET}'
        )

    @classmethod
    def confirm_company_config(cls):
        for obj in Company.objects.all():
            try:
                CompanyConfig.objects.get(company=obj)
            except CompanyConfig.DoesNotExist:
                CompanyConfig.objects.create(
                    company=obj,
                    language='vi',
                    currency=Currency.objects.get(code='VND'),
                )
        print('Confirm config of Company is success')
        return True
