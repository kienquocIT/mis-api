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
BUSINESS_TRIP_REQUEST = {
    "id": "87ce1662-ca9d-403f-a32e-9553714ebc6d",
    "title": "Business trip",
    "code": "businessrequest",
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
ASSET_TOOLS_PROVIDE = {
    "id": "55ba3005-6ccc-4807-af27-7cc45e99e3f6",
    "title": "Asset, Tools Provide",
    "code": "assettoolsprovide",
    "model_code": "assettoolsprovide",
    "app_label": "assettools",
    "is_workflow": True,
    "app_depend_on": [
        "a8badb2e-54ff-4654-b3fd-0d2d3c777538",  # Product
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
                "a8badb2e-54ff-4654-b3fd-0d2d3c777538": {"view": "4", },
            },
            "local_depends_on": {},
        },
        "edit": {
            "range": ["1", "2", "3", "4"],
            "app_depends_on": {
                "a8badb2e-54ff-4654-b3fd-0d2d3c777538": {"view": "4", },},
            "local_depends_on": {},
        },
        "delete": {
            "range": ["1", "2", "3", "4"],
            "app_depends_on": {},
            "local_depends_on": {},
        },
    },
}
MEETING_SCHEDULE = {
    "id": "6078deaa-96b3-4743-97e3-5457454fa7aa",
    "title": "Meeting Schedule",
    "code": "meetingschedule",
    "model_code": "meetingschedule",
    "app_label": "meetingschedule",
    "is_workflow": True,
    "app_depend_on": [
        "4e48c863-861b-475a-aa5e-97a4ed26f294",  # Saledata.Account
        "50348927-2c4f-4023-b638-445469c66953",  # Employee
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
                "4e48c863-861b-475a-aa5e-97a4ed26f294": {"view": "==", },
                "50348927-2c4f-4023-b638-445469c66953": {"view": "4", },
            },
            "local_depends_on": {"view": "==", },
        },
        "edit": {
            "range": ["1", "2", "3", "4"],
            "app_depends_on": {
                "4e48c863-861b-475a-aa5e-97a4ed26f294": {"view": "==", },
                "50348927-2c4f-4023-b638-445469c66953": {"view": "4", },
            },
            "local_depends_on": {"view": "==", },
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
    "87ce1662-ca9d-403f-a32e-9553714ebc6d": ApplicationConfigFrame(**BUSINESS_TRIP_REQUEST).data(
        depend_follow_main=False,
        filtering_inheritor=True
    ),
    "55ba3005-6ccc-4807-af27-7cc45e99e3f6": ApplicationConfigFrame(**ASSET_TOOLS_PROVIDE).data(
        depend_follow_main=False,
        filtering_inheritor=True
    ),
    "6078deaa-96b3-4743-97e3-5457454fa7aa": ApplicationConfigFrame(**MEETING_SCHEDULE).data(
        depend_follow_main=False,
        filtering_inheritor=True
    ),
}
