from .plan_app_sub.base import Application_base_data as _Application_base_data
from .plan_app_sub.crm import Application_crm_data as _Application_crm_data

__all__ = [
    "SubscriptionPlan_data",
    "Application_data",
    "PlanApplication_data",
    "FULL_PERMISSIONS_BY_CONFIGURED",
    "FULL_PLAN_ID",
    "check_app_depends_and_mapping",
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

__Application_crm_data = {
    "828b785a-8f57-4a03-9f90-e0edf96560d7": {
        "title": "Contact",
        "code": "contact",
        "model_code": "contact",
        "app_label": "saledata",
        "is_workflow": True,
        "option_permission": 0,
        "option_allowed": [1, 2, 3, 4],
    },
    "4e48c863-861b-475a-aa5e-97a4ed26f294": {
        "title": "Account",
        "code": "account",
        "model_code": "account",
        "app_label": "saledata",
        "is_workflow": True,
        "option_permission": 0,
        "option_allowed": [1, 2, 3, 4],
    },
    "296a1410-8d72-46a8-a0a1-1821f196e66c": {
        "title": "Opportunity",
        "code": "opportunity",
        "model_code": "opportunity",
        "app_label": "opportunity",
        "is_workflow": True,
        "option_permission": 0,
        "option_allowed": [1, 2, 3, 4],
    },
    "b9650500-aba7-44e3-b6e0-2542622702a3": {
        "title": "Quotation",
        "code": "quotation",
        "model_code": "quotation",
        "app_label": "quotation",
        "is_workflow": True,
        "option_permission": 0,
        "option_allowed": [1, 2, 3, 4],
    },
    "a870e392-9ad2-4fe2-9baa-298a38691cf2": {
        "title": "Sale Order",
        "code": "saleorder",
        "model_code": "saleorder",
        "app_label": "saleorder",
        "is_workflow": True,
        "option_permission": 0,
        "option_allowed": [1, 2, 3, 4],
    },
    "a8badb2e-54ff-4654-b3fd-0d2d3c777538": {
        "title": "Product",
        "code": "product",
        "model_code": "product",
        "app_label": "saledata",
        "is_workflow": False,
        "option_permission": 1,
        "option_allowed": [4],
    },
    "022375ce-c99c-4f11-8841-0a26c85f2fc2": {
        "title": "Expenses",
        "code": "expenses",
        "model_code": "expenses",
        "app_label": "saledata",
        "is_workflow": False,
        "option_permission": 1,
        "option_allowed": [4],
    },
    "80b8cd4f-cfba-4f33-9642-a4dd6ee31efd": {
        "title": "Warehouse",
        "code": "warehouse",
        "model_code": "warehouse",
        "app_label": "saledata",
        "is_workflow": False,
        "option_permission": 1,
        "option_allowed": [4],
    },
    "47e538a8-17e7-43bb-8c7e-dc936ccaf474": {
        "title": "Good receipt",
        "code": "goodreceipt",
        "model_code": "goodreceipt",
        "app_label": "saledata",
        "is_workflow": True,
        "option_permission": 1,
        "option_allowed": [4],
    },
    "3d8ad524-5dd9-4a8b-a7cd-a9a371315a2a": {
        "title": "Picking",
        "code": "orderpickingsub",
        "model_code": "orderpickingsub",
        "app_label": "delivery",
        "is_workflow": False,
        "option_permission": 1,
        "option_allowed": [4],
    },
    "1373e903-909c-4b77-9957-8bcf97e8d6d3": {
        "title": "Delivery",
        "code": "orderdeliverysub",
        "model_code": "orderdeliverysub",
        "app_label": "delivery",
        "is_workflow": True,
        "option_permission": 0,
        "option_allowed": [1, 2, 3, 4],
    },
    "10a5e913-fa51-4127-a632-a8347a55c4bb": {
        "title": "Prices",
        "code": "price",
        "model_code": "price",
        "app_label": "saledata",
        "is_workflow": False,
        "option_permission": 1,
        "option_allowed": [4],
    },
    "e6a00a1a-d4f9-41b7-b0de-bb1efbe8446a": {
        "title": "Shipping",
        "code": "shipping",
        "model_code": "shipping",
        "app_label": "saledata",
        "is_workflow": False,
        "option_permission": 1,
        "option_allowed": [4],
    },
    "f57b9e92-cb01-42e3-b7fe-6166ecd18e9c": {
        "title": "Promotions",
        "code": "promotion",
        "model_code": "promotion",
        "app_label": "promotion",
        "is_workflow": False,
        "option_permission": 1,
        "option_allowed": [4],
    },
    "57725469-8b04-428a-a4b0-578091d0e4f5": {
        "title": "Advance Payment",
        "code": "advancepayment",
        "model_code": "advancepayment",
        "app_label": "cashoutflow",
        "is_workflow": True,
        "option_permission": 0,
        "option_allowed": [1, 2, 3, 4],
    },
    "1010563f-7c94-42f9-ba99-63d5d26a1aca": {
        "title": "Payments",
        "code": "payment",
        "model_code": "payment",
        "app_label": "cashoutflow",
        "is_workflow": True,
        "option_permission": 0,
        "option_allowed": [1, 2, 3, 4],
    },
    "65d36757-557e-4534-87ea-5579709457d7": {
        "title": "Return Advance",
        "code": "returnadvance",
        "model_code": "returnadvance",
        "app_label": "cashoutflow",
        "is_workflow": True,
        "option_permission": 0,
        "option_allowed": [1, 2, 3, 4],
    },
    "e66cfb5a-b3ce-4694-a4da-47618f53de4c": {
        "title": "Task",
        "code": "opportunitytask",
        "model_code": "opportunitytask",
        "app_label": "task",
        "is_workflow": False,
        "option_permission": 0,
        "option_allowed": [1, 2, 3, 4],
        "app_depend_on": [
            "50348927-2c4f-4023-b638-445469c66953",  # Employee
        ],
        "permit_mapping": {
            "view": {
                "range": ["1", "2", "3", "4"],
                "app_depends_on": {
                    "50348927-2c4f-4023-b638-445469c66953": {
                        "view": "4",
                    }
                },
                "local_depends_on": {},
            },
            "create": {
                "range": ["1"],
                "app_depends_on": {
                    "50348927-2c4f-4023-b638-445469c66953": {
                        "view": "4",
                    }
                },
                "local_depends_on": {
                    "view": "4",
                },
            },
            "edit": {
                "range": ["2"],
                "app_depends_on": {
                    "50348927-2c4f-4023-b638-445469c66953": {
                        "view": "4",
                    }
                },
                "local_depends_on": {
                    "view": "4",
                },
            },
            "delete": {
                "range": ["3"],
                "app_depends_on": {
                    "50348927-2c4f-4023-b638-445469c66953": {
                        "view": "4",
                    }
                },
                "local_depends_on": {
                    "view": "4",
                },
            },
        }
    },

    "319356b4-f16c-4ba4-bdcb-e1b0c2a2c124": {
        "title": "Document For Customer",
        "code": "documentforcustomer",
        "model_code": "documentforcustomer",
        "app_label": "opportunity",
        "is_workflow": False,
        "option_permission": 0,
        "option_allowed": [1, 2, 3, 4],
    },

    "14dbc606-1453-4023-a2cf-35b1cd9e3efd": {
        "title": "Call",
        "code": "opportunitycall",
        "model_code": "opportunitycall",
        "app_label": "opportunity",
        "is_workflow": False,
        "option_permission": 0,
        "option_allowed": [1, 2, 3, 4],
    },

    "dec012bf-b931-48ba-a746-38b7fd7ca73b": {
        "title": "Email",
        "code": "opportunityemail",
        "model_code": "opportunityemail",
        "app_label": "opportunity",
        "is_workflow": False,
        "option_permission": 0,
        "option_allowed": [1, 2, 3, 4],
    },

    "2fe959e3-9628-4f47-96a1-a2ef03e867e3": {
        "title": "Metting With Customer",
        "code": "meetingwithcustomer",
        "model_code": "meetingwithcustomer",
        "app_label": "opportunity",
        "is_workflow": False,
        "option_permission": 0,
        "option_allowed": [1, 2, 3, 4],
    },

    "31c9c5b0-717d-4134-b3d0-cc4ca174b168": {
        "title": "Contract",
        "code": "contract",
        "model_code": "contract",
        "app_label": "contract",
        "is_workflow": False,
        "option_permission": 0,
        "option_allowed": [1, 2, 3, 4],
    },

    "a0d0a456-47b8-47ff-8f99-d9f3353a68ae": {
        "title": "Purchase Request",
        "code": "purchaserequest",
        "model_code": "purchaserequest",
        "app_label": "purchasing",
        "is_workflow": True,
        "option_permission": 0,
        "option_allowed": [1, 2, 3, 4],
    },
    "d78bd5f3-8a8d-48a3-ad62-b50d576ce173": {
        "title": "Purchase Quotation Request",
        "code": "purchasequotationrequest",
        "model_code": "purchasequotationrequest",
        "app_label": "purchasing",
        "is_workflow": True,
        "option_permission": 0,
        "option_allowed": [1, 2, 3, 4],
    },
    "f52a966a-2eb2-4851-852d-eff61efeb896": {
        "title": "Purchase Quotation",
        "code": "purchasequotation",
        "model_code": "purchasequotation",
        "app_label": "purchasing",
        "is_workflow": True,
        "option_permission": 0,
        "option_allowed": [1, 2, 3, 4],
    },
    "81a111ef-9c32-4cbd-8601-a3cce884badb": {
        "title": "Purchase Order",
        "code": "purchaseorder",
        "model_code": "purchaseorder",
        "app_label": "purchasing",
        "is_workflow": True,
        "option_permission": 0,
        "option_allowed": [1, 2, 3, 4],
    },
}

Application_data = {
    **_Application_base_data,
    **_Application_crm_data,
}

_PlanApplication_base_data = {
    "144e2a57-f953-4030-9158-28a12c4eb968": {
        "plan_id": "e42e93b6-5a7d-4d75-b6da-b288045058df",  # Base
        "application_id": "269f4421-04d8-4528-bc95-148ffd807235",  # Company
    },
    "a163f133-4a31-4a26-b192-dfbaebc80090": {
        "plan_id": "e42e93b6-5a7d-4d75-b6da-b288045058df",  # Base
        "application_id": "af9c6fd3-1815-4d5a-aa24-fca9d095cb7a",  # User
    },
    "5071bb63-8f72-43b4-9a4b-40e690c49299": {
        "plan_id": "e42e93b6-5a7d-4d75-b6da-b288045058df",  # Base
        "application_id": "50348927-2c4f-4023-b638-445469c66953",  # Employee
    },
    "e7cd78dd-3429-463c-b8ef-39679bb56bc7": {
        "plan_id": "e42e93b6-5a7d-4d75-b6da-b288045058df",  # Base
        "application_id": "4cdaabcc-09ae-4c13-bb4e-c606eb335b11",  # Role
    },
    "7ba3b025-7a6b-4faf-9f7e-4f8906a846de": {
        "plan_id": "e42e93b6-5a7d-4d75-b6da-b288045058df",  # Base
        "application_id": "e17b9123-8002-4c9b-921b-7722c3c9e3a5",  # Group
    },
    "c1df4ed4-8f9d-40cf-a37b-02de87ccb0e0": {
        "plan_id": "e42e93b6-5a7d-4d75-b6da-b288045058df",  # Base
        "application_id": "71393401-e6e7-4a00-b481-6097154efa64",  # Workflow
    },
}

_PlanApplication_hrm_data = {
}

_PlanApplication_sale_data = {
    "6ea04af3-4dda-4da4-9a27-05ef90928176": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "828b785a-8f57-4a03-9f90-e0edf96560d7",  # Contact
    },
    "f1aeea57-85e2-4349-9eb9-cc14aa4c74fd": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "4e48c863-861b-475a-aa5e-97a4ed26f294",  # Account
    },
    "b6eb6255-9798-43b1-9985-fa4c76b3a74c": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "a870e392-9ad2-4fe2-9baa-298a38691cf2",  # Sale Order
    },
    "9756ac42-aa94-4751-9348-20d7af10c6c9": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "b9650500-aba7-44e3-b6e0-2542622702a3",  # Quotation
    },
    "d7d7e2ef-4fab-4937-8f1e-82691ddfbfaa": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "3d8ad524-5dd9-4a8b-a7cd-a9a371315a2a",  # Picking
    },
    "0c292319-e66d-41b0-86a4-4eec86d0e313": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "1373e903-909c-4b77-9957-8bcf97e8d6d3",  # Delivery
    },
    "bd17c9bd-a7b8-4603-9b8f-d17da94b9aae": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "e66cfb5a-b3ce-4694-a4da-47618f53de4c",  # Task
    },
    "63f83f34-b0e7-4461-8c19-609824ef8d1e": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "47e538a8-17e7-43bb-8c7e-dc936ccaf474",  # Good-Receipt
    },
    "448343d8-c5a3-4aac-bdc6-d56013ac8fe3": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "319356b4-f16c-4ba4-bdcb-e1b0c2a2c124",  # Document For Customer
    },
    "0c6c8a31-1b03-4d88-ba36-ea690a7d3c0e": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "296a1410-8d72-46a8-a0a1-1821f196e66c",  # Opportunity
    },
    "aa6d7abb-c177-4531-873f-9233c7f98fa1": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "a0d0a456-47b8-47ff-8f99-d9f3353a68ae",  # Purchase Request
    },
    "b24a1795-5f8c-4b08-a998-cfed8618b714": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "d78bd5f3-8a8d-48a3-ad62-b50d576ce173",  # Purchase Quotation Request
    },
    "5ae426ab-1b3f-4a05-8117-77d136c13c8f": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "f52a966a-2eb2-4851-852d-eff61efeb896",  # Purchase Quotation
    },
    "375cb89c-7dd5-40ec-a6aa-93f9a87ba656": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "81a111ef-9c32-4cbd-8601-a3cce884badb",  # Purchase Order
    },
    "f15e4a2f-2b1b-4a80-a6fb-53776d563bcb": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "fbff9b3f-f7c9-414f-9959-96d3ec2fb8bf",  # Purchase request
    },
    "be9db37d-4d8a-4b2c-86f1-18a15f08d6d4": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "f57b9e92-cb01-42e3-b7fe-6166ecd18e9c",  # Promotion
    },
    "0a782095-fd0d-45e6-ae75-cf8904781d57": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "e6a00a1a-d4f9-41b7-b0de-bb1efbe8446a",  # Shipping
    },
    "1cc123a1-d6de-4e8a-b0b8-30c6e27a637c": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "fbff9b3f-f7c9-414f-9959-96d3ec2fb8bf",  # Expense Item
    },
    "52f8024f-b396-4adb-a368-570745914f6a": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "3407d35d-27ce-407e-8260-264574a216e3",  # Payment Term
    },
}

PlanApplication_data = {
    **_PlanApplication_base_data,
    **_PlanApplication_hrm_data,
    **_PlanApplication_sale_data,
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
    def get_sub(cls, range_current, app_depends_on, local_depends_on, app_data, plan_data):
        result = []

        for app_id, config_data in app_depends_on.items():
            app_depend_data = {'id': app_id, **Application_data[app_id]}
            for permit_code, range_code in local_depends_on.items():
                result.append(
                    cls.parse_one_permit_allow(
                        app_data=app_depend_data,
                        plan_data=plan_data,
                        range_code=range_current if range_code == '==' else range_code,
                        **cls.parse_permit_code_to_dict(permit_code),
                        sub_data=[],
                    )
                )

        for permit_code, range_code in local_depends_on.items():
            result.append(
                cls.parse_one_permit_allow(
                    app_data=app_data,
                    plan_data=plan_data,
                    range_code=range_current if range_code == '==' else range_code,
                    **cls.parse_permit_code_to_dict(permit_code),
                    sub_data=[],
                )
            )

        return result

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
                        sub_data=cls.get_sub(
                            range_current=range_code,
                            app_depends_on=config.get('app_depends_on', {}),
                            local_depends_on=config.get('local_depends_on', {}),
                            app_data=app_data,
                            plan_data=plan_data,
                        ),
                    )
                )
        return result

    @classmethod
    def full_permit(cls):
        result = []
        for _key, value in PlanApplication_data.items():
            plan_data = {'id': value['plan_id'], **SubscriptionPlan_data[value['plan_id']]}
            app_data = {'id': value['application_id'], **Application_data[value['application_id']]}
            result += cls.get_by_app(app_data=app_data, plan_data=plan_data)
        return result


def get_full_permissions_by_configured():
    return FullPermitHandle.full_permit()


FULL_PERMISSIONS_BY_CONFIGURED = get_full_permissions_by_configured()
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
