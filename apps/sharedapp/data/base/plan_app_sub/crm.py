from apps.sharedapp.data.base.settings import ApplicationConfigFrame

__all__ = [
    'Application_crm_data',
]

CONTACT_APP_CONFIG = {
    "id": "828b785a-8f57-4a03-9f90-e0edf96560d7",
    "title": "Contact",
    "code": "contact",
    "model_code": "contact",
    "app_label": "saledata",
    "is_workflow": True,
    "option_permission": 0,
    "option_allowed": [1, 2, 3, 4],
    "app_depend_on": [
        "50348927-2c4f-4023-b638-445469c66953",  # Employee
        "4e48c863-861b-475a-aa5e-97a4ed26f294",  # Account
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
                    "view": "4",
                },
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
                "50348927-2c4f-4023-b638-445469c66953": {
                    "view": "4",
                },
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
    }
}

ACCOUNT_APP_CONFIG = {
    "id": "4e48c863-861b-475a-aa5e-97a4ed26f294",
    "title": "Account",
    "code": "account",
    "model_code": "account",
    "app_label": "saledata",
    "is_workflow": True,
    "option_permission": 0,
    "option_allowed": [1, 2, 3, 4],
    "app_depend_on": [
        "50348927-2c4f-4023-b638-445469c66953",  # Employee
        "828b785a-8f57-4a03-9f90-e0edf96560d7",  # Contact
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
                    "view": "4",
                },
                "828b785a-8f57-4a03-9f90-e0edf96560d7": {
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
                "50348927-2c4f-4023-b638-445469c66953": {
                    "view": "4",
                },
                "828b785a-8f57-4a03-9f90-e0edf96560d7": {
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
    }
}

OPPORTUNITY_APP_CONFIG = {
    "id": "296a1410-8d72-46a8-a0a1-1821f196e66c",
    "title": "Opportunity",
    "code": "opportunity",
    "model_code": "opportunity",
    "app_label": "opportunity",
    "is_workflow": True,
    "app_depend_on": [
        "50348927-2c4f-4023-b638-445469c66953",  # Employee
        "4e48c863-861b-475a-aa5e-97a4ed26f294",  # Saledata.Account
        "828b785a-8f57-4a03-9f90-e0edf96560d7",  # Contact
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
                "50348927-2c4f-4023-b638-445469c66953": {"view": "4", },
                "4e48c863-861b-475a-aa5e-97a4ed26f294": {"view": "==", },
                "828b785a-8f57-4a03-9f90-e0edf96560d7": {"view": "==", },
                "a8badb2e-54ff-4654-b3fd-0d2d3c777538": {"view": "4", },
            },
            "local_depends_on": {
                "view": "==",
            },
        },
        "edit": {
            "range": ["1", "2", "3", "4"],
            "app_depends_on": {
                "50348927-2c4f-4023-b638-445469c66953": {"view": "4", },
                "4e48c863-861b-475a-aa5e-97a4ed26f294": {"view": "==", },
                "828b785a-8f57-4a03-9f90-e0edf96560d7": {"view": "==", },
                "a8badb2e-54ff-4654-b3fd-0d2d3c777538": {"view": "4", },
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

TASK_APP_CONFIG = {
    "id": "e66cfb5a-b3ce-4694-a4da-47618f53de4c",
    "title": "Task",
    "code": "opportunitytask",
    "model_code": "opportunitytask",
    "app_label": "task",
    "is_workflow": False,
    "option_permission": 0,
    "option_allowed": [1, 2, 3, 4],
    "app_depend_on": [
        "296a1410-8d72-46a8-a0a1-1821f196e66c",  # Opportunity
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
                "296a1410-8d72-46a8-a0a1-1821f196e66c": {"view": "4", },
                "50348927-2c4f-4023-b638-445469c66953": {"view": "4", },
            },
            "local_depends_on": {"view": "==", },
        },
        "edit": {
            "range": ["1", "2", "3", "4"],
            "app_depends_on": {
                "296a1410-8d72-46a8-a0a1-1821f196e66c": {"view": "4", },
                "50348927-2c4f-4023-b638-445469c66953": {"view": "4", },
            },
            "local_depends_on": {"view": "==", },
        },
        "delete": {
            "range": ["1", "2", "3", "4"],
            "app_depends_on": {},
            "local_depends_on": {"view": "==", },
        },
    },
}

QUOTATION_APP_CONFIG = {
    "id": "b9650500-aba7-44e3-b6e0-2542622702a3",
    "title": "Quotation",
    "code": "quotation",
    "model_code": "quotation",
    "app_label": "quotation",
    "is_workflow": True,
    "app_depend_on": [
        "296a1410-8d72-46a8-a0a1-1821f196e66c",  # Opportunity
        "4e48c863-861b-475a-aa5e-97a4ed26f294",  # Saledata.Account
        "828b785a-8f57-4a03-9f90-e0edf96560d7",  # Contact
        "50348927-2c4f-4023-b638-445469c66953",  # Employee
        "3407d35d-27ce-407e-8260-264574a216e3",  # Payment Term
        "a8badb2e-54ff-4654-b3fd-0d2d3c777538",  # Product
        "f57b9e92-cb01-42e3-b7fe-6166ecd18e9c",  # Promotion
        "e6a00a1a-d4f9-41b7-b0de-bb1efbe8446a",  # Shipping
        "245e9f47-df59-4d4a-b355-7eff2859247f",  # Expense Term
        "022375ce-c99c-4f11-8841-0a26c85f2fc2",  # Expense
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
                "296a1410-8d72-46a8-a0a1-1821f196e66c": {"view": "==", },
                "4e48c863-861b-475a-aa5e-97a4ed26f294": {"view": "==", },
                "828b785a-8f57-4a03-9f90-e0edf96560d7": {"view": "==", },
                "50348927-2c4f-4023-b638-445469c66953": {"view": "4", },
                "3407d35d-27ce-407e-8260-264574a216e3": {"view": "4", },
                "a8badb2e-54ff-4654-b3fd-0d2d3c777538": {"view": "4", },
                "f57b9e92-cb01-42e3-b7fe-6166ecd18e9c": {"view": "4", },
                "e6a00a1a-d4f9-41b7-b0de-bb1efbe8446a": {"view": "4", },
                "245e9f47-df59-4d4a-b355-7eff2859247f": {"view": "4", },
                "022375ce-c99c-4f11-8841-0a26c85f2fc2": {"view": "4", },
            },
            "local_depends_on": {"view": "==", },
        },
        "edit": {
            "range": ["1", "2", "3", "4"],
            "app_depends_on": {
                "296a1410-8d72-46a8-a0a1-1821f196e66c": {"view": "==", },
                "4e48c863-861b-475a-aa5e-97a4ed26f294": {"view": "==", },
                "828b785a-8f57-4a03-9f90-e0edf96560d7": {"view": "==", },
                "50348927-2c4f-4023-b638-445469c66953": {"view": "4", },
                "3407d35d-27ce-407e-8260-264574a216e3": {"view": "4", },
                "a8badb2e-54ff-4654-b3fd-0d2d3c777538": {"view": "4", },
                "f57b9e92-cb01-42e3-b7fe-6166ecd18e9c": {"view": "4", },
                "e6a00a1a-d4f9-41b7-b0de-bb1efbe8446a": {"view": "4", },
                "245e9f47-df59-4d4a-b355-7eff2859247f": {"view": "4", },
                "022375ce-c99c-4f11-8841-0a26c85f2fc2": {"view": "4", },
            },
            "local_depends_on": {"view": "==", },
        },
        "delete": {
            "range": ["1", "2", "3", "4"],
            "app_depends_on": {},
            "local_depends_on": {"view": "==", },
        },
    },
    "allow_print": True,
}

SALEORDER_APP_CONFIG = {
    "id": "a870e392-9ad2-4fe2-9baa-298a38691cf2",
    "title": "Sale Order",
    "code": "saleorder",
    "model_code": "saleorder",
    "app_label": "saleorder",
    "is_workflow": True,
    "app_depend_on": [
        "296a1410-8d72-46a8-a0a1-1821f196e66c",  # Opportunity
        "4e48c863-861b-475a-aa5e-97a4ed26f294",  # Saledata.Account
        "828b785a-8f57-4a03-9f90-e0edf96560d7",  # Contact
        "b9650500-aba7-44e3-b6e0-2542622702a3",  # Quotation
        "50348927-2c4f-4023-b638-445469c66953",  # Employee
        "3407d35d-27ce-407e-8260-264574a216e3",  # Payment Term
        "f57b9e92-cb01-42e3-b7fe-6166ecd18e9c",  # Promotion
        "e6a00a1a-d4f9-41b7-b0de-bb1efbe8446a",  # Shipping
        "245e9f47-df59-4d4a-b355-7eff2859247f",  # Expense Item
        "022375ce-c99c-4f11-8841-0a26c85f2fc2",  # Expense
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
                "296a1410-8d72-46a8-a0a1-1821f196e66c": {"view": "==", },
                "4e48c863-861b-475a-aa5e-97a4ed26f294": {"view": "==", },
                "828b785a-8f57-4a03-9f90-e0edf96560d7": {"view": "==", },
                "b9650500-aba7-44e3-b6e0-2542622702a3": {"view": "==", },
                "50348927-2c4f-4023-b638-445469c66953": {"view": "4", },
                "3407d35d-27ce-407e-8260-264574a216e3": {"view": "4", },
                "f57b9e92-cb01-42e3-b7fe-6166ecd18e9c": {"view": "4", },
                "e6a00a1a-d4f9-41b7-b0de-bb1efbe8446a": {"view": "4", },
                "245e9f47-df59-4d4a-b355-7eff2859247f": {"view": "4", },
                "022375ce-c99c-4f11-8841-0a26c85f2fc2": {"view": "4", },
            },
            "local_depends_on": {
                "view": "==",
            },
        },
        "edit": {
            "range": ["1", "2", "3", "4"],
            "app_depends_on": {
                "296a1410-8d72-46a8-a0a1-1821f196e66c": {"view": "==", },
                "4e48c863-861b-475a-aa5e-97a4ed26f294": {"view": "==", },
                "828b785a-8f57-4a03-9f90-e0edf96560d7": {"view": "==", },
                "b9650500-aba7-44e3-b6e0-2542622702a3": {"view": "==", },
                "50348927-2c4f-4023-b638-445469c66953": {"view": "4", },
                "3407d35d-27ce-407e-8260-264574a216e3": {"view": "4", },
                "f57b9e92-cb01-42e3-b7fe-6166ecd18e9c": {"view": "4", },
                "e6a00a1a-d4f9-41b7-b0de-bb1efbe8446a": {"view": "4", },
                "245e9f47-df59-4d4a-b355-7eff2859247f": {"view": "4", },
                "022375ce-c99c-4f11-8841-0a26c85f2fc2": {"view": "4", },
            },
            "local_depends_on": {
                "view": "==",
            },
        },
        "delete": {
            "range": ["1", "2", "3", "4"],
            "app_depends_on": {
                "296a1410-8d72-46a8-a0a1-1821f196e66c": {"view": "==", },
                "4e48c863-861b-475a-aa5e-97a4ed26f294": {"view": "==", },
                "828b785a-8f57-4a03-9f90-e0edf96560d7": {"view": "==", },
                "b9650500-aba7-44e3-b6e0-2542622702a3": {"view": "==", },
                "50348927-2c4f-4023-b638-445469c66953": {"view": "4", },
                "3407d35d-27ce-407e-8260-264574a216e3": {"view": "4", },
                "f57b9e92-cb01-42e3-b7fe-6166ecd18e9c": {"view": "4", },
                "e6a00a1a-d4f9-41b7-b0de-bb1efbe8446a": {"view": "4", },
                "245e9f47-df59-4d4a-b355-7eff2859247f": {"view": "4", },
                "022375ce-c99c-4f11-8841-0a26c85f2fc2": {"view": "4", },
            },
            "local_depends_on": {
                "view": "==",
            },
        },
    },
}

PRODUCT_APP_CONFIG = {
    "id": "a8badb2e-54ff-4654-b3fd-0d2d3c777538",
    "title": "Product",
    "code": "product",
    "model_code": "product",
    "app_label": "saledata",
    "is_workflow": False,
}

EXPENSES_APP_CONFIG = {
    "id": "022375ce-c99c-4f11-8841-0a26c85f2fc2",
    "title": "Internal labor item",
    "code": "expenses",
    "model_code": "expenses",
    "app_label": "saledata",
    "is_workflow": False,
}

EXPENSE_ITEM_APP_CONFIG = {
    "id": "245e9f47-df59-4d4a-b355-7eff2859247f",
    "title": "Expense Item",
    "code": "expenseitem",
    "model_code": "expenseitem",
    "app_label": "saledata",
    "is_workflow": False,
}

WAREHOUSE_APP_CONFIG = {
    "id": "80b8cd4f-cfba-4f33-9642-a4dd6ee31efd",
    "title": "Warehouse",
    "code": "warehouse",
    "model_code": "warehouse",
    "app_label": "saledata",
    "is_workflow": False,
}

PICKING_APP_CONFIG = {
    "id": "3d8ad524-5dd9-4a8b-a7cd-a9a371315a2a",
    "title": "Picking",
    "code": "orderpickingsub",
    "model_code": "orderpickingsub",
    "app_label": "delivery",
    "is_workflow": False,
    "app_depend_on": [
        "80b8cd4f-cfba-4f33-9642-a4dd6ee31efd",  # WareHouse
    ],
    "permit_mapping": {
        "view": {
            "range": ["1", "3", "4"],
            "app_depends_on": {},
            "local_depends_on": {},
        },
        "create": {
            "range": ["1", "3", "4"],
            "app_depends_on": {
                "80b8cd4f-cfba-4f33-9642-a4dd6ee31efd": {"view": "4", },
            },
            "local_depends_on": {"view": "==", },
        },
        "edit": {
            "range": ["1", "3", "4"],
            "app_depends_on": {
                "80b8cd4f-cfba-4f33-9642-a4dd6ee31efd": {"view": "4", },
            },
            "local_depends_on": {"view": "==", },
        },
        "delete": {
            "range": ["1", "3", "4"],
            "app_depends_on": {},
            "local_depends_on": {"view": "==", },
        },
    },
}

DELIVERY_APP_CONFIG = {
    "id": "1373e903-909c-4b77-9957-8bcf97e8d6d3",
    "title": "Delivery",
    "code": "orderdeliverysub",
    "model_code": "orderdeliverysub",
    "app_label": "delivery",
    "is_workflow": True,
    "app_depend_on": [
        "80b8cd4f-cfba-4f33-9642-a4dd6ee31efd",  # WareHouse
        "4e48c863-861b-475a-aa5e-97a4ed26f294",  # SaleData.Account
    ],
    "permit_mapping": {
        "view": {
            "range": ["1", "3", "4"],
            "app_depends_on": {},
            "local_depends_on": {},
        },
        "create": {
            "range": ["1", "3", "4"],
            "app_depends_on": {
                "80b8cd4f-cfba-4f33-9642-a4dd6ee31efd": {"view": "4", },
                "4e48c863-861b-475a-aa5e-97a4ed26f294": {"view": "4", },
            },
            "local_depends_on": {"view": "==", },
        },
        "edit": {
            "range": ["1", "3", "4"],
            "app_depends_on": {
                "80b8cd4f-cfba-4f33-9642-a4dd6ee31efd": {"view": "4", },
                "4e48c863-861b-475a-aa5e-97a4ed26f294": {"view": "4", },
            },
            "local_depends_on": {"view": "==", },
        },
        "delete": {
            "range": ["1", "3", "4"],
            "app_depends_on": {},
            "local_depends_on": {"view": "==", },
        },
    },
}

PRICES_APP_CONFIG = {
    "id": "10a5e913-fa51-4127-a632-a8347a55c4bb",
    "title": "Prices",
    "code": "price",
    "model_code": "price",
    "app_label": "saledata",
    "is_workflow": False,
}

SHIPPING_APP_CONFIG = {
    "id": "e6a00a1a-d4f9-41b7-b0de-bb1efbe8446a",
    "title": "Shipping",
    "code": "shipping",
    "model_code": "shipping",
    "app_label": "saledata",
    "is_workflow": False,
}

PROMOTION_APP_CONFIG = {
    "id": "f57b9e92-cb01-42e3-b7fe-6166ecd18e9c",
    "title": "Promotions",
    "code": "promotion",
    "model_code": "promotion",
    "app_label": "promotion",
    "is_workflow": False,
    "app_depend_on": [
        "828b785a-8f57-4a03-9f90-e0edf96560d7",  # Contact
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
                "828b785a-8f57-4a03-9f90-e0edf96560d7": {"view": "4", },
                "a8badb2e-54ff-4654-b3fd-0d2d3c777538": {"view": "4", },
            },
            "local_depends_on": {"view": "==", },
        },
        "edit": {
            "range": ["1", "2", "3", "4"],
            "app_depends_on": {
                "828b785a-8f57-4a03-9f90-e0edf96560d7": {"view": "4", },
                "a8badb2e-54ff-4654-b3fd-0d2d3c777538": {"view": "4", },
            },
            "local_depends_on": {"view": "==", },
        },
        "delete": {
            "range": ["1", "2", "3", "4"],
            "app_depends_on": {},
            "local_depends_on": {"view": "==", },
        },
    },
}

ADVANCE_PAYMENT_APP_CONFIG = {
    "id": "57725469-8b04-428a-a4b0-578091d0e4f5",
    "title": "Advance Payment",
    "code": "advancepayment",
    "model_code": "advancepayment",
    "app_label": "cashoutflow",
    "is_workflow": True,
    "app_depend_on": [
        "50348927-2c4f-4023-b638-445469c66953",  # Employee
        "a870e392-9ad2-4fe2-9baa-298a38691cf2",  # Sale Order
        "b9650500-aba7-44e3-b6e0-2542622702a3",  # Quotation
        "296a1410-8d72-46a8-a0a1-1821f196e66c",  # Opportunity
        "4e48c863-861b-475a-aa5e-97a4ed26f294",  # Saledata.Account
        "022375ce-c99c-4f11-8841-0a26c85f2fc2",  # Expenses
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
                "a870e392-9ad2-4fe2-9baa-298a38691cf2": {
                    "view": "==",
                },
                "b9650500-aba7-44e3-b6e0-2542622702a3": {
                    "view": "==",
                },
                "296a1410-8d72-46a8-a0a1-1821f196e66c": {
                    "view": "==",
                },
                "4e48c863-861b-475a-aa5e-97a4ed26f294": {
                    "view": "==",
                },
                "022375ce-c99c-4f11-8841-0a26c85f2fc2": {
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
                "a870e392-9ad2-4fe2-9baa-298a38691cf2": {
                    "view": "==",
                },
                "b9650500-aba7-44e3-b6e0-2542622702a3": {
                    "view": "==",
                },
                "296a1410-8d72-46a8-a0a1-1821f196e66c": {
                    "view": "==",
                },
                "4e48c863-861b-475a-aa5e-97a4ed26f294": {
                    "view": "==",
                },
                "022375ce-c99c-4f11-8841-0a26c85f2fc2": {
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

PAYMENT_APP_CONFIG = {
    "id": "1010563f-7c94-42f9-ba99-63d5d26a1aca",
    "title": "Payments",
    "code": "payment",
    "model_code": "payment",
    "app_label": "cashoutflow",
    "is_workflow": True,
    "app_depend_on": [
        "a870e392-9ad2-4fe2-9baa-298a38691cf2",  # Sale Order
        "b9650500-aba7-44e3-b6e0-2542622702a3",  # Quotation
        "296a1410-8d72-46a8-a0a1-1821f196e66c",  # Opportunity
        "4e48c863-861b-475a-aa5e-97a4ed26f294",  # Saledata.Account
        "50348927-2c4f-4023-b638-445469c66953",  # Employee
        "57725469-8b04-428a-a4b0-578091d0e4f5",  # Advance Payment
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
                "a870e392-9ad2-4fe2-9baa-298a38691cf2": {"view": "4", },
                "b9650500-aba7-44e3-b6e0-2542622702a3": {"view": "==", },
                "296a1410-8d72-46a8-a0a1-1821f196e66c": {"view": "==", },
                "4e48c863-861b-475a-aa5e-97a4ed26f294": {"view": "==", },
                "50348927-2c4f-4023-b638-445469c66953": {"view": "4", },
                "57725469-8b04-428a-a4b0-578091d0e4f5": {"view": "==", },
            },
            "local_depends_on": {
                "view": "==",
            },
        },
        "edit": {
            "range": ["1", "2", "3", "4"],
            "app_depends_on": {
                "a870e392-9ad2-4fe2-9baa-298a38691cf2": {"view": "4", },
                "b9650500-aba7-44e3-b6e0-2542622702a3": {"view": "==", },
                "296a1410-8d72-46a8-a0a1-1821f196e66c": {"view": "==", },
                "4e48c863-861b-475a-aa5e-97a4ed26f294": {"view": "==", },
                "50348927-2c4f-4023-b638-445469c66953": {"view": "4", },
                "57725469-8b04-428a-a4b0-578091d0e4f5": {"view": "==", },
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

PAYMENT_TERM_APP_CONFIG = {
    "id": "3407d35d-27ce-407e-8260-264574a216e3",
    "title": "Payment Term",
    "code": "paymentterm",
    "model_code": "paymentterm",
    "app_label": "saledata",
    "is_workflow": False,
}

RETURN_ADVANCE_APP_CONFIG = {
    "id": "65d36757-557e-4534-87ea-5579709457d7",
    "title": "Return Advance",
    "code": "returnadvance",
    "model_code": "returnadvance",
    "app_label": "cashoutflow",
    "is_workflow": True,
    "app_depend_on": [
        "57725469-8b04-428a-a4b0-578091d0e4f5",  # Advance Payment
        "50348927-2c4f-4023-b638-445469c66953",  # Employee
    ],
    "permit_mapping": {
        "view": {
            "range": ["1", "4"],
            "app_depends_on": {},
            "local_depends_on": {},
        },
        "create": {
            "range": ["1", "4"],
            "app_depends_on": {
                "57725469-8b04-428a-a4b0-578091d0e4f5": {"view": "4", },
                "50348927-2c4f-4023-b638-445469c66953": {"view": "4", },
            },
            "local_depends_on": {
                "view": "==",
            },
        },
        "edit": {
            "range": ["1", "4"],
            "app_depends_on": {
                "57725469-8b04-428a-a4b0-578091d0e4f5": {"view": "4", },
                "50348927-2c4f-4023-b638-445469c66953": {"view": "4", },
            },
            "local_depends_on": {
                "view": "==",
            },
        },
        "delete": {
            "range": ["1", "4"],
            "app_depends_on": {},
            "local_depends_on": {
                "view": "==",
            },
        },
    },
}

DOCUMENT_FOR_CUSTOMER_APP_CONFIG = {
    "id": "319356b4-f16c-4ba4-bdcb-e1b0c2a2c124",
    "title": "Document For Customer",
    "code": "documentforcustomer",
    "model_code": "documentforcustomer",
    "app_label": "opportunity",
    "is_workflow": False,
}

CALL_LOG_APP_CONFIG = {
    "id": "14dbc606-1453-4023-a2cf-35b1cd9e3efd",
    "title": "Call",
    "code": "opportunitycall",
    "model_code": "opportunitycall",
    "app_label": "opportunity",
    "is_workflow": False,
}

EMAIL_LOG_APP_CONFIG = {
    "id": "dec012bf-b931-48ba-a746-38b7fd7ca73b",
    "title": "Email",
    "code": "opportunityemail",
    "model_code": "opportunityemail",
    "app_label": "opportunity",
    "is_workflow": False,
}

MEETING_LOG_APP_CONFIG = {
    "id": "2fe959e3-9628-4f47-96a1-a2ef03e867e3",
    "title": "Meetting With Customer",
    "code": "meetingwithcustomer",
    "model_code": "meetingwithcustomer",
    "app_label": "opportunity",
    "is_workflow": False,
}

CONTRACT_APP_CONFIG = {
    "id": "31c9c5b0-717d-4134-b3d0-cc4ca174b168",
    "title": "Contract",
    "code": "contract",
    "model_code": "contract",
    "app_label": "contract",
    "is_workflow": False,
}

PURCHASE_QUOTATION_REQUEST_APP_CONFIG = {
    "id": "d78bd5f3-8a8d-48a3-ad62-b50d576ce173",
    "title": "Purchase Quotation Request",
    "code": "purchasequotationrequest",
    "model_code": "purchasequotationrequest",
    "app_label": "purchasing",
    "is_workflow": True,
    "app_depend_on": [
        "fbff9b3f-f7c9-414f-9959-96d3ec2fb8bf",  # Purchase Request
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
                "fbff9b3f-f7c9-414f-9959-96d3ec2fb8bf": {"view": "==", },
                "a8badb2e-54ff-4654-b3fd-0d2d3c777538": {"view": "4", },
            },
            "local_depends_on": {"view": "==", },
        },
        "edit": {
            "range": ["1", "2", "3", "4"],
            "app_depends_on": {
                "fbff9b3f-f7c9-414f-9959-96d3ec2fb8bf": {"view": "==", },
                "a8badb2e-54ff-4654-b3fd-0d2d3c777538": {"view": "4", },
            },
            "local_depends_on": {"view": "==", },
        },
        "delete": {
            "range": ["1", "2", "3", "4"],
            "app_depends_on": {
                "fbff9b3f-f7c9-414f-9959-96d3ec2fb8bf": {"view": "==", },
                "a8badb2e-54ff-4654-b3fd-0d2d3c777538": {"view": "4", },
            },
            "local_depends_on": {"view": "==", },
        },
    },
}

PURCHASE_QUOTATION_APP_CONFIG = {
    "id": "f52a966a-2eb2-4851-852d-eff61efeb896",
    "title": "Purchase Quotation",
    "code": "purchasequotation",
    "model_code": "purchasequotation",
    "app_label": "purchasing",
    "is_workflow": True,
    "app_depend_on": [
        "4e48c863-861b-475a-aa5e-97a4ed26f294",  # SaleData.Account
        "828b785a-8f57-4a03-9f90-e0edf96560d7",  # Contact
        "d78bd5f3-8a8d-48a3-ad62-b50d576ce173",  # Purchase Quotation Request
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
                "4e48c863-861b-475a-aa5e-97a4ed26f294": {"view": "4", },
                "828b785a-8f57-4a03-9f90-e0edf96560d7": {"view": "4", },
                "d78bd5f3-8a8d-48a3-ad62-b50d576ce173": {"view": "==", },
                "a8badb2e-54ff-4654-b3fd-0d2d3c777538": {"view": "4", },
            },
            "local_depends_on": {"view": "==", },
        },
        "edit": {
            "range": ["1", "2", "3", "4"],
            "app_depends_on": {
                "4e48c863-861b-475a-aa5e-97a4ed26f294": {"view": "4", },
                "828b785a-8f57-4a03-9f90-e0edf96560d7": {"view": "4", },
                "d78bd5f3-8a8d-48a3-ad62-b50d576ce173": {"view": "==", },
                "a8badb2e-54ff-4654-b3fd-0d2d3c777538": {"view": "4", },
            },
            "local_depends_on": {"view": "==", },
        },
        "delete": {
            "range": ["1", "2", "3", "4"],
            "app_depends_on": {},
            "local_depends_on": {"view": "==", },
        },
    },
}

PURCHASE_ORDER_APP_CONFIG = {
    "id": "81a111ef-9c32-4cbd-8601-a3cce884badb",
    "title": "Purchase Order",
    "code": "purchaseorder",
    "model_code": "purchaseorder",
    "app_label": "purchasing",
    "is_workflow": True,
    "app_depend_on": [
        "4e48c863-861b-475a-aa5e-97a4ed26f294",  # Saledata.Account
        "828b785a-8f57-4a03-9f90-e0edf96560d7",  # Contact
        "fbff9b3f-f7c9-414f-9959-96d3ec2fb8bf",  # Purchase Request
        "f52a966a-2eb2-4851-852d-eff61efeb896",  # Purchase Quotation
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
                "4e48c863-861b-475a-aa5e-97a4ed26f294": {"view": "==", },
                "828b785a-8f57-4a03-9f90-e0edf96560d7": {"view": "==", },
                "fbff9b3f-f7c9-414f-9959-96d3ec2fb8bf": {"view": "4", },
                "f52a966a-2eb2-4851-852d-eff61efeb896": {"view": "4", },
                "a8badb2e-54ff-4654-b3fd-0d2d3c777538": {"view": "4", },
            },
            "local_depends_on": {
                "view": "==",
            },
        },
        "edit": {
            "range": ["1", "2", "3", "4"],
            "app_depends_on": {
                "4e48c863-861b-475a-aa5e-97a4ed26f294": {"view": "==", },
                "828b785a-8f57-4a03-9f90-e0edf96560d7": {"view": "==", },
                "fbff9b3f-f7c9-414f-9959-96d3ec2fb8bf": {"view": "4", },
                "f52a966a-2eb2-4851-852d-eff61efeb896": {"view": "4", },
                "a8badb2e-54ff-4654-b3fd-0d2d3c777538": {"view": "4", },
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

PURCHASE_REQUEST_APP_CONFIG = {
    "id": "fbff9b3f-f7c9-414f-9959-96d3ec2fb8bf",
    "title": "Purchase Request",
    "code": "purchaserequest",
    "model_code": "purchaserequest",
    "app_label": "purchasing",
    "is_workflow": False,
    "app_depend_on": [
        "a870e392-9ad2-4fe2-9baa-298a38691cf2",  # Sale Order
        "4e48c863-861b-475a-aa5e-97a4ed26f294",  # SaleData.Account
        "828b785a-8f57-4a03-9f90-e0edf96560d7",  # Contact
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
                "a870e392-9ad2-4fe2-9baa-298a38691cf2": {"view": "4", },
                "4e48c863-861b-475a-aa5e-97a4ed26f294": {"view": "==", },
                "828b785a-8f57-4a03-9f90-e0edf96560d7": {"view": "==", },
                "a8badb2e-54ff-4654-b3fd-0d2d3c777538": {"view": "4", },
            },
            "local_depends_on": {"view": "==", },
        },
        "edit": {
            "range": ["1", "2", "3", "4"],
            "app_depends_on": {
                "a870e392-9ad2-4fe2-9baa-298a38691cf2": {"view": "4", },
                "4e48c863-861b-475a-aa5e-97a4ed26f294": {"view": "==", },
                "828b785a-8f57-4a03-9f90-e0edf96560d7": {"view": "==", },
                "a8badb2e-54ff-4654-b3fd-0d2d3c777538": {"view": "4", },
            },
            "local_depends_on": {"view": "==", },
        },
        "delete": {
            "range": ["1", "2", "3", "4"],
            "app_depends_on": {},
            "local_depends_on": {"view": "==", },
        },
    },
}

GOODS_RECEIPT_APP_CONFIG = {
    "id": "dd16a86c-4aef-46ec-9302-19f30b101cf5",
    "title": "Goods Receipt",
    "code": "goodsreceipt",
    "model_code": "goodsreceipt",
    "app_label": "inventory",
    "is_workflow": True,
    "app_depend_on": [
        "81a111ef-9c32-4cbd-8601-a3cce884badb",  # Purchase order
        "4e48c863-861b-475a-aa5e-97a4ed26f294",  # Account
        "828b785a-8f57-4a03-9f90-e0edf96560d7",  # Contact
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
                "81a111ef-9c32-4cbd-8601-a3cce884badb": {"view": "==", },
                "4e48c863-861b-475a-aa5e-97a4ed26f294": {"view": "==", },
                "828b785a-8f57-4a03-9f90-e0edf96560d7": {"view": "==", },
            },
            "local_depends_on": {
                "view": "==",
            },
        },
        "edit": {
            "range": ["1", "2", "3", "4"],
            "app_depends_on": {
                "81a111ef-9c32-4cbd-8601-a3cce884badb": {"view": "==", },
                "4e48c863-861b-475a-aa5e-97a4ed26f294": {"view": "==", },
                "828b785a-8f57-4a03-9f90-e0edf96560d7": {"view": "==", },
            },
            "local_depends_on": {
                "view": "==",
            },
        },
        "delete": {
            "range": ["1", "2", "3", "4"],
            "app_depends_on": {
                "81a111ef-9c32-4cbd-8601-a3cce884badb": {"view": "==", },
                "4e48c863-861b-475a-aa5e-97a4ed26f294": {"view": "==", },
                "828b785a-8f57-4a03-9f90-e0edf96560d7": {"view": "==", },
            },
            "local_depends_on": {
                "view": "==",
            },
        },
    },
}

GOODS_TRANSFER_APP_CONFIG = {
    "id": "866f163d-b724-404d-942f-4bc44dc2e2ed",
    "title": "Goods Transfer",
    "code": "goodstransfer",
    "model_code": "goodstransfer",
    "app_label": "inventory",
    "is_workflow": True,
    "app_depend_on": [
        "4e48c863-861b-475a-aa5e-97a4ed26f294",  # Account
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
            },
            "local_depends_on": {
                "view": "==",
            },
        },
        "edit": {
            "range": ["1", "2", "3", "4"],
            "app_depends_on": {
                "4e48c863-861b-475a-aa5e-97a4ed26f294": {"view": "==", },
            },
            "local_depends_on": {
                "view": "==",
            },
        },
        "delete": {
            "range": ["1", "2", "3", "4"],
            "app_depends_on": {
                "4e48c863-861b-475a-aa5e-97a4ed26f294": {"view": "==", },
            },
            "local_depends_on": {
                "view": "==",
            },
        },
    },
}

GOODS_ISSUE_APP_CONFIG = {
    "id": "f26d7ce4-e990-420a-8ec6-2dc307467f2c",
    "title": "Goods Issue",
    "code": "goodsissue",
    "model_code": "goodsissue",
    "app_label": "inventory",
    "is_workflow": True,
    "app_depend_on": [
        "c5de0a7d-bea3-4f39-922f-06a40a060aba",  # Inventory Adjustment
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
                "c5de0a7d-bea3-4f39-922f-06a40a060aba": {"view": "==", },
            },
            "local_depends_on": {
                "view": "==",
            },
        },
        "edit": {
            "range": ["1", "2", "3", "4"],
            "app_depends_on": {
                "c5de0a7d-bea3-4f39-922f-06a40a060aba": {"view": "==", },
            },
            "local_depends_on": {
                "view": "==",
            },
        },
        "delete": {
            "range": ["1", "2", "3", "4"],
            "app_depends_on": {
                "c5de0a7d-bea3-4f39-922f-06a40a060aba": {"view": "==", },
            },
            "local_depends_on": {
                "view": "==",
            },
        },
    },
}

GOODS_INVENTORY_ADJUSTMENT_APP_CONFIG = {
    "id": "c5de0a7d-bea3-4f39-922f-06a40a060aba",
    "title": "Inventory Adjustment",
    "code": "inventoryadjustment",
    "model_code": "inventoryadjustment",
    "app_label": "inventory",
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
            "app_depends_on": {
            },
            "local_depends_on": {
            },
        },
        "edit": {
            "range": ["1", "2", "3", "4"],
            "app_depends_on": {
            },
            "local_depends_on": {
            },
        },
        "delete": {
            "range": ["1", "2", "3", "4"],
            "app_depends_on": {
            },
            "local_depends_on": {
            },
        },
    },
}

REPORT_REVENUE_APP_CONFIG = {
    "id": "c3260940-21ff-4929-94fe-43bc4199d38b",
    "title": "Report Revenue",
    "code": "reportrevenue",
    "model_code": "reportrevenue",
    "app_label": "report",
    "is_workflow": False,
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
}

REPORT_PRODUCT_APP_CONFIG = {
    "id": "2a709d75-35a7-49c8-84bf-c350164405bc",
    "title": "Report Product",
    "code": "reportproduct",
    "model_code": "reportproduct",
    "app_label": "report",
    "is_workflow": False,
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
}

REPORT_CUSTOMER_APP_CONFIG = {
    "id": "d633036a-8937-4f9d-a227-420e061496fc",
    "title": "Report Customer",
    "code": "reportcustomer",
    "model_code": "reportcustomer",
    "app_label": "report",
    "is_workflow": False,
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
}

REPORT_PIPELINE_APP_CONFIG = {
    "id": "298c8b6f-6a62-493f-b0ac-d549a4541497",
    "title": "Report Pipeline",
    "code": "reportpipeline",
    "model_code": "reportpipeline",
    "app_label": "report",
    "is_workflow": False,
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
}

REVENUE_PLAN_APP_CONFIG = {
    "id": "e4ae0a2c-2130-4a65-b644-1b79db3d033b",
    "title": "Revenue Plan",
    "code": "revenueplan",
    "model_code": "revenueplan",
    "app_label": "revenue_plan",
    "is_workflow": False,
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
}

AR_INVOICE_APP_CONFIG = {
    "id": "1d7291dd-1e59-4917-83a3-1cc07cfc4638",
    "title": "AR Invoice",
    "code": "arinvoice",
    "model_code": "arinvoice",
    "app_label": "arinvoice",
    "is_workflow": False,
    "app_depend_on": [
        "4e48c863-861b-475a-aa5e-97a4ed26f294",  # Account
        "a870e392-9ad2-4fe2-9baa-298a38691cf2",  # Sale Order
        "1373e903-909c-4b77-9957-8bcf97e8d6d3",  # Delivery
    ],
    "permit_mapping": {
        "view": {
            "range": ["1", "2", "3", "4"],
            "app_depends_on": {},
            "local_depends_on": {"view": "==", },
        },
        "create": {
            "range": ["1", "2", "3", "4"],
            "app_depends_on": {
                "4e48c863-861b-475a-aa5e-97a4ed26f294": {"view": "4", },
                "a870e392-9ad2-4fe2-9baa-298a38691cf2": {"view": "4", },
                "1373e903-909c-4b77-9957-8bcf97e8d6d3": {"view": "4", },
            },
            "local_depends_on": {
                "view": "==",
            },
        },
        "edit": {
            "range": ["1", "2", "3", "4"],
            "app_depends_on": {
                "4e48c863-861b-475a-aa5e-97a4ed26f294": {"view": "4", },
                "a870e392-9ad2-4fe2-9baa-298a38691cf2": {"view": "4", },
                "1373e903-909c-4b77-9957-8bcf97e8d6d3": {"view": "4", },
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

AP_INVOICE_APP_CONFIG = {
    "id": "c05a6cf4-efff-47e0-afcf-072017b8141a",
    "title": "AP Invoice",
    "code": "apinvoice",
    "model_code": "apinvoice",
    "app_label": "apinvoice",
    "is_workflow": False,
    "app_depend_on": [
        "4e48c863-861b-475a-aa5e-97a4ed26f294",  # Account
        "81a111ef-9c32-4cbd-8601-a3cce884badb",  # Purchase Order
        "dd16a86c-4aef-46ec-9302-19f30b101cf5",  # Goods receipt
    ],
    "permit_mapping": {
        "view": {
            "range": ["1", "2", "3", "4"],
            "app_depends_on": {},
            "local_depends_on": {"view": "==", },
        },
        "create": {
            "range": ["1", "2", "3", "4"],
            "app_depends_on": {
                "4e48c863-861b-475a-aa5e-97a4ed26f294": {"view": "4", },
                "81a111ef-9c32-4cbd-8601-a3cce884badb": {"view": "4", },
                "dd16a86c-4aef-46ec-9302-19f30b101cf5": {"view": "4", },
            },
            "local_depends_on": {
                "view": "==",
            },
        },
        "edit": {
            "range": ["1", "2", "3", "4"],
            "app_depends_on": {
                "4e48c863-861b-475a-aa5e-97a4ed26f294": {"view": "4", },
                "81a111ef-9c32-4cbd-8601-a3cce884badb": {"view": "4", },
                "dd16a86c-4aef-46ec-9302-19f30b101cf5": {"view": "4", },
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

GOODS_RETURN_APP_CONFIG = {
    "id": "0242ba77-8b02-4589-8ed9-239788083f2b",
    "title": "Goods Return",
    "code": "goodsreturn",
    "model_code": "goodsreturn",
    "app_label": "inventory",
    "is_workflow": True,
    "app_depend_on": [
        "a870e392-9ad2-4fe2-9baa-298a38691cf2",  # Sale Order
        "1373e903-909c-4b77-9957-8bcf97e8d6d3",  # Delivery
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
                "a870e392-9ad2-4fe2-9baa-298a38691cf2": {"view": "==", },
                "1373e903-909c-4b77-9957-8bcf97e8d6d3": {"view": "==", },
            },
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
}

REPORT_CASHFLOW_APP_CONFIG = {
    "id": "69e84b95-b347-4f49-abdf-0ec80d6eb5bd",
    "title": "Report Cashflow",
    "code": "reportcashflow",
    "model_code": "reportcashflow",
    "app_label": "report",
    "is_workflow": False,
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
}

REPORT_INVENTORY_APP_CONFIG = {
    "id": "c22a9e96-e56e-4636-9083-8ee1c66cb1b2",
    "title": "Report Inventory",
    "code": "reportinventory",
    "model_code": "reportinventory",
    "app_label": "report",
    "is_workflow": False,
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
}

# Nhóm 1: các chức năng quản lý phân quyền theo space opportunity
#   - Các activity: Call, Email, Document for customer
#   - Task
#   - Quotation
#   - Sale order
#   - Contract
#   - Advanced payment
#   - Payment
#   - Return payment
# Nhóm 2: các chức năng quản lý phân quyền theo space project
#   - Các activity: Call, Email, Document for customer
#   - Task
#   - Contract
#   - Advanced payment
#   - Payment
#   - Return payment
# Nhóm 3: Còn lại
#   - ...
# # # Tự trình bày: Các chức năng ở nhóm 1/2 sẽ có thêm spacing_allow = "1"

Application_crm_data = {
    # Nhóm 1 ^ 2
    "14dbc606-1453-4023-a2cf-35b1cd9e3efd": ApplicationConfigFrame(**CALL_LOG_APP_CONFIG).data(
        depend_follow_main=True,
        filtering_inheritor=True,
        spacing_allow=["0", "1"],
    ),
    "dec012bf-b931-48ba-a746-38b7fd7ca73b": ApplicationConfigFrame(**EMAIL_LOG_APP_CONFIG).data(
        depend_follow_main=True,
        filtering_inheritor=True,
        spacing_allow=["0", "1"],
    ),
    "319356b4-f16c-4ba4-bdcb-e1b0c2a2c124": ApplicationConfigFrame(**DOCUMENT_FOR_CUSTOMER_APP_CONFIG).data(
        depend_follow_main=True,
        filtering_inheritor=True,
        spacing_allow=["0", "1"],
    ),
    "e66cfb5a-b3ce-4694-a4da-47618f53de4c": ApplicationConfigFrame(**TASK_APP_CONFIG).data(
        depend_follow_main=True,
        filtering_inheritor=True,
        spacing_allow=["0", "1"],
    ),
    "31c9c5b0-717d-4134-b3d0-cc4ca174b168": ApplicationConfigFrame(**CONTRACT_APP_CONFIG).data(
        depend_follow_main=True,
        filtering_inheritor=True,
        spacing_allow=["0", "1"],
    ),
    "57725469-8b04-428a-a4b0-578091d0e4f5": ApplicationConfigFrame(**ADVANCE_PAYMENT_APP_CONFIG).data(
        depend_follow_main=True,
        filtering_inheritor=True,
        spacing_allow=["0", "1"],
    ),
    "1010563f-7c94-42f9-ba99-63d5d26a1aca": ApplicationConfigFrame(**PAYMENT_APP_CONFIG).data(
        depend_follow_main=True,
        filtering_inheritor=True,
        spacing_allow=["0", "1"],
    ),
    "65d36757-557e-4534-87ea-5579709457d7": ApplicationConfigFrame(**RETURN_ADVANCE_APP_CONFIG).data(
        depend_follow_main=True,
        filtering_inheritor=True,
        spacing_allow=["0", "1"],
    ),

    # Nhóm 1
    "a870e392-9ad2-4fe2-9baa-298a38691cf2": ApplicationConfigFrame(**SALEORDER_APP_CONFIG).data(
        depend_follow_main=True,
        filtering_inheritor=True,
        spacing_allow=["0", "1"],
    ),
    "b9650500-aba7-44e3-b6e0-2542622702a3": ApplicationConfigFrame(**QUOTATION_APP_CONFIG).data(
        depend_follow_main=True,
        filtering_inheritor=True,
        spacing_allow=["0", "1"],
    ),

    # Nhóm 2

    # Nhóm 3
    "828b785a-8f57-4a03-9f90-e0edf96560d7": ApplicationConfigFrame(**CONTACT_APP_CONFIG).data(
        depend_follow_main=False,
        filtering_inheritor=True,
    ),
    "4e48c863-861b-475a-aa5e-97a4ed26f294": ApplicationConfigFrame(**ACCOUNT_APP_CONFIG).data(
        depend_follow_main=False,
        filtering_inheritor=True,
    ),
    "296a1410-8d72-46a8-a0a1-1821f196e66c": ApplicationConfigFrame(**OPPORTUNITY_APP_CONFIG).data(
        depend_follow_main=False,
        filtering_inheritor=True,
        spacing_allow=["0", "1"],
    ),
    "a8badb2e-54ff-4654-b3fd-0d2d3c777538": ApplicationConfigFrame(**PRODUCT_APP_CONFIG).data(
        depend_follow_main=False,
        filtering_inheritor=False,
    ),
    "022375ce-c99c-4f11-8841-0a26c85f2fc2": ApplicationConfigFrame(**EXPENSES_APP_CONFIG).data(
        depend_follow_main=False,
        filtering_inheritor=False,
    ),
    "80b8cd4f-cfba-4f33-9642-a4dd6ee31efd": ApplicationConfigFrame(**WAREHOUSE_APP_CONFIG).data(
        depend_follow_main=False,
        filtering_inheritor=False,
    ),
    "3d8ad524-5dd9-4a8b-a7cd-a9a371315a2a": ApplicationConfigFrame(**PICKING_APP_CONFIG).data(
        depend_follow_main=False,
        filtering_inheritor=True,
    ),
    "1373e903-909c-4b77-9957-8bcf97e8d6d3": ApplicationConfigFrame(**DELIVERY_APP_CONFIG).data(
        depend_follow_main=False,
        filtering_inheritor=True,
    ),
    "10a5e913-fa51-4127-a632-a8347a55c4bb": ApplicationConfigFrame(**PRICES_APP_CONFIG).data(
        depend_follow_main=False,
        filtering_inheritor=False,
    ),
    "e6a00a1a-d4f9-41b7-b0de-bb1efbe8446a": ApplicationConfigFrame(**SHIPPING_APP_CONFIG).data(
        depend_follow_main=False,
        filtering_inheritor=False,
    ),
    "f57b9e92-cb01-42e3-b7fe-6166ecd18e9c": ApplicationConfigFrame(**PROMOTION_APP_CONFIG).data(
        depend_follow_main=False,
        filtering_inheritor=False,
    ),
    "3407d35d-27ce-407e-8260-264574a216e3": ApplicationConfigFrame(**PAYMENT_TERM_APP_CONFIG).data(
        depend_follow_main=False,
        filtering_inheritor=False,
    ),
    "2fe959e3-9628-4f47-96a1-a2ef03e867e3": ApplicationConfigFrame(**MEETING_LOG_APP_CONFIG).data(
        depend_follow_main=False,
        filtering_inheritor=True,
    ),
    "d78bd5f3-8a8d-48a3-ad62-b50d576ce173": ApplicationConfigFrame(**PURCHASE_QUOTATION_REQUEST_APP_CONFIG).data(
        depend_follow_main=False,
        filtering_inheritor=True,
    ),
    "f52a966a-2eb2-4851-852d-eff61efeb896": ApplicationConfigFrame(**PURCHASE_QUOTATION_APP_CONFIG).data(
        depend_follow_main=False,
        filtering_inheritor=True,
    ),
    "81a111ef-9c32-4cbd-8601-a3cce884badb": ApplicationConfigFrame(**PURCHASE_ORDER_APP_CONFIG).data(
        depend_follow_main=False,
        filtering_inheritor=True,
    ),
    "fbff9b3f-f7c9-414f-9959-96d3ec2fb8bf": ApplicationConfigFrame(**PURCHASE_REQUEST_APP_CONFIG).data(
        depend_follow_main=False,
        filtering_inheritor=True,
    ),
    "245e9f47-df59-4d4a-b355-7eff2859247f": ApplicationConfigFrame(**EXPENSE_ITEM_APP_CONFIG).data(
        depend_follow_main=False,
        filtering_inheritor=False,
    ),
    "dd16a86c-4aef-46ec-9302-19f30b101cf5": ApplicationConfigFrame(**GOODS_RECEIPT_APP_CONFIG).data(
        depend_follow_main=False,
        filtering_inheritor=False,
    ),
    "866f163d-b724-404d-942f-4bc44dc2e2ed": ApplicationConfigFrame(**GOODS_TRANSFER_APP_CONFIG).data(
        depend_follow_main=False,
        filtering_inheritor=False,
    ),
    "f26d7ce4-e990-420a-8ec6-2dc307467f2c": ApplicationConfigFrame(**GOODS_ISSUE_APP_CONFIG).data(
        depend_follow_main=False,
        filtering_inheritor=False,
    ),
    "c5de0a7d-bea3-4f39-922f-06a40a060aba": ApplicationConfigFrame(**GOODS_INVENTORY_ADJUSTMENT_APP_CONFIG).data(
        depend_follow_main=False,
        filtering_inheritor=True,
    ),
    "c3260940-21ff-4929-94fe-43bc4199d38b": ApplicationConfigFrame(**REPORT_REVENUE_APP_CONFIG).data(
        depend_follow_main=False,
        filtering_inheritor=True,
    ),
    "2a709d75-35a7-49c8-84bf-c350164405bc": ApplicationConfigFrame(**REPORT_PRODUCT_APP_CONFIG).data(
        depend_follow_main=False,
        filtering_inheritor=True,
    ),
    "d633036a-8937-4f9d-a227-420e061496fc": ApplicationConfigFrame(**REPORT_CUSTOMER_APP_CONFIG).data(
        depend_follow_main=False,
        filtering_inheritor=True,
    ),
    "298c8b6f-6a62-493f-b0ac-d549a4541497": ApplicationConfigFrame(**REPORT_PIPELINE_APP_CONFIG).data(
        depend_follow_main=False,
        filtering_inheritor=True,
    ),
    "e4ae0a2c-2130-4a65-b644-1b79db3d033b": ApplicationConfigFrame(**REVENUE_PLAN_APP_CONFIG).data(
        depend_follow_main=False,
        filtering_inheritor=True,
    ),
    "1d7291dd-1e59-4917-83a3-1cc07cfc4638": ApplicationConfigFrame(**AR_INVOICE_APP_CONFIG).data(
        depend_follow_main=False,
        filtering_inheritor=True,
    ),
    "c05a6cf4-efff-47e0-afcf-072017b8141a": ApplicationConfigFrame(**AP_INVOICE_APP_CONFIG).data(
        depend_follow_main=False,
        filtering_inheritor=True,
    ),
    "0242ba77-8b02-4589-8ed9-239788083f2b": ApplicationConfigFrame(**GOODS_RETURN_APP_CONFIG).data(
        depend_follow_main=False,
        filtering_inheritor=True,
    ),
    "69e84b95-b347-4f49-abdf-0ec80d6eb5bd": ApplicationConfigFrame(**REPORT_CASHFLOW_APP_CONFIG).data(
        depend_follow_main=False,
        filtering_inheritor=True,
    ),
    "c22a9e96-e56e-4636-9083-8ee1c66cb1b2": ApplicationConfigFrame(**REPORT_INVENTORY_APP_CONFIG).data(
        depend_follow_main=False,
        filtering_inheritor=True,
    ),
}
