import json

from django.core.management.base import BaseCommand
from apps.core.hr.models import Group
from apps.shared import CustomizeEncoder

default_filter = {'company_id': "560bcfd8-bfdb-4f48-b8d2-58c5f9e66320"}


def summary_group(group_obj=None, regis_group_executed=[]):
    data = []
    if group_obj is None:
        for obj in Group.objects.prefetch_related('group_level').filter(**default_filter, parent_n__isnull=True):
            regis_group_executed.append(str(obj.id))
            data.append(
                {
                    'id': obj.id,
                    'title': obj.title,
                    'group_level': obj.group_level.level - 1 if obj.group_level else 0,
                    'children': summary_group(obj, regis_group_executed)
                }
            )
    else:
        for obj in Group.objects.prefetch_related('group_level').filter(**default_filter, parent_n=group_obj):
            if str(obj.id) in regis_group_executed:
                raise ValueError('Group circle execute!')
            regis_group_executed.append(str(obj.id))
            data.append(
                {
                    'id': obj.id,
                    'title': obj.title,
                    'group_level': obj.group_level.level - 1 if obj.group_level else 0,
                    'children': summary_group(obj, regis_group_executed)
                }
            )
    return data


class Command(BaseCommand):
    help = 'Clean cache server'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Running function testing...\n'))
        data = summary_group()
        print(json.dumps(data, cls=CustomizeEncoder, ensure_ascii=False))
