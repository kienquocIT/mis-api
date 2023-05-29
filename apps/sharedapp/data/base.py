__all__ = [
    'SubscriptionPlan_data',
    'Application_data',
    'PlanApplication_data',
    'PermissionApplication_data',
    'ApplicationProperty_data',
    'Currency_data',
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
    "af9c6fd3-1815-4d5a-aa24-fca9d095cb7a": {
        "title": "User",
        "code": "user",
        "app_label": "account",
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
    "284ff7a6-78f2-452e-9826-c2d852a83f81": {
        "plan_id": "395eb68e-266f-45b9-b667-bd2086325522",  # HRM
        "application_id": "4cdaabcc-09ae-4c13-bb4e-c606eb335b11",  # Role
    },
    "499bbc78-ea45-4f2a-b97b-d38ee9e82a9b": {
        "plan_id": "395eb68e-266f-45b9-b667-bd2086325522",  # HRM
        "application_id": "50348927-2c4f-4023-b638-445469c66953",  # Employee
    },
    "65eed348-50d7-4707-857f-1e644e9f549d": {
        "plan_id": "395eb68e-266f-45b9-b667-bd2086325522",  # HRM
        "application_id": "e17b9123-8002-4c9b-921b-7722c3c9e3a5",  # Group
    },
    "6ea04af3-4dda-4da4-9a27-05ef90928176": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "828b785a-8f57-4a03-9f90-e0edf96560d7",  # Contact
    },
    "f1aeea57-85e2-4349-9eb9-cc14aa4c74fd": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "4e48c863-861b-475a-aa5e-97a4ed26f294",  # Account
    },

}

PermissionApplication_data = {  # create & view & edit & delete
    # Account - User
    "a279829a-b842-4bdc-8c2f-edf56e055396": {
        "app_id": "af9c6fd3-1815-4d5a-aa24-fca9d095cb7a",
        "permission": "create__account__user",
    },
    "dcf98d80-bd8f-41d7-a925-3e29e6a4e322": {
        "app_id": "af9c6fd3-1815-4d5a-aa24-fca9d095cb7a",
        "permission": "view__account__user",
    },
    "99e45cf5-47b7-42d4-9514-a53464686187": {
        "app_id": "af9c6fd3-1815-4d5a-aa24-fca9d095cb7a",
        "permission": "edit__account__user",
    },
    "3df85cdd-8254-46a4-9d73-ad15f40938f7": {
        "app_id": "af9c6fd3-1815-4d5a-aa24-fca9d095cb7a",
        "permission": "delete__account__user",
    },
    # HR - Role
    "dbd24785-7ff3-4e81-beb2-ad7f6eee8df9": {
        "app_id": "4cdaabcc-09ae-4c13-bb4e-c606eb335b11",
        "permission": "create__hr__role",
    },
    "43703e75-bd16-4e65-97e5-a90998e0a94d": {
        "app_id": "4cdaabcc-09ae-4c13-bb4e-c606eb335b11",
        "permission": "view__hr__role",
    },
    "c3232101-9853-4706-8100-5b11ace1c145": {
        "app_id": "4cdaabcc-09ae-4c13-bb4e-c606eb335b11",
        "permission": "edit__hr__role",
    },
    "67278d3f-0ff5-40dd-b150-e579764311a6": {
        "app_id": "4cdaabcc-09ae-4c13-bb4e-c606eb335b11",
        "permission": "delete__hr__role",
    },
    # HR - Employee
    "71f2eeaf-55f7-4516-b470-ece3c0dab0c6": {
        "app_id": "50348927-2c4f-4023-b638-445469c66953",
        "permission": "create__hr__employee",
    },
    "2417e931-4912-4ab7-b5c5-6e0655beada2": {
        "app_id": "50348927-2c4f-4023-b638-445469c66953",
        "permission": "view__hr__employee",
    },
    "00af7c1b-803b-4322-b2b6-18998268285b": {
        "app_id": "50348927-2c4f-4023-b638-445469c66953",
        "permission": "edit__hr__employee",
    },
    "425ea59f-1fb2-4165-90fe-1f1707687cba": {
        "app_id": "50348927-2c4f-4023-b638-445469c66953",
        "permission": "delete__hr__employee",
    },
    # HR - Group
    "26b7fb28-cd37-41f6-9147-1f270851f04f": {
        "app_id": "e17b9123-8002-4c9b-921b-7722c3c9e3a5",
        "permission": "create__hr__group",
    },
    "5aa1af15-34b8-4871-8c90-611b7fca9314": {
        "app_id": "e17b9123-8002-4c9b-921b-7722c3c9e3a5",
        "permission": "view__hr__group",
    },
    "8c603c9a-69d7-40c5-83a0-54025971926e": {
        "app_id": "e17b9123-8002-4c9b-921b-7722c3c9e3a5",
        "permission": "edit__hr__group",
    },
    "0a7e66a0-48e0-4b9d-9484-c2170b02b7f2": {
        "app_id": "e17b9123-8002-4c9b-921b-7722c3c9e3a5",
        "permission": "delete__hr__group",
    },
    # SaleData - Contact
    "54c8fbf9-4a53-413f-8cd6-c2a54636c6e3": {
        "app_id": "828b785a-8f57-4a03-9f90-e0edf96560d7",
        "permission": "create__saledata__contact",
    },
    "7ec11953-9c52-4128-bb9a-36b932444a48": {
        "app_id": "828b785a-8f57-4a03-9f90-e0edf96560d7",
        "permission": "view__saledata__contact",
    },
    "ae61b6ed-4142-49e6-89a1-187efcdcd5dd": {
        "app_id": "828b785a-8f57-4a03-9f90-e0edf96560d7",
        "permission": "edit__saledata__contact",
    },
    "c3c509d9-cdd5-42c5-b60b-54567f980dee": {
        "app_id": "828b785a-8f57-4a03-9f90-e0edf96560d7",
        "permission": "delete__saledata__contact",
    },
    # SaleData - Account
    "e40ce783-5909-4967-bcd5-0f1bf4d3e6e8": {
        "app_id": "4e48c863-861b-475a-aa5e-97a4ed26f294",
        "permission": "create__saledata__account",
    },
    "f5e366d2-0e17-4096-863e-b8960271da06": {
        "app_id": "4e48c863-861b-475a-aa5e-97a4ed26f294",
        "permission": "view__saledata__account",
    },
    "87bc9689-febf-446d-a607-7dfb2ae1ec06": {
        "app_id": "4e48c863-861b-475a-aa5e-97a4ed26f294",
        "permission": "edit__saledata__account",
    },
    "57e0fef9-2fd9-4a3d-8d12-aee15a6b03e4": {
        "app_id": "4e48c863-861b-475a-aa5e-97a4ed26f294",
        "permission": "delete__saledata__account",
    },
    #
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

Currency_data = {
    "14bcc332-1089-49f0-9aae-433f361fc848": {
        "title": "Đồng Việt Nam",
        "code": "VND",
        "symbol": "VND",
    },
    "e66f2870-e34f-4cd3-a9eb-78b539e80bdc": {
        "title": "United States Dollar",
        "code": "USD",
        "symbol": "$",
    },
    "6e9b6378-97fb-4b2e-ac28-7b73b2e35635": {
        "title": "Euro",
        "code": "EUR",
        "symbol": "€",
    },
    "84810a69-20cb-44f0-a4f3-d26aeb71eb76": {
        "title": "Swiss Franc",
        "code": "CHF",
        "symbol": "CHF",
    },
    "82944baf-686e-48dd-8233-e450f0a0b83c": {
        "title": "United Kingdom Pounds",
        "code": "GBP",
        "symbol": "£",
    },
    "2589a8fc-b94e-46a1-8148-ecead8f8bffe": {
        "title": "India Rupees",
        "code": "INR",
        "symbol": "₹",
    },
    "c165c3bd-3ed5-40b4-9ff2-64000206c466": {
        "title": "Australian Dollar",
        "code": "AUD",
        "symbol": "AUD",
    },
    "f3cf7feb-f7ef-492a-9362-7163547dcadb": {
        "title": "Canadian Dollar",
        "code": "CAD",
        "symbol": "CAD",
    },
    "98517b06-6d2c-4545-aa92-df0d6669cba5": {
        "title": "South African Rand",
        "code": "ZAR",
        "symbol": "R",
    },
    "6d4f8bce-7ddc-48e3-9597-538106b807b4": {
        "title": "Japanese Yen",
        "code": "JPY",
        "symbol": "JPY",
    },
    "b2c3bd13-cf72-4403-9331-a476e13169b9": {
        "title": "Chinese Yuan Renminbi",
        "code": "CNY",
        "symbol": "CNY",
    },
}
