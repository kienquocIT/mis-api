__all__ = [
    "SubscriptionPlan_data",
    "Application_data",
    "PlanApplication_data",
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
        "is_workflow": False,
    },
    "4cdaabcc-09ae-4c13-bb4e-c606eb335b11": {
        "title": "Role",
        "code": "role",
        "app_label": "hr",
        "is_workflow": False,
    },
    "50348927-2c4f-4023-b638-445469c66953": {
        "title": "Employee",
        "code": "employee",
        "app_label": "hr",
        "is_workflow": False,
    },
    "e17b9123-8002-4c9b-921b-7722c3c9e3a5": {
        "title": "Group",
        "code": "group",
        "app_label": "hr",
        "is_workflow": False,
    },
    "828b785a-8f57-4a03-9f90-e0edf96560d7": {
        "title": "Contact",
        "code": "contact",
        "app_label": "saledata",
        "is_workflow": True,
    },
    "4e48c863-861b-475a-aa5e-97a4ed26f294": {
        "title": "Account",
        "code": "account",
        "app_label": "saledata",
        "is_workflow": True,
    },
    "a870e392-9ad2-4fe2-9baa-298a38691cf2": {
        "title": "Sale Order",
        "code": "saleorder",
        "app_label": "saleorder",
        "is_workflow": True,
    },
    "b9650500-aba7-44e3-b6e0-2542622702a3": {
        "title": "Quotation",
        "code": "quotation",
        "app_label": "quotation",
    },
    "3d8ad524-5dd9-4a8b-a7cd-a9a371315a2a": {
        "title": "Picking",
        "code": "orderpickingsub",
        "app_label": "delivery",
        "is_workflow": True,
    },
    "1373e903-909c-4b77-9957-8bcf97e8d6d3": {
        "title": "Delivery",
        "code": "orderdeliverysub",
        "app_label": "delivery",
        "is_workflow": True,
    },
    "296a1410-8d72-46a8-a0a1-1821f196e66c": {
        "title": "Opportunity",
        "code": "opportunity",
        "app_label": "opportunity",
    },
    "e66cfb5a-b3ce-4694-a4da-47618f53de4c": {
        "title": "Task",
        "code": "task",
        "app_label": "task",
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
}
