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
    ],
    "permit_mapping": {
        "view": {
            "range": ["1", "2", "3", "4"],
            "app_depends_on": {},
            "local_depends_on": {},
        },
        "create": {
            "range": ["1", "2", "3", "4"],
            "app_depends_on": {},
            "local_depends_on": {},
        },
        "edit": {
            "range": ["1", "2", "3", "4"],
            "app_depends_on": {},
            "local_depends_on": {},
        },
        "delete": {
            "range": ["1", "2", "3", "4"],
            "app_depends_on": {},
            "local_depends_on": {},
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
    ],
    "permit_mapping": {
        "view": {
            "range": ["1", "2", "3", "4"],
            "app_depends_on": {},
            "local_depends_on": {},
        },
        "edit": {
            "range": ["1", "2", "3", "4"],
            "app_depends_on": {},
            "local_depends_on": {},
        },
    },
}
LEAVE_APP_BUSINESS_TRIP = {
    "id": "87ce1662-ca9d-403f-a32e-9553714ebc6d",
    "title": "Business trip",
    "code": "businesstrip",
    "model_code": "businessrequest",
    "app_label": "businesstrip",
    "is_workflow": True,
    "app_depend_on": [
    ],
    "permit_mapping": {
        "view": {
            "range": ["1", "2", "3", "4"],
            "app_depends_on": {},
            "local_depends_on": {},
        },
        "create": {
            "range": ["1", "2", "3", "4"],
            "app_depends_on": {},
            "local_depends_on": {},
        },
        "edit": {
            "range": ["1", "2", "3", "4"],
            "app_depends_on": {},
            "local_depends_on": {},
        },
        "delete": {
            "range": ["1", "2", "3", "4"],
            "app_depends_on": {},
            "local_depends_on": {},
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
    "87ce1662-ca9d-403f-a32e-9553714ebc6d": ApplicationConfigFrame(**LEAVE_APP_BUSINESS_TRIP).data(
        depend_follow_main=False,
        filtering_inheritor=False
    ),
}
