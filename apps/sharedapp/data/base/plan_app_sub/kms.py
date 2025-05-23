from apps.sharedapp.data.base.settings import ApplicationConfigFrame

__all__ = [
    'Application_kms_data',
]
KMS_DOCUMENT_APPROVAL = {
    "id": "7505d5db-42fe-4cde-ae5e-dbba78e2df03",
    "title": "Document approval",
    "code": "kmsdocumentapproval",
    "model_code": "kmsdocumentapproval",
    "app_label": "documentapproval",
    "is_workflow": True,
    "allow_permit": True,
    "option_permission": 0,
    "option_allowed": [1, 2, 3, 4],
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
    "allow_import": False,
}


Application_kms_data = {
    "7505d5db-42fe-4cde-ae5e-dbba78e2df03": ApplicationConfigFrame(**KMS_DOCUMENT_APPROVAL).data(
        depend_follow_main=False,
        filtering_inheritor=True
    ),
}
