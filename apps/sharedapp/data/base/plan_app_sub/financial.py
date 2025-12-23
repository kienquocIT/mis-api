from apps.sharedapp.data.base.settings import ApplicationConfigFrame

__all__ = {
    'Application_financial_data',
}

FINANCIAL_CASHFLOW_CASH_INFLOW_APP_CONFIG = {
    "id": "7ba35923-d8ff-4f6d-bf80-468a7190a63b",
    "title": "Cash Inflow",
    "code": "cashinflow",
    "model_code": "cashinflow",
    "app_label": "financialcashflow",
    "is_workflow": True,
    "app_depend_on": [
        "4e48c863-861b-475a-aa5e-97a4ed26f294",  # Saledata.Account
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
                "4e48c863-861b-475a-aa5e-97a4ed26f294": {
                    "view": "==",
                },
            },
            "local_depends_on": {
                "view": "==",
            },
        },
        "edit": {
            "range": ["1", "2", "3", "4"],
            "app_depends_on": {
                "4e48c863-861b-475a-aa5e-97a4ed26f294": {
                    "view": "==",
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
    "allow_permit": True,
    "allow_print": True,
    "allow_process": False,
    "allow_opportunity": False,
}

FINANCIAL_CASHFLOW_CASH_OUTFLOW_APP_CONFIG = {
    "id": "c51857ef-513f-4dbf-babd-26d68950ad6e",
    "title": "Cash Outflow",
    "code": "cashoutflow",
    "model_code": "cashoutflow",
    "app_label": "financialcashflow",
    "is_workflow": True,
    "app_depend_on": [
        "4e48c863-861b-475a-aa5e-97a4ed26f294",  # Saledata.Account
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
                "4e48c863-861b-475a-aa5e-97a4ed26f294": {
                    "view": "==",
                },
            },
            "local_depends_on": {
                "view": "==",
            },
        },
        "edit": {
            "range": ["1", "2", "3", "4"],
            "app_depends_on": {
                "4e48c863-861b-475a-aa5e-97a4ed26f294": {
                    "view": "==",
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
    "allow_permit": True,
    "allow_print": True,
    "allow_process": False,
    "allow_opportunity": False,
}

ACCOUNTING_JE_APP_CONFIG = {
    "id": "a9bb7b64-4f3c-412d-9e08-3b713d58d31d",
    "title": "Journal Entry",
    "code": "reconciliation",
    "model_code": "journalentry",
    "app_label": "accounting",
    "is_workflow": True,
    "app_depend_on": [],
    "permit_mapping": {
        "view": {
            "range": ["1", "2", "3", "4"],
            "app_depends_on": {},
            "local_depends_on": {},
        },
        "create": {
            "range": ["1", "2", "3", "4"],
            "app_depends_on": {},
            "local_depends_on": {
                "view": "==",
            },
        },
        "edit": {
            "range": ["1", "2", "3", "4"],
            "app_depends_on": {},
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
    "allow_permit": True,
    "allow_print": True,
    "allow_process": False,
    "allow_opportunity": False,
}

POSTING_ENGINE_APP_CONFIG = {
    "id": "f02ef380-5b42-4b9c-af9b-232809105a1d",
    "title": "Posting Engine",
    "code": "postingengine",
    "model_code": "postingengine",
    "app_label": "postingengine",
    "is_workflow": True,
    "app_depend_on": [],
    "permit_mapping": {
        "view": {
            "range": ["1", "2", "3", "4"],
            "app_depends_on": {},
            "local_depends_on": {},
        },
        "create": {
            "range": ["1", "2", "3", "4"],
            "app_depends_on": {},
            "local_depends_on": {
                "view": "==",
            },
        },
        "edit": {
            "range": ["1", "2", "3", "4"],
            "app_depends_on": {},
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
    "allow_permit": True,
    "allow_print": False,
    "allow_process": False,
    "allow_opportunity": False,
}

Application_financial_data = {
    "7ba35923-d8ff-4f6d-bf80-468a7190a63b": ApplicationConfigFrame(**FINANCIAL_CASHFLOW_CASH_INFLOW_APP_CONFIG).data(
        depend_follow_main=True,
        filtering_inheritor=True,
        spacing_allow=["0", "1"],
    ),
    "c51857ef-513f-4dbf-babd-26d68950ad6e": ApplicationConfigFrame(**FINANCIAL_CASHFLOW_CASH_OUTFLOW_APP_CONFIG).data(
        depend_follow_main=True,
        filtering_inheritor=True,
        spacing_allow=["0", "1"],
    ),
    "a9bb7b64-4f3c-412d-9e08-3b713d58d31d": ApplicationConfigFrame(**ACCOUNTING_JE_APP_CONFIG).data(
        depend_follow_main=True,
        filtering_inheritor=True,
        spacing_allow=["0", "1"],
    ),
    "f02ef380-5b42-4b9c-af9b-232809105a1d": ApplicationConfigFrame(**POSTING_ENGINE_APP_CONFIG).data(
        depend_follow_main=False,
        filtering_inheritor=True,
    ),
}

