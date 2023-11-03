from apps.sharedapp.data.base.settings import ApplicationConfigFrame

__all__ = [
    'Application_eOffice_data'
]

LEAVE_APP_CONFIG = {
    "id": "baff033a-c416-47e1-89af-b6653534f06e",
    "title": "Leave",
    "code": "leaverequest",
    "model_code": "leaverequest",
    "app_label": "leave",
    "is_workflow": True,
    "app_depend_on": [
        "50348927-2c4f-4023-b638-445469c66953",  # Employee
        "7738935a-0442-4fd4-a7ff-d06a22aaeccf",  # Leave available
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
                "50348927-2c4f-4023-b638-445469c66953": {
                    "view": "4"
                },
                "7738935a-0442-4fd4-a7ff-d06a22aaeccf": {
                    "view": "4",
                },
            },
            "local_depends_on": {
                "view": "==",
            },
        },
        "edit": {
            "range": ["1", "2", "3", "4"],
            "app_depends_on": {
                "50348927-2c4f-4023-b638-445469c66953": {
                    "view": "4"
                },
                "7738935a-0442-4fd4-a7ff-d06a22aaeccf": {
                    "view": "4",
                },
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
LEAVE_APP_AVAILABLE = {
    "id": "7738935a-0442-4fd4-a7ff-d06a22aaeccf",
    "title": "Leave available",
    "code": "leaveavailable",
    "model_code": "leaveavailable",
    "app_label": "leave",
    "is_workflow": False,
    "app_depend_on": [
        "50348927-2c4f-4023-b638-445469c66953",  # Employee
    ],
    "permit_mapping": {
        "view": {
            "range": ["1", "2", "3", "4"],
            "app_depends_on": {
                "50348927-2c4f-4023-b638-445469c66953": {
                    "view": "==",
                },
            },
            "local_depends_on": {},
        },
        "edit": {
            "range": ["1", "2", "3", "4"],
            "app_depends_on": {
                "50348927-2c4f-4023-b638-445469c66953": {
                    "view": "4"
                },
            },
            "local_depends_on": {
                "view": "==",
            },
        },
    },
}

Application_eOffice_data = {
    "baff033a-c416-47e1-89af-b6653534f06e": ApplicationConfigFrame(**LEAVE_APP_CONFIG).data(
        depend_follow_main=False,
        filtering_inheritor=True,
    ),
    "7738935a-0442-4fd4-a7ff-d06a22aaeccf": ApplicationConfigFrame(**LEAVE_APP_AVAILABLE).data(
        depend_follow_main=False,
        filtering_inheritor=False
    ),
}
