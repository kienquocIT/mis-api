__all__ = [
    'SubscriptionPlan_data',
    'Application_data',
    'PlanApplication_data',
    'PermissionApplication_data',
    'ApplicationProperty_data'
]

SubscriptionPlan_data = {
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
    "196d5b50-ec24-4849-ad09-f14e33c663aa": {
        "title": "User",
        "code": "user",
        "app_label": "account"
    },
    "4cdaabcc-09ae-4c13-bb4e-c606eb335b11": {
        "title": "Role",
        "code": "role",
        "app_label": 'hr'
    },
    "50348927-2c4f-4023-b638-445469c66953": {
        "title": "Employee",
        "code": "employee",
        "app_label": 'hr'
    },
    "e17b9123-8002-4c9b-921b-7722c3c9e3a5": {
        "title": "Group",
        "code": "group",
        "app_label": 'hr'
    },
    "828b785a-8f57-4a03-9f90-e0edf96560d7": {
        "title": "Contact",
        "code": "contact",
        'app_label': 'saledata',
    },
    "4e48c863-861b-475a-aa5e-97a4ed26f294": {
        "title": "Account",
        "code": "account",
        'app_label': 'saledata',
    },
}

PlanApplication_data = {
    "f06c4bfa-29b4-4039-b4c6-94304ae5c0ae": {
        "plan_id": "395eb68e-266f-45b9-b667-bd2086325522",  # HRM
        "application_id": "4cdaabcc-09ae-4c13-bb4e-c606eb335b11",
    },
    "f1493708-4e14-472e-9374-081a3505210f": {
        "plan_id": "395eb68e-266f-45b9-b667-bd2086325522",  # HRM
        "application_id": "50348927-2c4f-4023-b638-445469c66953",
    },
    "f42a27ff-aa82-4171-b171-bf729c94679c": {
        "plan_id": "395eb68e-266f-45b9-b667-bd2086325522",  # HRM
        "application_id": "e17b9123-8002-4c9b-921b-7722c3c9e3a5",
    },
    "34346b2e-e705-4ded-85cc-144e7e856a60": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale
        "application_id": "828b785a-8f57-4a03-9f90-e0edf96560d7",
    },
    "539c736c-da5f-409c-aa9e-1c8bc15ac3fa": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale
        "application_id": "4e48c863-861b-475a-aa5e-97a4ed26f294",
    },
}

PermissionApplication_data = {
    # user
    "bc0a5ed6-51d8-4974-b3a9-4ee55afa3b98": {
        'app_id': "196d5b50-ec24-4849-ad09-f14e33c663aa",
        'permission': "create__account__user",
    },
    "c31401de-9531-41a8-b030-f7e052488e42": {
        'app_id': "196d5b50-ec24-4849-ad09-f14e33c663aa",
        'permission': "view__account__user",
    },
    "ebf5fd9e-1728-4d82-9742-a1bed461009d": {
        'app_id': "196d5b50-ec24-4849-ad09-f14e33c663aa",
        'permission': "edit__account__user",
    },
    "b12fb40b-839a-4826-8992-07f94f339e37": {
        'app_id': "196d5b50-ec24-4849-ad09-f14e33c663aa",
        'permission': "delete__account__user",
    },
    # hr_role
    "94530e1d-e4ac-49eb-8eb3-eec85be68a59": {
        "app_id": "4cdaabcc-09ae-4c13-bb4e-c606eb335b11",
        "permission": "create__hr__role",
    },
    "7113644c-32c6-4a9b-9e8a-e0f2f3f6106f": {
        "app_id": "4cdaabcc-09ae-4c13-bb4e-c606eb335b11",
        "permission": "view__hr__role",
    },
    "100a1c55-1984-4e21-9239-d6e487892ac6": {
        "app_id": "4cdaabcc-09ae-4c13-bb4e-c606eb335b11",
        "permission": "edit__hr__role",
    },
    "c5d082a3-70de-4efe-9ed1-edd7ddbbade4": {
        "app_id": "4cdaabcc-09ae-4c13-bb4e-c606eb335b11",
        "permission": "delete__hr__role",
    },
    # hr_employee
    "af3d66b7-22b7-4928-8eeb-6065ee6c7749": {
        "app_id": "50348927-2c4f-4023-b638-445469c66953",
        "permission": "create__hr__employee",
    },
    "b2f13806-c765-42ac-ae01-bb3da95e54ef": {
        "app_id": "50348927-2c4f-4023-b638-445469c66953",
        "permission": "view__hr__employee",
    },
    "0fdc526e-a836-42c2-9a0d-dd65a66ce61a": {
        "app_id": "50348927-2c4f-4023-b638-445469c66953",
        "permission": "edit__hr__employee",
    },
    "9a647881-7f67-4458-8c20-c4700abf0e50": {
        "app_id": "50348927-2c4f-4023-b638-445469c66953",
        "permission": "delete__hr__employee",
    },
    # hr_group
    "92054b35-23c0-46c1-817f-26125bfb4e19": {
        "app_id": "e17b9123-8002-4c9b-921b-7722c3c9e3a5",
        "permission": "create__hr__group",
    },
    "1a26e419-6fe2-4f6e-9e14-25b4a2451593": {
        "app_id": "e17b9123-8002-4c9b-921b-7722c3c9e3a5",
        "permission": "view__hr__group",
    },
    "02bce6db-4b09-4dbb-b8c8-8f58ae4d169a": {
        "app_id": "e17b9123-8002-4c9b-921b-7722c3c9e3a5",
        "permission": "edit__hr__group",
    },
    "e6cbcce3-b7d7-464e-a0cc-6d9bc737899f": {
        "app_id": "e17b9123-8002-4c9b-921b-7722c3c9e3a5",
        "permission": "delete__hr__group",
    },
    # saledata_contact
    '61acb5ee-cf53-4dec-b476-9635ae002075': {
        'id': '61acb5ee-cf53-4dec-b476-9635ae002075',
        'app_id': '828b785a-8f57-4a03-9f90-e0edf96560d7',
        'permission': 'create__saledata__contact',
    },
    '87158af6-e829-4550-96d9-dafadeab71d5': {
        'id': '87158af6-e829-4550-96d9-dafadeab71d5',
        'app_id': '828b785a-8f57-4a03-9f90-e0edf96560d7',
        'permission': 'view__saledata__contact',
    },
    '0e77a049-d9c3-4253-89d2-7df8fc9438ac': {
        'id': '0e77a049-d9c3-4253-89d2-7df8fc9438ac',
        'app_id': '828b785a-8f57-4a03-9f90-e0edf96560d7',
        'permission': 'edit__saledata__contact',
    },
    '29cc98c0-cd5a-4232-b852-5b057206bf6a': {
        'id': '29cc98c0-cd5a-4232-b852-5b057206bf6a',
        'app_id': '828b785a-8f57-4a03-9f90-e0edf96560d7',
        'permission': 'delete__saledata__contact',
    },
    # saledata_account
    '584b6eb9-02fa-4c3d-aae4-3d69e9dc88db': {
        'id': '584b6eb9-02fa-4c3d-aae4-3d69e9dc88db',
        'app_id': '4e48c863-861b-475a-aa5e-97a4ed26f294',
        'permission': 'view__saledata__account',
    },
    '4715941a-fc6c-480f-9d8d-e39a189e86b7': {
        'id': '4715941a-fc6c-480f-9d8d-e39a189e86b7',
        'app_id': '4e48c863-861b-475a-aa5e-97a4ed26f294',
        'permission': 'create__saledata__account',
    },
    'fb9f971b-7f08-4322-8753-fadd3e3fa2fd': {
        'id': 'fb9f971b-7f08-4322-8753-fadd3e3fa2fd',
        'app_id': '4e48c863-861b-475a-aa5e-97a4ed26f294',
        'permission': 'edit__saledata__account',
    },
    '56d8ffcc-5438-4376-8665-f7370417eb1b': {
        'id': '56d8ffcc-5438-4376-8665-f7370417eb1b',
        'app_id': '4e48c863-861b-475a-aa5e-97a4ed26f294',
        'permission': 'delete__saledata__account',
    },
}

ApplicationProperty_data = {
    # Employee
    'fc7fcfcc-5294-4c2f-bdcb-fa0d8076d211': {
        'application_id': '50348927-2c4f-4023-b638-445469c66953',
        'title': 'first name',
        'code': 'first_name',
        'type': 1,
    },
    '9a17bbfa-f555-4996-957c-e2437ecc41ab': {
        'application_id': '50348927-2c4f-4023-b638-445469c66953',
        'title': 'last name',
        'code': 'last_name',
        'type': 1,
    },
    'e35a0c33-0482-486a-b45d-0eacde759242': {
        'application_id': '50348927-2c4f-4023-b638-445469c66953',
        'title': 'email',
        'code': 'email',
        'type': 1,
    },
    '3358a14e-12c6-417b-bc7e-bce1538cd83f': {
        'application_id': '50348927-2c4f-4023-b638-445469c66953',
        'title': 'phone',
        'code': 'phone',
        'type': 1,
    },
    '6b6713e1-3d0b-415e-ba91-4cdcf12ec2db': {
        'application_id': '50348927-2c4f-4023-b638-445469c66953',
        'title': 'code',
        'code': 'code',
        'type': 1,
    },
    '757f8311-793c-4e41-a24b-d1651354ae9a': {
        'application_id': '50348927-2c4f-4023-b638-445469c66953',
        'title': 'user',
        'code': 'user',
        'type': 5,
        'content_type': 'account_User',
        'properties': {
            "dropdown_list": {
                "url": "/account/users/api",
                "prefix": "user_list",
                "multiple": "false"
            }
        },
    },
    'ab9e114a-47ed-4cc4-9a4e-89ffa54afa07': {
        'application_id': '50348927-2c4f-4023-b638-445469c66953',
        'title': 'group',
        'code': 'group',
        'type': 5,
        'content_type': 'hr_Group',
        'properties': {
            "dropdown_list": {
                "url": "/hr/group/api",
                "prefix": "group_list",
                "multiple": "false"
            }
        },
    },
    'f205394a-8bc2-4d43-8d14-78524d1fae56': {
        'application_id': '50348927-2c4f-4023-b638-445469c66953',
        'title': 'employee inherit',
        'code': 'employee_inherit',
        'type': 5,
        'content_type': 'hr_Employee',
        'properties': {
            "dropdown_list": {
                "url": "/hr/employee/api",
                "prefix": "employee_list",
                "multiple": "false"
            }
        },
    },
    '1497e99f-89e2-4632-b698-cd4ab3f22d19': {
        'application_id': '50348927-2c4f-4023-b638-445469c66953',
        'title': 'date joined',
        'code': 'date_joined',
        'type': 2,
    },
    '3d8ea97e-6b9c-43e3-a584-369cfe4bdfaf': {
        'application_id': '50348927-2c4f-4023-b638-445469c66953',
        'title': 'date of birth',
        'code': 'dob',
        'type': 2,
    },
}
