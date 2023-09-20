from apps.sharedapp.data.base.settings import ApplicationConfigFrame

__all__ = [
    'Application_eOffice_data'
]

LEAVE_APP_CONFIG = {
    "id": "baff033a-c416-47e1-89af-b6653534f06e",
    "title": "Leave",
    "code": "leave",
    "model_code": "leave",
    "app_label": "eoffice",
    "is_workflow": True,
    "app_depend_on": [
        "50348927-2c4f-4023-b638-445469c66953",  # Employee
    #     "a870e392-9ad2-4fe2-9baa-298a38691cf2",  # Sale Order
    #     "b9650500-aba7-44e3-b6e0-2542622702a3",  # Quotation
    #     "296a1410-8d72-46a8-a0a1-1821f196e66c",  # Opportunity
    #     "4e48c863-861b-475a-aa5e-97a4ed26f294",  # Saledata.Account
    #     "022375ce-c99c-4f11-8841-0a26c85f2fc2",  # Expenses
    ],
    "permit_mapping": {
        "view": {
            "range": ["1", "2", "3", "4"],
            "app_depends_on": {},
            "local_depends_on": {},
        },
        "create": {
            "range": ["1", "2", "3", "4"],
            "app_depends_on": {
                # "50348927-2c4f-4023-b638-445469c66953": {
                #     "view": "4"
                # },
                # "a870e392-9ad2-4fe2-9baa-298a38691cf2": {
                #     "view": "4",
                # },
                # "b9650500-aba7-44e3-b6e0-2542622702a3": {
                #     "view": "4",
                # },
                # "296a1410-8d72-46a8-a0a1-1821f196e66c": {
                #     "view": "4",
                # },
                # "4e48c863-861b-475a-aa5e-97a4ed26f294": {
                #     "view": "==",
                # },
                # "022375ce-c99c-4f11-8841-0a26c85f2fc2": {
                #     "view": "4",
                # },
            },
            "local_depends_on": {
                "view": "==",
            },
        },
        "edit": {
            "range": ["1", "2", "3", "4"],
            "app_depends_on": {
                # "50348927-2c4f-4023-b638-445469c66953": {
                #     "view": "4"
                # },
                # "a870e392-9ad2-4fe2-9baa-298a38691cf2": {
                #     "view": "4",
                # },
                # "b9650500-aba7-44e3-b6e0-2542622702a3": {
                #     "view": "4",
                # },
                # "296a1410-8d72-46a8-a0a1-1821f196e66c": {
                #     "view": "4",
                # },
                # "4e48c863-861b-475a-aa5e-97a4ed26f294": {
                #     "view": "==",
                # },
                # "022375ce-c99c-4f11-8841-0a26c85f2fc2": {
                #     "view": "4",
                # },
            },
            "local_depends_on": {
                "view": "==",
            },
        },
        "delete": {
            "range": ["1", "2", "3", "4"],
            "app_depends_on": {},
            "local_depends_on": {
                "view": "==",
            },
        },
    },
}

Application_eOffice_data = {
    "baff033a-c416-47e1-89af-b6653534f06e": ApplicationConfigFrame(**LEAVE_APP_CONFIG).data,
}
