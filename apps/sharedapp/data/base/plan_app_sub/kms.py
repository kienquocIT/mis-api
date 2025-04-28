from apps.sharedapp.data.base.settings import ApplicationConfigFrame

__all__ = [
    'Application_kms_data',
]
KMS_DOCUMENT_APPROVAL = {
    "id": "7505d5db-42fe-4cde-ae5e-dbba78e2df03",
    "title": "Document approval",
    "code": "documentapproval",
    "model_code": "kmsdocumentapproval",
    "app_label": "kms",
    "is_workflow": True,
    "allow_permit": True,
    "option_permission": 1,
    "option_allowed": [4],
    "app_depend_on": [
        "50348927-2c4f-4023-b638-445469c66953",  # Employee
        "e17b9123-8002-4c9b-921b-7722c3c9e3a5",  # Group
    ],
    "permit_mapping": {
        "view": {
            "range": ["4"],
            "app_depends_on": {
                "50348927-2c4f-4023-b638-445469c66953": {"view": "4", },  # For summary permit of employee
                "e17b9123-8002-4c9b-921b-7722c3c9e3a5": {"view": "4", },  # For summary permit of group
            },
            "local_depends_on": {
                "view": "4",
            },
        },
        "create": {
            "range": ["4"],
            "app_depends_on": {
                "50348927-2c4f-4023-b638-445469c66953": {"view": "4", },  # For summary permit of employee
                "e17b9123-8002-4c9b-921b-7722c3c9e3a5": {"view": "4", },  # For summary permit of group
            },
            "local_depends_on": {
                "view": "4",
            },
        },
        "edit": {
            "range": ["4"],
            "app_depends_on": {
                "50348927-2c4f-4023-b638-445469c66953": {"view": "4", },  # For summary permit of employee
                "e17b9123-8002-4c9b-921b-7722c3c9e3a5": {"view": "4", },  # For summary permit of group
            },
            "local_depends_on": {
                "view": "4",
            },
        },
        "delete": {
            "range": ["1", "2", "3", "4"],
            "app_depends_on": {},
            "local_depends_on": {
                "view": "4",
            },
        },
    },
    "allow_import": False,
}


Application_kms_data = {
    "7505d5db-42fe-4cde-ae5e-dbba78e2df03": ApplicationConfigFrame(**KMS_DOCUMENT_APPROVAL).data(
        depend_follow_main=False,
        filtering_inheritor=True
    ),
}
