from .plan_app_sub.base import Application_base_data as _Application_base_data
from .plan_app_sub.crm import Application_crm_data as _Application_crm_data
from .plan_app_sub.eoffice import Application_eOffice_data as _Application_eOffice_data

__all__ = [
    "SubscriptionPlan_data",
    "Application_data",
    "PlanApplication_data",
    "FULL_PLAN_ID",
    "check_app_depends_and_mapping",
    "FullPermitHandle",
]

SubscriptionPlan_data = {
    "e42e93b6-5a7d-4d75-b6da-b288045058df": {
        "title": "Base",
        "code": "base",
    },
    "395eb68e-266f-45b9-b667-bd2086325522": {
        "title": "HRM",
        "code": "hrm",
    },
    "4e082324-45e2-4c27-a5aa-e16a758d5627": {
        "title": "Sale",
        "code": "sale",
    },
    "a8ca704a-11b7-4ef5-abd7-f41d05f9d9c8": {
        "title": "E-Office",
        "code": "e-office",
    },
    "a939c80b-6cb6-422c-bd42-34e0adf91802": {
        "title": "Personal",
        "code": "personal",
    },
}

Application_data = {
    **_Application_base_data,
    **_Application_crm_data,
    **_Application_eOffice_data,
}

_PlanApplication_base_data = {
    "269f4421-04d8-4528-bc95-148ffd807235": {
        "plan_id": "e42e93b6-5a7d-4d75-b6da-b288045058df",  # Base
        "application_id": "269f4421-04d8-4528-bc95-148ffd807235",  # Company
    },
    "af9c6fd3-1815-4d5a-aa24-fca9d095cb7a": {
        "plan_id": "e42e93b6-5a7d-4d75-b6da-b288045058df",  # Base
        "application_id": "af9c6fd3-1815-4d5a-aa24-fca9d095cb7a",  # User
    },
    "50348927-2c4f-4023-b638-445469c66953": {
        "plan_id": "e42e93b6-5a7d-4d75-b6da-b288045058df",  # Base
        "application_id": "50348927-2c4f-4023-b638-445469c66953",  # Employee
    },
    "4cdaabcc-09ae-4c13-bb4e-c606eb335b11": {
        "plan_id": "e42e93b6-5a7d-4d75-b6da-b288045058df",  # Base
        "application_id": "4cdaabcc-09ae-4c13-bb4e-c606eb335b11",  # Role
    },
    "e17b9123-8002-4c9b-921b-7722c3c9e3a5": {
        "plan_id": "e42e93b6-5a7d-4d75-b6da-b288045058df",  # Base
        "application_id": "e17b9123-8002-4c9b-921b-7722c3c9e3a5",  # Group
    },
    "71393401-e6e7-4a00-b481-6097154efa64": {
        "plan_id": "e42e93b6-5a7d-4d75-b6da-b288045058df",  # Base
        "application_id": "71393401-e6e7-4a00-b481-6097154efa64",  # Workflow
    },
}

_PlanApplication_hrm_data = {}

_PlanApplication_sale_data = {
    "828b785a-8f57-4a03-9f90-e0edf96560d7": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "828b785a-8f57-4a03-9f90-e0edf96560d7",  # Contact
    },
    "4e48c863-861b-475a-aa5e-97a4ed26f294": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "4e48c863-861b-475a-aa5e-97a4ed26f294",  # Account
    },
    "296a1410-8d72-46a8-a0a1-1821f196e66c": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "296a1410-8d72-46a8-a0a1-1821f196e66c",  # Opportunity
    },
    "b9650500-aba7-44e3-b6e0-2542622702a3": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "b9650500-aba7-44e3-b6e0-2542622702a3",  # Quotation
    },
    "a870e392-9ad2-4fe2-9baa-298a38691cf2": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "a870e392-9ad2-4fe2-9baa-298a38691cf2",  # Sale Order
    },
    "a8badb2e-54ff-4654-b3fd-0d2d3c777538": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "a8badb2e-54ff-4654-b3fd-0d2d3c777538",  # Product
    },
    "022375ce-c99c-4f11-8841-0a26c85f2fc2": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "022375ce-c99c-4f11-8841-0a26c85f2fc2",  # Expenses
    },
    "80b8cd4f-cfba-4f33-9642-a4dd6ee31efd": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "80b8cd4f-cfba-4f33-9642-a4dd6ee31efd",  # WareHouse
    },
    "47e538a8-17e7-43bb-8c7e-dc936ccaf474": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "47e538a8-17e7-43bb-8c7e-dc936ccaf474",  # Good Receipt
    },
    "3d8ad524-5dd9-4a8b-a7cd-a9a371315a2a": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "3d8ad524-5dd9-4a8b-a7cd-a9a371315a2a",  # Picking
    },
    "1373e903-909c-4b77-9957-8bcf97e8d6d3": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "1373e903-909c-4b77-9957-8bcf97e8d6d3",  # Delivery
    },
    "10a5e913-fa51-4127-a632-a8347a55c4bb": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "10a5e913-fa51-4127-a632-a8347a55c4bb",  # Prices
    },
    "e6a00a1a-d4f9-41b7-b0de-bb1efbe8446a": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "e6a00a1a-d4f9-41b7-b0de-bb1efbe8446a",  # Shipping
    },
    "f57b9e92-cb01-42e3-b7fe-6166ecd18e9c": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "f57b9e92-cb01-42e3-b7fe-6166ecd18e9c",  # Promotion
    },
    "57725469-8b04-428a-a4b0-578091d0e4f5": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "57725469-8b04-428a-a4b0-578091d0e4f5",  # Advance Payment
    },
    "1010563f-7c94-42f9-ba99-63d5d26a1aca": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "1010563f-7c94-42f9-ba99-63d5d26a1aca",  # Payment
    },
    "3407d35d-27ce-407e-8260-264574a216e3": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "3407d35d-27ce-407e-8260-264574a216e3",  # Payment Term
    },
    "65d36757-557e-4534-87ea-5579709457d7": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "65d36757-557e-4534-87ea-5579709457d7",  # Return Advance
    },
    "e66cfb5a-b3ce-4694-a4da-47618f53de4c": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "e66cfb5a-b3ce-4694-a4da-47618f53de4c",  # Task
    },
    "319356b4-f16c-4ba4-bdcb-e1b0c2a2c124": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "319356b4-f16c-4ba4-bdcb-e1b0c2a2c124",  # Document For Customer
    },
    "14dbc606-1453-4023-a2cf-35b1cd9e3efd": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "14dbc606-1453-4023-a2cf-35b1cd9e3efd",  # Call Log
    },
    "dec012bf-b931-48ba-a746-38b7fd7ca73b": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "dec012bf-b931-48ba-a746-38b7fd7ca73b",  # Email Log
    },
    "2fe959e3-9628-4f47-96a1-a2ef03e867e3": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "2fe959e3-9628-4f47-96a1-a2ef03e867e3",  # Meting Log
    },
    "31c9c5b0-717d-4134-b3d0-cc4ca174b168": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "31c9c5b0-717d-4134-b3d0-cc4ca174b168",  # Contract
    },
    "d78bd5f3-8a8d-48a3-ad62-b50d576ce173": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "d78bd5f3-8a8d-48a3-ad62-b50d576ce173",  # Purchase Quotation Request
    },
    "f52a966a-2eb2-4851-852d-eff61efeb896": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "f52a966a-2eb2-4851-852d-eff61efeb896",  # Purchase Quotation
    },
    "81a111ef-9c32-4cbd-8601-a3cce884badb": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "81a111ef-9c32-4cbd-8601-a3cce884badb",  # Purchase Order
    },
    "fbff9b3f-f7c9-414f-9959-96d3ec2fb8bf": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "fbff9b3f-f7c9-414f-9959-96d3ec2fb8bf",  # Purchase Request
    },
    "245e9f47-df59-4d4a-b355-7eff2859247f": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "245e9f47-df59-4d4a-b355-7eff2859247f",  # Expense Item
    },
    "dd16a86c-4aef-46ec-9302-19f30b101cf5": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "dd16a86c-4aef-46ec-9302-19f30b101cf5",  # Goods Receipt
    },
    "866f163d-b724-404d-942f-4bc44dc2e2ed": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "866f163d-b724-404d-942f-4bc44dc2e2ed",  # Goods Transfer
    },
    "f26d7ce4-e990-420a-8ec6-2dc307467f2c": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "f26d7ce4-e990-420a-8ec6-2dc307467f2c",  # Goods Issue
    },
    "c5de0a7d-bea3-4f39-922f-06a40a060aba": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "c5de0a7d-bea3-4f39-922f-06a40a060aba",  # Inventory Adjustment
    },
}

_PlanApplication_eOffice_data = {
    "baff033a-c416-47e1-89af-b6653534f06e": {
        "plan_id": "a8ca704a-11b7-4ef5-abd7-f41d05f9d9c8",  # E-office
        "application_id": "baff033a-c416-47e1-89af-b6653534f06e",  # Leave
    },
    "7738935a-0442-4fd4-a7ff-d06a22aaeccf": {
        "plan_id": "a8ca704a-11b7-4ef5-abd7-f41d05f9d9c8",  # E-office
        "application_id": "7738935a-0442-4fd4-a7ff-d06a22aaeccf",  # Leave available
    }
}

PlanApplication_data = {
    **_PlanApplication_base_data,
    **_PlanApplication_hrm_data,
    **_PlanApplication_sale_data,
    **_PlanApplication_eOffice_data,
}


class FullPermitHandle:
    @classmethod
    def parse_one_permit_allow(
            cls, app_data, plan_data, range_code,
            is_view=False, is_create=False, is_edit=False, is_delete=False,
            sub_data: list = None,
    ):
        sub_data = [] if sub_data is None else sub_data
        return {
            'id': None,
            'app_id': app_data['id'],
            'app_data': {
                'id': app_data['id'],
                'title': app_data['title'],
                'code': app_data['code'],
                'model_code': app_data['model_code'],
                'app_label': app_data['app_label'],
                'option_permission': app_data['option_permission'],
            } if 'title' in app_data else {},
            'plan_id': plan_data['id'],
            'plan_data': {
                'id': plan_data['id'], 'title': plan_data['title'], 'code': plan_data['code']
            } if 'title' in plan_data else {},
            'create': is_create,
            'view': is_view,
            'edit': is_edit,
            'delete': is_delete,
            'range': range_code,
            'sub': sub_data
        }

    @classmethod
    def parse_permit_code_to_dict(cls, data):
        if data == 'view':
            return {'is_view': True}
        if data == 'create':
            return {'is_create': True}
        if data == 'edit':
            return {'is_edit': True}
        if data == 'delete':
            return {'is_delete': True}
        return {}

    @classmethod
    def get_by_app(cls, app_data, plan_data):
        result = []
        for permit, config in app_data.get('permit_mapping', {}).items():
            permit_has_range = config.get('range', [])
            for range_code in permit_has_range:
                result.append(
                    cls.parse_one_permit_allow(
                        app_data=app_data, plan_data=plan_data, range_code=range_code,
                        **cls.parse_permit_code_to_dict(permit),
                    )
                )
        return result

    @classmethod
    def full_permit(cls):
        result = []
        for _key, value in PlanApplication_data.items():
            if _key != value['application_id']:
                raise ValueError('PlanApplication ID must be equal Application ID.')
            plan_data = {'id': value['plan_id'], **SubscriptionPlan_data[value['plan_id']]}
            app_data = {'id': value['application_id'], **Application_data[value['application_id']]}
            result += cls.get_by_app(app_data=app_data, plan_data=plan_data)
        return result


FULL_PERMISSIONS_BY_CONFIGURED = FullPermitHandle.full_permit()
FULL_PLAN_ID = SubscriptionPlan_data.keys()


class CheckingDependsOnApp:
    RANGE_ALLOWED = ['1', '2', '3', '4', '*', '==']

    @classmethod
    def make_sure_range_support(cls, range_or_range_list):
        if isinstance(range_or_range_list, list):
            for range_x in range_or_range_list:
                cls.make_sure_range_support(range_x)
        else:
            if range_or_range_list not in cls.RANGE_ALLOWED:
                raise ValueError(
                    'Range "%s" not in RANGE_ALLOWED = %s.' % (
                        str(range_or_range_list),
                        str(cls.RANGE_ALLOWED)
                    )
                )

    @classmethod
    def check_depends_on_app_correct(cls, app_depend_on):
        if app_depend_on:
            if isinstance(app_depend_on, dict):
                for app_id, permit_config in app_depend_on.items():
                    app_data = Application_data.get(app_id, None)
                    if app_data:
                        data_permit_map = app_data.get('permit_mapping', [])
                        data_permit_keys = list(set(data_permit_map.keys()))
                        for permit_key, allow_range_code in permit_config.items():
                            cls.make_sure_range_support(allow_range_code)
                            if not allow_range_code or (
                                    isinstance(allow_range_code, list) and len(allow_range_code) == 0
                            ):
                                raise ValueError(
                                    'The application ID "%s" require range for depends on apps.' % (str(app_id))
                                )

                            if permit_key not in data_permit_keys:
                                raise ValueError(
                                    'The application ID "%s" permit not in permit allow of app depended. '
                                    'DATA: "%s" not in %s.' % (
                                        str(app_id),
                                        str(permit_key),
                                        str(data_permit_keys),
                                    )
                                )
                            else:
                                range_mapped_by_key = data_permit_map[permit_key].get('range', [])
                                cls.make_sure_range_support(range_mapped_by_key)
                                if '*' not in range_mapped_by_key:
                                    if allow_range_code == '==':
                                        ...
                                    elif allow_range_code not in range_mapped_by_key:
                                        raise ValueError(
                                            'The application ID "%s" use range not allow by original apps. '
                                            'DATA: %s not in %s.' % (
                                                str(app_id),
                                                str(allow_range_code),
                                                str(range_mapped_by_key)
                                            )
                                        )
                    else:
                        raise ValueError('The application ID "%s" is not found.' % (str(app_id)))
            else:
                raise ValueError('Depends on should be match dict type. DATA: %s.' % (str(app_depend_on)))
        return True

    @classmethod
    def get_app_in_permit_mapping(cls, permit_mapping):
        app_ids = []
        if permit_mapping and isinstance(permit_mapping, dict):
            for permit, data in permit_mapping.items():
                app_depend_on = data.get('app_depends_on', {})
                app_ids += list(set(app_depend_on.keys()))
                cls.check_depends_on_app_correct(app_depend_on)
        return list(set(app_ids))

    @staticmethod
    def not_app_in_depends(depend_ids, mapping_app_ids):
        depend_ids = list(set(depend_ids))
        mapping_app_ids = list(set(mapping_app_ids))
        not_in_apps = []
        for _item_x in mapping_app_ids:
            if _item_x not in depend_ids:
                not_in_apps.append(_item_x)
        return not_in_apps


def check_app_depends_and_mapping():
    errors = []
    for _id, data in Application_data.items():
        app_depend_on = list(set(data.get('app_depend_on', [])))
        permit_mapping = data.get('permit_mapping', {})

        # check app_depend_on compare with app in permit_mapping.
        app_ids = CheckingDependsOnApp.get_app_in_permit_mapping(permit_mapping=permit_mapping)
        if len(app_depend_on) != len(app_ids):
            errors.append(
                {
                    _id: [
                        f"Apps in permit_mapping but not exist in depends on: "
                        f"{', '.join(CheckingDependsOnApp.not_app_in_depends(app_depend_on, app_ids))}",
                    ]
                }
            )

        #

    if errors:
        for err_data in errors:
            print(err_data)
        print('Some errors raise in Application depends!')
        return False
    print('All application depends is correct!')
    return True
