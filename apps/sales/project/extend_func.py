from uuid import uuid4

from apps.core.hr.models import DistributionApplication


def pj_get_alias_permit_from_app(employee_obj):
    result = []
    app_id_get = [
        "e66cfb5a-b3ce-4694-a4da-47618f53de4c",  # Task
    ]

    for obj in DistributionApplication.objects.select_related('app').filter(  # noqa
            employee=employee_obj, app_id__in=app_id_get
    ):
        permit_has_1_range = []
        permit_has_4_range = []
        for permit_code, permit_config in obj.app.permit_mapping.items():
            if '1' in permit_config.get('range', []):
                permit_has_1_range.append(permit_code)
            elif '4' in permit_config.get('range', []):
                permit_has_4_range.append(permit_code)

        has_1 = False
        data_tmp_for_1 = {
            'id': str(uuid4()),
            'app_id': str(obj.app_id),
            'view': False,
            'create': False,
            'edit': False,
            'delete': False,
            'range': '1',
            'space': '0',
        }
        has_4 = False
        data_tmp_for_4 = {
            'id': str(uuid4()),
            'app_id': str(obj.app_id),
            'view': False,
            'create': False,
            'edit': False,
            'delete': False,
            'range': '4',
            'space': '0',
        }

        for key in ['view', 'create', 'edit', 'delete']:
            if key in permit_has_1_range:
                has_1 = True
                data_tmp_for_1[key] = True
            elif key in permit_has_4_range:
                has_4 = True
                data_tmp_for_4[key] = True

        if has_1 is True:
            result.append(data_tmp_for_1)
        if has_4 is True:
            result.append(data_tmp_for_4)
    return result
