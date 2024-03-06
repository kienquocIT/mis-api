from apps.sharedapp.data.base.settings import ApplicationConfigFrame

__all__ = [
    'Application_base_data',
]

BASTION_APP_CONFIG = {
    "id": "ba2ef9f1-63f4-4cfb-ae2f-9dee6a56da68",
    "title": "Bastion",
    "code": "bastion",
    "model_code": "system",
    "app_label": "system",
    "is_workflow": False,
    "option_permission": 1,
    "option_allowed": [],
    "app_depend_on": [],
    "permit_mapping": {},
}

WORKFLOW_APP_CONFIG = {
    "id": "71393401-e6e7-4a00-b481-6097154efa64",
    "title": "Workflow",
    "code": "workflow",
    "model_code": "workflow",
    "app_label": "workflow",
    "is_workflow": False,
    "option_permission": 1,
    "option_allowed": [4],
    "app_depend_on": [
        "50348927-2c4f-4023-b638-445469c66953",  # Employee
    ],
    "permit_mapping": {
        "view": {
            "range": ["4"],
            "app_depends_on": {
                "50348927-2c4f-4023-b638-445469c66953": {
                    "view": "4",
                }
            },
            "local_depends_on": {},
            "opp": {},
            "prj": {},
        },
        "create": {
            "range": ["4"],
            "app_depends_on": {
                "50348927-2c4f-4023-b638-445469c66953": {
                    "view": "4",
                }
            },
            "local_depends_on": {
                "view": "4",
            },
            "opp": {
                "range": ["4"],
                "app_depends_on": {},
                "local_depends_on": {},
            },
        },
        "edit": {
            "range": ["1", "4"],
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
            "range": ["1", "4"],
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
}

EMPLOYEE_APP_CONFIG = {
    "id": "50348927-2c4f-4023-b638-445469c66953",
    "title": "Employee",
    "code": "employee",
    "model_code": "employee",
    "app_label": "hr",
    "is_workflow": False,
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
    }
}

COMPANY_APP_CONFIG = {
    "id": "269f4421-04d8-4528-bc95-148ffd807235",
    "title": "Company",
    "code": "company",
    "model_code": "company",
    "app_label": "company",
    "is_workflow": False,
    "option_permission": 1,
    "option_allowed": [4],
}

USER_APP_CONFIG = {
    "id": "af9c6fd3-1815-4d5a-aa24-fca9d095cb7a",
    "title": "User",
    "code": "user",
    "model_code": "user",
    "app_label": "account",
    "is_workflow": False,
    "option_permission": 1,
    "option_allowed": [4],
    "app_depend_on": [
        "269f4421-04d8-4528-bc95-148ffd807235",  # Company
    ],
    "permit_mapping": {
        "view": {
            "range": ["4"],
            "app_depends_on": {},
            "local_depends_on": {},
        },
        "create": {
            "range": ["4"],
            "app_depends_on": {
                "269f4421-04d8-4528-bc95-148ffd807235": {"view": "4"},
            },
            "local_depends_on": {
                "view": "4",
            },
        },
        "edit": {
            "range": ["4"],
            "app_depends_on": {
                "269f4421-04d8-4528-bc95-148ffd807235": {"view": "4"},
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
    "allow_import": True,
}

ROLE_APP_CONFIG = {
    "id": "4cdaabcc-09ae-4c13-bb4e-c606eb335b11",
    "title": "Role",
    "code": "role",
    "model_code": "role",
    "app_label": "hr",
    "is_workflow": False,
    "option_permission": 1,
    "option_allowed": [4],
    "app_depend_on": [
        "50348927-2c4f-4023-b638-445469c66953",  # Employee
    ],
    "permit_mapping": {
        "view": {
            "range": ["4"],
            "app_depends_on": {},
            "local_depends_on": {},
        },
        "create": {
            "range": ["4"],
            "app_depends_on": {
                "50348927-2c4f-4023-b638-445469c66953": {
                    "view": "4",
                },
            },
            "local_depends_on": {
                "view": "4",
            },
        },
        "edit": {
            "range": ["4"],
            "app_depends_on": {
                "50348927-2c4f-4023-b638-445469c66953": {
                    "view": "4",
                },
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
}

GROUP_APP_CONFIG = {
    "id": "e17b9123-8002-4c9b-921b-7722c3c9e3a5",
    "title": "Group",
    "code": "group",
    "model_code": "group",
    "app_label": "hr",
    "is_workflow": False,
    "option_permission": 1,
    "option_allowed": [4],
    "app_depend_on": [
        "50348927-2c4f-4023-b638-445469c66953",  # Employee
    ],
    "permit_mapping": {
        "view": {
            "range": ["4"],
            "app_depends_on": {},
            "local_depends_on": {},
        },
        "create": {
            "range": ["4"],
            "app_depends_on": {
                "50348927-2c4f-4023-b638-445469c66953": {
                    "view": "4",
                },
            },
            "local_depends_on": {
                "view": "4",
            },
        },
        "edit": {
            "range": ["4"],
            "app_depends_on": {
                "50348927-2c4f-4023-b638-445469c66953": {
                    "view": "4",
                },
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
}

Application_base_data = {
    "ba2ef9f1-63f4-4cfb-ae2f-9dee6a56da68": ApplicationConfigFrame(**BASTION_APP_CONFIG).data(),
    "269f4421-04d8-4528-bc95-148ffd807235": ApplicationConfigFrame(**COMPANY_APP_CONFIG).data(
        depend_follow_main=False,
        filtering_inheritor=False,
    ),
    "af9c6fd3-1815-4d5a-aa24-fca9d095cb7a": ApplicationConfigFrame(**USER_APP_CONFIG).data(
        depend_follow_main=False,
        filtering_inheritor=False
    ),
    "50348927-2c4f-4023-b638-445469c66953": ApplicationConfigFrame(**EMPLOYEE_APP_CONFIG).data(
        depend_follow_main=False,
        filtering_inheritor=False,
    ),
    "4cdaabcc-09ae-4c13-bb4e-c606eb335b11": ApplicationConfigFrame(**ROLE_APP_CONFIG).data(
        depend_follow_main=False,
        filtering_inheritor=False,
    ),
    "e17b9123-8002-4c9b-921b-7722c3c9e3a5": ApplicationConfigFrame(**GROUP_APP_CONFIG).data(
        depend_follow_main=False,
        filtering_inheritor=False,
    ),
    "71393401-e6e7-4a00-b481-6097154efa64": ApplicationConfigFrame(**WORKFLOW_APP_CONFIG).data(
        depend_follow_main=False,
        filtering_inheritor=False,
    ),
}
