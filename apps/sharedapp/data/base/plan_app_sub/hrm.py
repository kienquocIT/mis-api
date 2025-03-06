from apps.sharedapp.data.base.settings import ApplicationConfigFrame

__all__ = [
    'Application_hrm_data',
]
EMPLOYEE_INFO = {
    "id": "7436c857-ad09-4213-a190-c1c7472e99be",
    "title": "Employee info",
    "code": "employeeinfo",
    "model_code": "employeeinfo",
    "app_label": "hrm",
    "is_workflow": False,
    "allow_permit": True,
    "option_permission": 1,
    "option_allowed": [4],
    "app_depend_on": [
        "af9c6fd3-1815-4d5a-aa24-fca9d095cb7a",  # User
        "e17b9123-8002-4c9b-921b-7722c3c9e3a5",  # Group
        "4cdaabcc-09ae-4c13-bb4e-c606eb335b11",  # Role
    ],
    "permit_mapping": {
        "view": {
            "range": ["4"],
            "app_depends_on": {
                "4cdaabcc-09ae-4c13-bb4e-c606eb335b11": {"view": "4", },  # For summary permit of employee
            },
            "local_depends_on": {},
        },
        "create": {
            "range": ["4"],
            "app_depends_on": {
                "af9c6fd3-1815-4d5a-aa24-fca9d095cb7a": {"view": "4", },
                "e17b9123-8002-4c9b-921b-7722c3c9e3a5": {"view": "4", },
                "4cdaabcc-09ae-4c13-bb4e-c606eb335b11": {"view": "4", },
            },
            "local_depends_on": {
                "view": "4",
            },
        },
        "edit": {
            "range": ["4"],
            "app_depends_on": {
                "af9c6fd3-1815-4d5a-aa24-fca9d095cb7a": {"view": "4", },
                "e17b9123-8002-4c9b-921b-7722c3c9e3a5": {"view": "4", },
                "4cdaabcc-09ae-4c13-bb4e-c606eb335b11": {"view": "4", },
            },
            "local_depends_on": {
                "view": "4",
            },
        },
        "delete": {
            "range": ["4"],
            "app_depends_on": {},
            "local_depends_on": {
                "view": "4",
            },
        },
    },
    "allow_import": False,
}

EMPLOYEE_CONTRACT = {
    "id": "1b8a6f6e-65ec-4769-acaa-465bed2d0523",
    "title": "Employee contract",
    "code": "employeecontract",
    "model_code": "employeecontract",
    "app_label": "hrm",
    "is_workflow": False,
    "allow_permit": True,
    "option_permission": 1,
    "option_allowed": [4],
    "app_depend_on": [],
    "permit_mapping": {
        "view": {
            "range": [],
            "app_depends_on": {},
            "local_depends_on": {},
        },
        "create": {
            "range": [],
            "app_depends_on": {},
            "local_depends_on": {},
        },
        "edit": {
            "range": [],
            "app_depends_on": {},
            "local_depends_on": {},
        },
        "delete": {
            "range": [],
            "app_depends_on": {},
            "local_depends_on": {},
        },
    },
    "allow_import": False,
}

Application_hrm_data = {
    "7436c857-ad09-4213-a190-c1c7472e99be": ApplicationConfigFrame(**EMPLOYEE_INFO).data(
        depend_follow_main=False,
        filtering_inheritor=False,
    ),
    "1b8a6f6e-65ec-4769-acaa-465bed2d0523": ApplicationConfigFrame(**EMPLOYEE_CONTRACT).data(
        depend_follow_main=False,
        filtering_inheritor=False,
    ),
}
