from apps.sharedapp.data.base.settings import ApplicationConfigFrame

__all__ = [
    'Application_crm_data',
]

CURRENCY_APP_CONFIG = {
    "id": "1102a36d-5dbe-48f6-845e-a6e0e69e04b2",
    "title": "Currency",
    "code": "currency",
    "permit_mapping": {},
    "model_code": "currency",
    "app_label": "saledata",
    "allow_import": True,
}

ACCOUNT_GROUP_APP_CONFIG = {
    "id": "35b38745-ba92-4d97-b1f7-4675a46585d3",
    "title": "Account Group",
    "code": "accountgroup",
    "permit_mapping": {},
    "model_code": "accountgroup",
    "app_label": "saledata",
    "allow_import": True,
}

ACCOUNT_TYPE_APP_CONFIG = {
    "id": "b22a58d3-cc9e-4913-a06d-beee11afba60",
    "title": "Account Type",
    "code": "accounttype",
    "permit_mapping": {},
    "model_code": "accounttype",
    "app_label": "saledata",
    # "allow_import": True,
}

INDUSTRY_APP_CONFIG = {
    "id": "37eb1961-8103-46c5-ad2e-236f3a6585f5",
    "title": "Industry",
    "code": "industry",
    "permit_mapping": {},
    "model_code": "industry",
    "app_label": "saledata",
    "allow_import": True,
}

SALUTATION_APP_CONFIG = {
    "id": "d3903adb-61a9-4b18-90ed-542ce7acedc8",
    "title": "Salutation",
    "code": "salutation",
    "model_code": "salutation",
    "app_label": "saledata",
    "allow_import": True,
}

UOM_GROUP_APP_CONFIG = {
    "id": "eb5c547f-3a68-4113-8aa3-a1f938c9d3a7",
    "title": "Unit Of Measure Group",
    "code": "unitofmeasuregroup",
    "permit_mapping": {},
    "model_code": "unitofmeasuregroup",
    "app_label": "saledata",
    "allow_import": True,
}

PRODUCT_TYPE_APP_CONFIG = {
    "id": "90f07280-e2f4-4406-aa23-ba255a22ec2d",
    "title": "Product Type",
    "code": "producttype",
    "permit_mapping": {},
    "model_code": "producttype",
    "app_label": "saledata",
    # "allow_import": True,
}

PRODUCT_CATEGORY_APP_CONFIG = {
    "id": "053c0804-162a-4357-a1c2-2161e6606cc2",
    "title": "Product Category",
    "code": "productcategory",
    "permit_mapping": {},
    "model_code": "productcategory",
    "app_label": "saledata",
    "allow_import": True,
}

PRODUCT_MANUFACTURER_APP_CONFIG = {
    "id": "d6e7d038-aef7-4e4e-befd-b13895974ec5",
    "title": "Manufacturer",
    "code": "manufacturer",
    "permit_mapping": {},
    "model_code": "manufacturer",
    "app_label": "saledata",
    "allow_import": True,
}

UOM_APP_CONFIG = {
    "id": "7bc78f47-66f1-4104-a6fa-5ca07f3f2275",
    "title": "Unit Of Measure",
    "code": "unitofmeasure",
    "permit_mapping": {},
    "model_code": "unitofmeasure",
    "app_label": "saledata",
    "allow_import": True,
}

TAX_APP_CONFIG = {
    "id": "720d14f9-e031-4ffe-acb9-3c7763c134fc",
    "title": "Tax",
    "code": "tax",
    "permit_mapping": {},
    "model_code": "tax",
    "app_label": "saledata",
    "allow_import": True,
}

TAX_CATEGORY_APP_CONFIG = {
    "id": "133e105e-cb3f-4845-8fba-bbb2516c5de2",
    "title": "Tax Category",
    "code": "taxcategory",
    "permit_mapping": {},
    "model_code": "taxcategory",
    "app_label": "saledata",
    "allow_import": True,
}

CONTACT_APP_CONFIG = {
    "id": "828b785a-8f57-4a03-9f90-e0edf96560d7",
    "title": "Contact",
    "code": "contact",
    "model_code": "contact",
    "app_label": "saledata",
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
                    "view": "==",
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
                    "view": "==",
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
    },
    "allow_permit": True,
    "allow_import": True,
}

ACCOUNT_APP_CONFIG = {
    "id": "4e48c863-861b-475a-aa5e-97a4ed26f294",
    "title": "Account",
    "code": "account",
    "model_code": "account",
    "app_label": "saledata",
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
                    "view": "==",
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
                    "view": "==",
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
    },
    "allow_permit": True,
    "allow_import": True,
}

OPPORTUNITY_APP_CONFIG = {
    "id": "296a1410-8d72-46a8-a0a1-1821f196e66c",
    "title": "Opportunity",
    "code": "opportunity",
    "model_code": "opportunity",
    "app_label": "opportunity",
    "is_workflow": False,
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
                "50348927-2c4f-4023-b638-445469c66953": {"view": "==", },
                "4e48c863-861b-475a-aa5e-97a4ed26f294": {"view": "==", },
                "828b785a-8f57-4a03-9f90-e0edf96560d7": {"view": "==", },
                "a8badb2e-54ff-4654-b3fd-0d2d3c777538": {"view": "==", },
            },
            "local_depends_on": {
                "view": "==",
            },
        },
        "edit": {
            "range": ["1", "2", "3", "4"],
            "app_depends_on": {
                "50348927-2c4f-4023-b638-445469c66953": {"view": "==", },
                "4e48c863-861b-475a-aa5e-97a4ed26f294": {"view": "==", },
                "828b785a-8f57-4a03-9f90-e0edf96560d7": {"view": "==", },
                "a8badb2e-54ff-4654-b3fd-0d2d3c777538": {"view": "==", },
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
                "296a1410-8d72-46a8-a0a1-1821f196e66c": {"view": "==", },
                "50348927-2c4f-4023-b638-445469c66953": {"view": "==", },
            },
            "local_depends_on": {"view": "==", },
        },
        "edit": {
            "range": ["1", "2", "3", "4"],
            "app_depends_on": {
                "296a1410-8d72-46a8-a0a1-1821f196e66c": {"view": "==", },
                "50348927-2c4f-4023-b638-445469c66953": {"view": "==", },
            },
            "local_depends_on": {"view": "==", },
        },
        "delete": {
            "range": ["1", "2", "3", "4"],
            "app_depends_on": {},
            "local_depends_on": {"view": "==", },
        },
    },
    "allow_permit": True,
    "allow_process": True,
    "allow_opportunity": True,
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
        "3407d35d-27ce-407e-8260-264574a216e3",  # Payment Term
        "f57b9e92-cb01-42e3-b7fe-6166ecd18e9c",  # Promotion
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
                "3407d35d-27ce-407e-8260-264574a216e3": {"view": "==", },
                "f57b9e92-cb01-42e3-b7fe-6166ecd18e9c": {"view": "==", },
            },
            "local_depends_on": {"view": "==", },
        },
        "edit": {
            "range": ["1", "2", "3", "4"],
            "app_depends_on": {
                "296a1410-8d72-46a8-a0a1-1821f196e66c": {"view": "==", },
                "4e48c863-861b-475a-aa5e-97a4ed26f294": {"view": "==", },
                "828b785a-8f57-4a03-9f90-e0edf96560d7": {"view": "==", },
                "3407d35d-27ce-407e-8260-264574a216e3": {"view": "==", },
                "f57b9e92-cb01-42e3-b7fe-6166ecd18e9c": {"view": "==", },
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
    "allow_mail": True,
    "allow_permit": True,
    "allow_process": True,
    "allow_opportunity": True,
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
        "3407d35d-27ce-407e-8260-264574a216e3",  # Payment Term
        "f57b9e92-cb01-42e3-b7fe-6166ecd18e9c",  # Promotion
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
                "3407d35d-27ce-407e-8260-264574a216e3": {"view": "==", },
                "f57b9e92-cb01-42e3-b7fe-6166ecd18e9c": {"view": "==", },
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
                "3407d35d-27ce-407e-8260-264574a216e3": {"view": "==", },
                "f57b9e92-cb01-42e3-b7fe-6166ecd18e9c": {"view": "==", },
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
    "allow_print": True,
    "allow_permit": True,
    "allow_process": True,
    "allow_opportunity": True,
    "allow_recurrence": True,
}

PRODUCT_APP_CONFIG = {
    "id": "a8badb2e-54ff-4654-b3fd-0d2d3c777538",
    "title": "Product",
    "code": "product",
    "model_code": "product",
    "app_label": "saledata",
    "is_workflow": False,
    "allow_permit": True,
    "allow_import": True,
}

EXPENSES_APP_CONFIG = {
    "id": "022375ce-c99c-4f11-8841-0a26c85f2fc2",
    "title": "Internal labor item",
    "code": "expenses",
    "model_code": "expenses",
    "app_label": "saledata",
    "is_workflow": False,
    "allow_permit": True,
}

EXPENSE_ITEM_APP_CONFIG = {
    "id": "245e9f47-df59-4d4a-b355-7eff2859247f",
    "title": "Expense Item",
    "code": "expenseitem",
    "model_code": "expenseitem",
    "app_label": "saledata",
    "is_workflow": False,
    "allow_permit": True,
}

WAREHOUSE_APP_CONFIG = {
    "id": "80b8cd4f-cfba-4f33-9642-a4dd6ee31efd",
    "title": "Warehouse",
    "code": "warehouse",
    "model_code": "warehouse",
    "app_label": "saledata",
    "is_workflow": False,
    "allow_permit": True,
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
                "80b8cd4f-cfba-4f33-9642-a4dd6ee31efd": {"view": "==", },
            },
            "local_depends_on": {"view": "==", },
        },
        "edit": {
            "range": ["1", "3", "4"],
            "app_depends_on": {
                "80b8cd4f-cfba-4f33-9642-a4dd6ee31efd": {"view": "==", },
            },
            "local_depends_on": {"view": "==", },
        },
        "delete": {
            "range": ["1", "3", "4"],
            "app_depends_on": {},
            "local_depends_on": {"view": "==", },
        },
    },
    "allow_permit": True,
}

DELIVERY_APP_CONFIG = {
    "id": "1373e903-909c-4b77-9957-8bcf97e8d6d3",
    "title": "Delivery",
    "code": "orderdeliverysub",
    "model_code": "orderdeliverysub",
    "app_label": "delivery",
    "is_workflow": True,
    "app_depend_on": [
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
                "4e48c863-861b-475a-aa5e-97a4ed26f294": {"view": "==", },
            },
            "local_depends_on": {"view": "==", },
        },
        "edit": {
            "range": ["1", "3", "4"],
            "app_depends_on": {
                "4e48c863-861b-475a-aa5e-97a4ed26f294": {"view": "==", },
            },
            "local_depends_on": {"view": "==", },
        },
        "delete": {
            "range": ["1", "3", "4"],
            "app_depends_on": {},
            "local_depends_on": {"view": "==", },
        },
    },
    "allow_print": True,
    "allow_mail": True,
    "allow_permit": True,
    "allow_process": True,
}

PRICES_APP_CONFIG = {
    "id": "10a5e913-fa51-4127-a632-a8347a55c4bb",
    "title": "Prices",
    "code": "price",
    "model_code": "price",
    "app_label": "saledata",
    "is_workflow": False,
    "allow_permit": True,
}

SHIPPING_APP_CONFIG = {
    "id": "e6a00a1a-d4f9-41b7-b0de-bb1efbe8446a",
    "title": "Shipping",
    "code": "shipping",
    "model_code": "shipping",
    "app_label": "saledata",
    "is_workflow": False,
    "allow_permit": True,
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
                "828b785a-8f57-4a03-9f90-e0edf96560d7": {"view": "==", },
                "a8badb2e-54ff-4654-b3fd-0d2d3c777538": {"view": "==", },
            },
            "local_depends_on": {"view": "==", },
        },
        "edit": {
            "range": ["1", "2", "3", "4"],
            "app_depends_on": {
                "828b785a-8f57-4a03-9f90-e0edf96560d7": {"view": "==", },
                "a8badb2e-54ff-4654-b3fd-0d2d3c777538": {"view": "==", },
            },
            "local_depends_on": {"view": "==", },
        },
        "delete": {
            "range": ["1", "2", "3", "4"],
            "app_depends_on": {},
            "local_depends_on": {"view": "==", },
        },
    },
    "allow_permit": True,
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
                    "view": "=="
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
                    "view": "=="
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
    "allow_process": True,
    "allow_opportunity": True,
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
                "a870e392-9ad2-4fe2-9baa-298a38691cf2": {"view": "==", },
                "b9650500-aba7-44e3-b6e0-2542622702a3": {"view": "==", },
                "296a1410-8d72-46a8-a0a1-1821f196e66c": {"view": "==", },
                "4e48c863-861b-475a-aa5e-97a4ed26f294": {"view": "==", },
                "50348927-2c4f-4023-b638-445469c66953": {"view": "==", },
                "57725469-8b04-428a-a4b0-578091d0e4f5": {"view": "==", },
            },
            "local_depends_on": {
                "view": "==",
            },
        },
        "edit": {
            "range": ["1", "2", "3", "4"],
            "app_depends_on": {
                "a870e392-9ad2-4fe2-9baa-298a38691cf2": {"view": "==", },
                "b9650500-aba7-44e3-b6e0-2542622702a3": {"view": "==", },
                "296a1410-8d72-46a8-a0a1-1821f196e66c": {"view": "==", },
                "4e48c863-861b-475a-aa5e-97a4ed26f294": {"view": "==", },
                "50348927-2c4f-4023-b638-445469c66953": {"view": "==", },
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
    "allow_permit": True,
    "allow_print": True,
    "allow_process": True,
    "allow_opportunity": True,
    "allow_recurrence": False,
}

PAYMENT_TERM_APP_CONFIG = {
    "id": "3407d35d-27ce-407e-8260-264574a216e3",
    "title": "Payment Term",
    "code": "paymentterm",
    "model_code": "paymentterm",
    "app_label": "saledata",
    "is_workflow": False,
    "allow_permit": True,
    "allow_import": True,
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
                "57725469-8b04-428a-a4b0-578091d0e4f5": {"view": "==", },
                "50348927-2c4f-4023-b638-445469c66953": {"view": "==", },
            },
            "local_depends_on": {
                "view": "==",
            },
        },
        "edit": {
            "range": ["1", "4"],
            "app_depends_on": {
                "57725469-8b04-428a-a4b0-578091d0e4f5": {"view": "==", },
                "50348927-2c4f-4023-b638-445469c66953": {"view": "==", },
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
    "allow_permit": True,
    "allow_process": True,
}

DOCUMENT_FOR_CUSTOMER_APP_CONFIG = {
    "id": "319356b4-f16c-4ba4-bdcb-e1b0c2a2c124",
    "title": "Document For Customer",
    "code": "documentforcustomer",
    "model_code": "documentforcustomer",
    "app_label": "opportunity",
    "is_workflow": False,
    "allow_permit": True,
    "allow_process": True,
}

CALL_LOG_APP_CONFIG = {
    "id": "14dbc606-1453-4023-a2cf-35b1cd9e3efd",
    "title": "Call",
    "code": "opportunitycall",
    "model_code": "opportunitycall",
    "app_label": "opportunity",
    "permit_mapping": {
        "view": {
            "range": ["1", "4"],
            "app_depends_on": {},
            "local_depends_on": {},
        },
        "create": {
            "range": ["1", "4"],
            "app_depends_on": {},
            "local_depends_on": {
                "view": "==",
            },
        },
        "edit": {
            "range": ["1", "4"],
            "app_depends_on": {},
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
    "is_workflow": False,
    "allow_permit": True,
    "allow_process": True,
    "allow_opportunity": True,
}

EMAIL_LOG_APP_CONFIG = {
    "id": "dec012bf-b931-48ba-a746-38b7fd7ca73b",
    "title": "Email",
    "code": "opportunityemail",
    "model_code": "opportunityemail",
    "app_label": "opportunity",
    "permit_mapping": {
        "view": {
            "range": ["1", "4"],
            "app_depends_on": {},
            "local_depends_on": {},
        },
        "create": {
            "range": ["1", "4"],
            "app_depends_on": {},
            "local_depends_on": {
                "view": "==",
            },
        },
        "edit": {
            "range": ["1", "4"],
            "app_depends_on": {},
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
    "is_workflow": False,
    "allow_permit": True,
    "allow_process": True,
    "allow_opportunity": True,
}

MEETING_LOG_APP_CONFIG = {
    "id": "2fe959e3-9628-4f47-96a1-a2ef03e867e3",
    "title": "Meeting With Customer",
    "code": "meetingwithcustomer",
    "model_code": "meetingwithcustomer",
    "app_label": "opportunity",
    "permit_mapping": {
        "view": {
            "range": ["1", "4"],
            "app_depends_on": {},
            "local_depends_on": {},
        },
        "create": {
            "range": ["1", "4"],
            "app_depends_on": {},
            "local_depends_on": {
                "view": "==",
            },
        },
        "edit": {
            "range": ["1", "4"],
            "app_depends_on": {},
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
    "is_workflow": False,
    "allow_permit": True,
    "allow_process": True,
    "allow_opportunity": True,
}

CONTRACT_APP_CONFIG = {
    "id": "31c9c5b0-717d-4134-b3d0-cc4ca174b168",
    "title": "Contract",
    "code": "contract",
    "model_code": "contract",
    "app_label": "contract",
    "is_workflow": False,
    "allow_permit": False,
    "allow_process": False,
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
                "a8badb2e-54ff-4654-b3fd-0d2d3c777538": {"view": "==", },
            },
            "local_depends_on": {"view": "==", },
        },
        "edit": {
            "range": ["1", "2", "3", "4"],
            "app_depends_on": {
                "fbff9b3f-f7c9-414f-9959-96d3ec2fb8bf": {"view": "==", },
                "a8badb2e-54ff-4654-b3fd-0d2d3c777538": {"view": "==", },
            },
            "local_depends_on": {"view": "==", },
        },
        "delete": {
            "range": ["1", "2", "3", "4"],
            "app_depends_on": {
                "fbff9b3f-f7c9-414f-9959-96d3ec2fb8bf": {"view": "==", },
                "a8badb2e-54ff-4654-b3fd-0d2d3c777538": {"view": "==", },
            },
            "local_depends_on": {"view": "==", },
        },
    },
    "allow_permit": True,
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
                "4e48c863-861b-475a-aa5e-97a4ed26f294": {"view": "==", },
                "828b785a-8f57-4a03-9f90-e0edf96560d7": {"view": "==", },
                "d78bd5f3-8a8d-48a3-ad62-b50d576ce173": {"view": "==", },
                "a8badb2e-54ff-4654-b3fd-0d2d3c777538": {"view": "==", },
            },
            "local_depends_on": {"view": "==", },
        },
        "edit": {
            "range": ["1", "2", "3", "4"],
            "app_depends_on": {
                "4e48c863-861b-475a-aa5e-97a4ed26f294": {"view": "==", },
                "828b785a-8f57-4a03-9f90-e0edf96560d7": {"view": "==", },
                "d78bd5f3-8a8d-48a3-ad62-b50d576ce173": {"view": "==", },
                "a8badb2e-54ff-4654-b3fd-0d2d3c777538": {"view": "==", },
            },
            "local_depends_on": {"view": "==", },
        },
        "delete": {
            "range": ["1", "2", "3", "4"],
            "app_depends_on": {},
            "local_depends_on": {"view": "==", },
        },
    },
    "allow_permit": True,
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
        "f52a966a-2eb2-4851-852d-eff61efeb896",  # Purchase Quotation
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
                "f52a966a-2eb2-4851-852d-eff61efeb896": {"view": "==", },
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
                "f52a966a-2eb2-4851-852d-eff61efeb896": {"view": "==", },
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
}

PURCHASE_REQUEST_APP_CONFIG = {
    "id": "fbff9b3f-f7c9-414f-9959-96d3ec2fb8bf",
    "title": "Purchase Request",
    "code": "purchaserequest",
    "model_code": "purchaserequest",
    "app_label": "purchasing",
    "is_workflow": True,
    "app_depend_on": [
        "a870e392-9ad2-4fe2-9baa-298a38691cf2",  # Sale Order
        "57a32d5a-3580-43b7-bf31-953a1afc68f4",  # Distribution plan
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
                "a870e392-9ad2-4fe2-9baa-298a38691cf2": {"view": "==", },
                "57a32d5a-3580-43b7-bf31-953a1afc68f4": {"view": "==", },
                "4e48c863-861b-475a-aa5e-97a4ed26f294": {"view": "==", },
                "828b785a-8f57-4a03-9f90-e0edf96560d7": {"view": "==", },
                "a8badb2e-54ff-4654-b3fd-0d2d3c777538": {"view": "==", },
            },
            "local_depends_on": {"view": "==", },
        },
        "edit": {
            "range": ["1", "2", "3", "4"],
            "app_depends_on": {
                "a870e392-9ad2-4fe2-9baa-298a38691cf2": {"view": "==", },
                "57a32d5a-3580-43b7-bf31-953a1afc68f4": {"view": "==", },
                "4e48c863-861b-475a-aa5e-97a4ed26f294": {"view": "==", },
                "828b785a-8f57-4a03-9f90-e0edf96560d7": {"view": "==", },
                "a8badb2e-54ff-4654-b3fd-0d2d3c777538": {"view": "==", },
            },
            "local_depends_on": {"view": "==", },
        },
        "delete": {
            "range": ["1", "2", "3", "4"],
            "app_depends_on": {},
            "local_depends_on": {"view": "==", },
        },
    },
    "allow_permit": True,
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
    "allow_permit": True,
}

GOODS_DETAIL_APP_CONFIG = {
    "id": "a943adf4-e00d-4cae-bb3e-78cca3efb09a",
    "title": "Goods Detail",
    "code": "goodsdetail",
    "model_code": "goodsdetail",
    "app_label": "inventory",
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
    "allow_permit": True,
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
    "allow_permit": True,
    "allow_print": True
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
    "allow_permit": True,
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
    "allow_permit": True,
    "allow_print": True
}

INVENTORY_ADJUSTMENT_APP_CONFIG = {
    "id": "c5de0a7d-bea3-4f39-922f-06a40a060aba",
    "title": "Inventory Adjustment",
    "code": "inventoryadjustment",
    "model_code": "inventoryadjustment",
    "app_label": "inventory",
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
    "allow_permit": True,
    "allow_print": True
}

REPORT_REVENUE_APP_CONFIG = {
    "id": "c3260940-21ff-4929-94fe-43bc4199d38b",
    "title": "Revenue Report",
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
    "allow_permit": True,
}

REPORT_PRODUCT_APP_CONFIG = {
    "id": "2a709d75-35a7-49c8-84bf-c350164405bc",
    "title": "Product Report",
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
    "allow_permit": True,
}

REPORT_CUSTOMER_APP_CONFIG = {
    "id": "d633036a-8937-4f9d-a227-420e061496fc",
    "title": "Customer Report",
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
    "allow_permit": True,
}

REPORT_PIPELINE_APP_CONFIG = {
    "id": "298c8b6f-6a62-493f-b0ac-d549a4541497",
    "title": "Pipeline Report",
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
    "allow_permit": True,
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
    "allow_permit": True,
}

AR_INVOICE_APP_CONFIG = {
    "id": "1d7291dd-1e59-4917-83a3-1cc07cfc4638",
    "title": "AR Invoice",
    "code": "arinvoice",
    "model_code": "arinvoice",
    "app_label": "arinvoice",
    "is_workflow": True,
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
                "4e48c863-861b-475a-aa5e-97a4ed26f294": {"view": "==", },
                "a870e392-9ad2-4fe2-9baa-298a38691cf2": {"view": "==", },
                "1373e903-909c-4b77-9957-8bcf97e8d6d3": {"view": "==", },
            },
            "local_depends_on": {
                "view": "==",
            },
        },
        "edit": {
            "range": ["1", "2", "3", "4"],
            "app_depends_on": {
                "4e48c863-861b-475a-aa5e-97a4ed26f294": {"view": "==", },
                "a870e392-9ad2-4fe2-9baa-298a38691cf2": {"view": "==", },
                "1373e903-909c-4b77-9957-8bcf97e8d6d3": {"view": "==", },
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
    "allow_recurrence": True,
}

AP_INVOICE_APP_CONFIG = {
    "id": "c05a6cf4-efff-47e0-afcf-072017b8141a",
    "title": "AP Invoice",
    "code": "apinvoice",
    "model_code": "apinvoice",
    "app_label": "apinvoice",
    "is_workflow": True,
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
                "4e48c863-861b-475a-aa5e-97a4ed26f294": {"view": "==", },
                "81a111ef-9c32-4cbd-8601-a3cce884badb": {"view": "==", },
                "dd16a86c-4aef-46ec-9302-19f30b101cf5": {"view": "==", },
            },
            "local_depends_on": {
                "view": "==",
            },
        },
        "edit": {
            "range": ["1", "2", "3", "4"],
            "app_depends_on": {
                "4e48c863-861b-475a-aa5e-97a4ed26f294": {"view": "==", },
                "81a111ef-9c32-4cbd-8601-a3cce884badb": {"view": "==", },
                "dd16a86c-4aef-46ec-9302-19f30b101cf5": {"view": "==", },
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
}

REPORT_CASHFLOW_APP_CONFIG = {
    "id": "69e84b95-b347-4f49-abdf-0ec80d6eb5bd",
    "title": "Cashflow Report",
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
    "allow_permit": True,
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
    "allow_permit": True,
}

FINAL_ACCEPTANCE_APP_CONFIG = {
    "id": "710c5a94-3a29-4e0e-973c-e6cace96c1e7",
    "title": "Final Acceptance",
    "code": "finalacceptance",
    "model_code": "finalacceptance",
    "app_label": "acceptance",
    "is_workflow": True,
    "app_depend_on": [
        "a870e392-9ad2-4fe2-9baa-298a38691cf2",  # Sale order
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
            },
            "local_depends_on": {
                "view": "==",
            },
        },
        "edit": {
            "range": ["1", "2", "3", "4"],
            "app_depends_on": {
                "a870e392-9ad2-4fe2-9baa-298a38691cf2": {"view": "==", },
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
    "allow_opportunity": True,
}

REPORT_PURCHASING_APP_CONFIG = {
    "id": "e696a636-0f36-4b20-970d-70035d6e1e37",
    "title": "Report Purchasing",
    "code": "reportpurchasing",
    "model_code": "reportpurchasing",
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
    "allow_permit": True,
}

LEAD_APP_CONFIG = {
    "id": "c04b2295-307f-49ed-80ab-1ca7f2b32d00",
    "title": "Lead",
    "code": "lead",
    "model_code": "lead",
    "app_label": "lead",
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
    "allow_permit": True,
}

SALE_PROJECT = {
    "id": "49fe2eb9-39cd-44af-b74a-f690d7b61b67",
    "title": "Project",
    "code": "project",
    "model_code": "project",
    "app_label": "project",
    "is_workflow": False,
    "option_permission": 0,
    "option_allowed": [1, 2, 3, 4],
    "app_depend_on": [
        "50348927-2c4f-4023-b638-445469c66953",  # Employee
        "e66cfb5a-b3ce-4694-a4da-47618f53de4c",  # Task
    ],
    "permit_mapping": {
        "view": {
            "range": ["1", "2", "3", "4"],
            "app_depends_on": {
                "50348927-2c4f-4023-b638-445469c66953": {"view": "==", },
                "e66cfb5a-b3ce-4694-a4da-47618f53de4c": {"view": "==", },
            },
            "local_depends_on": {
                "view": "==",
            },
        },
        "create": {
            "range": ["1", "2", "3", "4"],
            "app_depends_on": {
                "50348927-2c4f-4023-b638-445469c66953": {"view": "==", },
                "e66cfb5a-b3ce-4694-a4da-47618f53de4c": {"view": "==", },
            },
            "local_depends_on": {
                "view": "==",
            },
        },
        "edit": {
            "range": ["1", "2", "3", "4"],
            "app_depends_on": {
                "50348927-2c4f-4023-b638-445469c66953": {"view": "==", },
                "e66cfb5a-b3ce-4694-a4da-47618f53de4c": {"view": "==", },
            },
            "local_depends_on": {
                "view": "==",
            },
        },
        "delete": {
            "range": ["1", "2", "3", "4"],
            "app_depends_on": {
                "50348927-2c4f-4023-b638-445469c66953": {"view": "==", },
                "e66cfb5a-b3ce-4694-a4da-47618f53de4c": {"view": "==", },
            },
            "local_depends_on": {
                "view": "==",
            },
        },
    },
    "allow_permit": True,
    "allow_process": True,
}

SALE_PROJECT_BASELINE = {
    "id": "255d9f44-905f-4bc7-8256-316a6959b683",
    "title": "Project Baseline",
    "code": "projectbaseline",
    "model_code": "projectbaseline",
    "app_label": "project",
    "is_workflow": True,
    "option_permission": 0,
    "option_allowed": [1, 2, 3, 4],
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
    "allow_permit": True,
}

BUDGET_PLAN_APP_CONFIG = {
    "id": "ac21e8e4-fe32-41f4-9887-ee077677735c",
    "title": "Budget Plan",
    "code": "budgetplan",
    "model_code": "budgetplan",
    "app_label": "budget_plan",
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
    "allow_permit": True,
}

REPORT_BUDGET_APP_CONFIG = {
    "id": "b9fa8d62-4387-4fa5-9be3-d76d77614687",
    "title": "Report Budget",
    "code": "reportbudget",
    "model_code": "reportbudget",
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
    "allow_permit": True,
}

REGISTRATION_APP_CONFIG = {
    "id": "20ad27de-ea68-48a9-82bf-8833d7ab6da7",
    "title": "Goods Registration",
    "code": "goodsregistration",
    "model_code": "goodsregistration",
    "app_label": "inventory",
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
    "allow_permit": True,
}

DISTRIBUTION_PLAN_CONFIG = {
    "id": "57a32d5a-3580-43b7-bf31-953a1afc68f4",
    "title": "Goods Stock Plan",
    "code": "distributionplan",
    "model_code": "distributionplan",
    "app_label": "distributionplan",
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
}

CONTRACT_APPROVAL_APP_CONFIG = {
    "id": "58385bcf-f06c-474e-a372-cadc8ea30ecc",
    "title": "Contract Approval",
    "code": "contractapproval",
    "model_code": "contractapproval",
    "app_label": "contract",
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
    "allow_opportunity": True,
    "allow_process": True,
}

BOM_APP_CONFIG = {
    "id": "2de9fb91-4fb9-48c8-b54e-c03bd12f952b",
    "title": "Bill Of Material",
    "code": "bom",
    "model_code": "bom",
    "app_label": "production",
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
}

PRODUCTION_ORDER_APP_CONFIG = {
    "id": "a4a99ba0-5596-4ff8-8bd9-68414b5af579",
    "title": "Production Order",
    "code": "productionorder",
    "model_code": "productionorder",
    "app_label": "production",
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
}

WORK_ORDER_APP_CONFIG = {
    "id": "b698df99-3e8e-4183-ba5d-0eb55aeba1b2",
    "title": "Work Order",
    "code": "workorder",
    "model_code": "workorder",
    "app_label": "production",
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
    "allow_opportunity": True,
}

BIDDING_APP_CONFIG = {
    "id": "ad1e1c4e-2a7e-4b98-977f-88d069554657",
    "title": "Bidding",
    "code": "bidding",
    "model_code": "bidding",
    "app_label": "bidding",
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
    "allow_process": True,
    "allow_opportunity": True,
}

CONSULTING_APP_CONFIG = {
    "id": "3a369ba5-82a0-4c4d-a447-3794b67d1d02",
    "title": "Consulting",
    "code": "consulting",
    "model_code": "consulting",
    "app_label": "consulting",
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
    "allow_process": True,
    "allow_opportunity": True,
}

LEASEORDER_APP_CONFIG = {
    "id": "010404b3-bb91-4b24-9538-075f5f00ef14",
    "title": "Lease Order",
    "code": "leaseorder",
    "model_code": "leaseorder",
    "app_label": "leaseorder",
    "is_workflow": True,
    "app_depend_on": [
        "296a1410-8d72-46a8-a0a1-1821f196e66c",  # Opportunity
        "4e48c863-861b-475a-aa5e-97a4ed26f294",  # Saledata.Account
        "828b785a-8f57-4a03-9f90-e0edf96560d7",  # Contact
        "b9650500-aba7-44e3-b6e0-2542622702a3",  # Quotation
        "3407d35d-27ce-407e-8260-264574a216e3",  # Payment Term
        "f57b9e92-cb01-42e3-b7fe-6166ecd18e9c",  # Promotion
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
                "3407d35d-27ce-407e-8260-264574a216e3": {"view": "==", },
                "f57b9e92-cb01-42e3-b7fe-6166ecd18e9c": {"view": "==", },
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
                "3407d35d-27ce-407e-8260-264574a216e3": {"view": "==", },
                "f57b9e92-cb01-42e3-b7fe-6166ecd18e9c": {"view": "==", },
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
    "allow_print": True,
    "allow_permit": True,
    "allow_process": True,
    "allow_opportunity": True,
    "allow_recurrence": True,
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

FINANCIAL_RECON_APP_CONFIG = {
    "id": "b690b9ff-670a-474b-8ae2-2c17d7c30f40",
    "title": "Reconciliation",
    "code": "reconciliation",
    "model_code": "reconciliation",
    "app_label": "reconciliation",
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

PARTNERCENTER_LISTS_APP_CONFIG = {
    "id": "488a6284-6341-4c51-b837-fb6964e51d82",
    "title": "PartnerCenter/ Lists",
    "code": "list",
    "model_code": "list",
    "app_label": "partnercenter",
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
    "allow_permit": True,
    "allow_print": True,
}

FIXED_ASSET_APP_CONFIG = {
    "id": "fc552ebb-eb98-4d7b-81cd-e4b5813b7815",
    "title": "Fixed Asset",
    "code": "fixedasset",
    "model_code": "fixedasset",
    "app_label": "asset",
    "is_workflow": True,
    "app_depend_on": [],
    "permit_mapping": {
        "view": {
            "range": ["1", "4"],
            "app_depends_on": {},
            "local_depends_on": {},
        },
        "create": {
            "range": ["1", "4"],
            "app_depends_on": {},
            "local_depends_on": {
                "view": "==",
            },
        },
        "edit": {
            "range": ["1", "4"],
            "app_depends_on": {},
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
    "allow_permit": True,
}

INSTRUMENT_TOOL_APP_CONFIG = {
    "id": "2952f630-30e9-4a6a-a108-fb1dc4b9cdb1",
    "title": "Instrument & Tool",
    "code": "instrumenttool",
    "model_code": "instrumenttool",
    "app_label": "asset",
    "is_workflow": True,
    "app_depend_on": [],
    "permit_mapping": {
        "view": {
            "range": ["1", "4"],
            "app_depends_on": {},
            "local_depends_on": {},
        },
        "create": {
            "range": ["1", "4"],
            "app_depends_on": {},
            "local_depends_on": {
                "view": "==",
            },
        },
        "edit": {
            "range": ["1", "4"],
            "app_depends_on": {},
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
    "allow_permit": True,
}

GOODS_RECOVERY_APP_CONFIG = {
    "id": "a196c182-01d4-4450-a4ef-86c16b536daa",
    "title": "Goods Recovery",
    "code": "goodsrecovery",
    "model_code": "goodsrecovery",
    "app_label": "inventory",
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
}

FIXED_ASSET_WRITEOFF_APP_CONFIG = {
    "id": "bf724e39-fdd0-45ab-a343-d19c9c559e28",
    "title": "Fixed Asset Write-off",
    "code": "fixedassetwriteoff",
    "model_code": "fixedassetwriteoff",
    "app_label": "asset",
    "is_workflow": True,
    "app_depend_on": [],
    "permit_mapping": {
        "view": {
            "range": ["1", "4"],
            "app_depends_on": {},
            "local_depends_on": {},
        },
        "create": {
            "range": ["1", "4"],
            "app_depends_on": {},
            "local_depends_on": {
                "view": "==",
            },
        },
        "edit": {
            "range": ["1", "4"],
            "app_depends_on": {},
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
    "allow_permit": True,
}

INSTRUMENT_TOOL_WRITEOFF_APP_CONFIG = {
    "id": "5db2cba4-564f-4386-8b89-86e2457d60e0",
    "title": "Instrument Tool Write-off",
    "code": "instrumenttoolwriteoff",
    "model_code": "instrumenttoolwriteoff",
    "app_label": "asset",
    "is_workflow": True,
    "app_depend_on": [],
    "permit_mapping": {
        "view": {
            "range": ["1", "4"],
            "app_depends_on": {},
            "local_depends_on": {},
        },
        "create": {
            "range": ["1", "4"],
            "app_depends_on": {},
            "local_depends_on": {
                "view": "==",
            },
        },
        "edit": {
            "range": ["1", "4"],
            "app_depends_on": {},
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
    "allow_permit": True,
}

GROUP_ORDER_APP_CONFIG = {
    "id": "14662696-261f-4878-8765-56f17d738b66",
    "title": "Group Order",
    "code": "grouporder",
    "model_code": "grouporder",
    "app_label": "grouporder",
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
    "allow_permit": True,
    "allow_opportunity": True,
}

PRODUCT_MODIFICATION_APP_CONFIG = {
    "id": "f491fdf3-1384-4a82-b155-12ef6673c901",
    "title": "Product Modification",
    "code": "productmodification",
    "model_code": "productmodification",
    "app_label": "productmodification",
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

PRODUCT_MODIFICATION_BOM_APP_CONFIG = {
    "id": "b1d60043-ba66-4a52-8080-172b110cdd35",
    "title": "Product Modification BOM",
    "code": "productmodificationbom",
    "model_code": "productmodificationbom",
    "app_label": "productmodificationbom",
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

EQUIPMENT_LOAN_APP_CONFIG = {
    "id": "3fc09568-e3ff-4fd3-a70d-4d069ac1521d",
    "title": "Equipment Loan",
    "code": "equipmentloan",
    "model_code": "equipmentloan",
    "app_label": "equipmentloan",
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

REPORT_LEASE_APP_CONFIG = {
    "id": "e02cd98d-79a4-4462-8c1a-cf14fe8f7062",
    "title": "Lease Report",
    "code": "reportlease",
    "model_code": "reportlease",
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
    "allow_permit": True,
}

EQUIPMENT_RETURN_APP_CONFIG = {
    "id": "f5954e02-6ad1-4ebf-a4f2-0b598820f5f0",
    "title": "Equipment Return",
    "code": "equipmentreturn",
    "model_code": "equipmentreturn",
    "app_label": "equipmentreturn",
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

PAYMENT_PLAN_APP_CONFIG = {
    "id": "0a788054-1d79-4dfd-9371-8bc6a23971f3",
    "title": "Payment Plan",
    "code": "paymentplan",
    "model_code": "paymentplan",
    "app_label": "paymentplan",
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
    "allow_permit": True,
}

SERVICEORDER_APP_CONFIG = {
    "id": "36f25733-a6e7-43ea-b710-38e2052f0f6d",
    "title": "Service Order",
    "code": "serviceorder",
    "model_code": "serviceorder",
    "app_label": "serviceorder",
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
    "allow_permit": True,
}

SERVICEQUOTATION_APP_CONFIG = {
    "id": "c9e131ec-760c-45af-8ae6-5349f2bb542e",
    "title": "Service Quotation",
    "code": "servicequotation",
    "model_code": "servicequotation",
    "app_label": "servicequotation",
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
    # another
    'd3903adb-61a9-4b18-90ed-542ce7acedc8': ApplicationConfigFrame(**SALUTATION_APP_CONFIG).data(),
    '1102a36d-5dbe-48f6-845e-a6e0e69e04b2': ApplicationConfigFrame(**CURRENCY_APP_CONFIG).data(),
    '35b38745-ba92-4d97-b1f7-4675a46585d3': ApplicationConfigFrame(**ACCOUNT_GROUP_APP_CONFIG).data(),
    'b22a58d3-cc9e-4913-a06d-beee11afba60': ApplicationConfigFrame(**ACCOUNT_TYPE_APP_CONFIG).data(),
    '37eb1961-8103-46c5-ad2e-236f3a6585f5': ApplicationConfigFrame(**INDUSTRY_APP_CONFIG).data(),
    'eb5c547f-3a68-4113-8aa3-a1f938c9d3a7': ApplicationConfigFrame(**UOM_GROUP_APP_CONFIG).data(),
    '90f07280-e2f4-4406-aa23-ba255a22ec2d': ApplicationConfigFrame(**PRODUCT_TYPE_APP_CONFIG).data(),
    '053c0804-162a-4357-a1c2-2161e6606cc2': ApplicationConfigFrame(**PRODUCT_CATEGORY_APP_CONFIG).data(),
    'd6e7d038-aef7-4e4e-befd-b13895974ec5': ApplicationConfigFrame(**PRODUCT_MANUFACTURER_APP_CONFIG).data(),
    '7bc78f47-66f1-4104-a6fa-5ca07f3f2275': ApplicationConfigFrame(**UOM_APP_CONFIG).data(),
    '133e105e-cb3f-4845-8fba-bbb2516c5de2': ApplicationConfigFrame(**TAX_CATEGORY_APP_CONFIG).data(),
    '720d14f9-e031-4ffe-acb9-3c7763c134fc': ApplicationConfigFrame(**TAX_APP_CONFIG).data(),


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
    "010404b3-bb91-4b24-9538-075f5f00ef14": ApplicationConfigFrame(**LEASEORDER_APP_CONFIG).data(
        depend_follow_main=True,
        filtering_inheritor=True,
        spacing_allow=["0", "1"],
    ),
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
    "b690b9ff-670a-474b-8ae2-2c17d7c30f40": ApplicationConfigFrame(**FINANCIAL_RECON_APP_CONFIG).data(
        depend_follow_main=True,
        filtering_inheritor=True,
        spacing_allow=["0", "1"],
    ),
    "a9bb7b64-4f3c-412d-9e08-3b713d58d31d": ApplicationConfigFrame(**ACCOUNTING_JE_APP_CONFIG).data(
        depend_follow_main=True,
        filtering_inheritor=True,
        spacing_allow=["0", "1"],
    ),

    # Nhóm 2
    "49fe2eb9-39cd-44af-b74a-f690d7b61b67": ApplicationConfigFrame(**SALE_PROJECT).data(
        depend_follow_main=True,
        filtering_inheritor=True,
        spacing_allow=["0", "1"],
    ),
    "255d9f44-905f-4bc7-8256-316a6959b683": ApplicationConfigFrame(**SALE_PROJECT_BASELINE).data(
        depend_follow_main=False,
        filtering_inheritor=True,
    ),

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
        filtering_inheritor=True,
    ),
    "a943adf4-e00d-4cae-bb3e-78cca3efb09a": ApplicationConfigFrame(**GOODS_DETAIL_APP_CONFIG).data(
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
    "c5de0a7d-bea3-4f39-922f-06a40a060aba": ApplicationConfigFrame(**INVENTORY_ADJUSTMENT_APP_CONFIG).data(
        depend_follow_main=False,
        filtering_inheritor=False,
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
    "710c5a94-3a29-4e0e-973c-e6cace96c1e7": ApplicationConfigFrame(**FINAL_ACCEPTANCE_APP_CONFIG).data(
        depend_follow_main=False,
        filtering_inheritor=True,
    ),
    "e696a636-0f36-4b20-970d-70035d6e1e37": ApplicationConfigFrame(**REPORT_PURCHASING_APP_CONFIG).data(
        depend_follow_main=False,
        filtering_inheritor=True,
    ),
    "c04b2295-307f-49ed-80ab-1ca7f2b32d00": ApplicationConfigFrame(**LEAD_APP_CONFIG).data(
        depend_follow_main=False,
        filtering_inheritor=True,
    ),
    "ac21e8e4-fe32-41f4-9887-ee077677735c": ApplicationConfigFrame(**BUDGET_PLAN_APP_CONFIG).data(
        depend_follow_main=False,
        filtering_inheritor=True,
    ),
    "b9fa8d62-4387-4fa5-9be3-d76d77614687": ApplicationConfigFrame(**REPORT_BUDGET_APP_CONFIG).data(
        depend_follow_main=False,
        filtering_inheritor=True,
    ),
    "20ad27de-ea68-48a9-82bf-8833d7ab6da7": ApplicationConfigFrame(**REGISTRATION_APP_CONFIG).data(
        depend_follow_main=False,
        filtering_inheritor=True,
    ),
    "57a32d5a-3580-43b7-bf31-953a1afc68f4": ApplicationConfigFrame(**DISTRIBUTION_PLAN_CONFIG).data(
        depend_follow_main=False,
        filtering_inheritor=True,
    ),
    "58385bcf-f06c-474e-a372-cadc8ea30ecc": ApplicationConfigFrame(**CONTRACT_APPROVAL_APP_CONFIG).data(
        depend_follow_main=False,
        filtering_inheritor=True,
    ),
    "2de9fb91-4fb9-48c8-b54e-c03bd12f952b": ApplicationConfigFrame(**BOM_APP_CONFIG).data(
        depend_follow_main=False,
        filtering_inheritor=True,
    ),
    "a4a99ba0-5596-4ff8-8bd9-68414b5af579": ApplicationConfigFrame(**PRODUCTION_ORDER_APP_CONFIG).data(
        depend_follow_main=False,
        filtering_inheritor=True,
    ),
    "b698df99-3e8e-4183-ba5d-0eb55aeba1b2": ApplicationConfigFrame(**WORK_ORDER_APP_CONFIG).data(
        depend_follow_main=False,
        filtering_inheritor=True,
    ),
    "ad1e1c4e-2a7e-4b98-977f-88d069554657": ApplicationConfigFrame(**BIDDING_APP_CONFIG).data(
        depend_follow_main=False,
        filtering_inheritor=True,
    ),
    "3a369ba5-82a0-4c4d-a447-3794b67d1d02": ApplicationConfigFrame(**CONSULTING_APP_CONFIG).data(
        depend_follow_main=False,
        filtering_inheritor=True,
    ),
    "488a6284-6341-4c51-b837-fb6964e51d82": ApplicationConfigFrame(**PARTNERCENTER_LISTS_APP_CONFIG).data(
        depend_follow_main=False,
        filtering_inheritor=True,
    ),
    "fc552ebb-eb98-4d7b-81cd-e4b5813b7815": ApplicationConfigFrame(**FIXED_ASSET_APP_CONFIG).data(
        depend_follow_main=False,
        filtering_inheritor=True,
    ),
    "2952f630-30e9-4a6a-a108-fb1dc4b9cdb1": ApplicationConfigFrame(**INSTRUMENT_TOOL_APP_CONFIG).data(
        depend_follow_main=False,
        filtering_inheritor=True,
    ),
    "a196c182-01d4-4450-a4ef-86c16b536daa": ApplicationConfigFrame(**GOODS_RECOVERY_APP_CONFIG).data(
        depend_follow_main=False,
        filtering_inheritor=True,
    ),
    "bf724e39-fdd0-45ab-a343-d19c9c559e28": ApplicationConfigFrame(**FIXED_ASSET_WRITEOFF_APP_CONFIG).data(
        depend_follow_main=False,
        filtering_inheritor=True,
    ),
    "5db2cba4-564f-4386-8b89-86e2457d60e0": ApplicationConfigFrame(**INSTRUMENT_TOOL_WRITEOFF_APP_CONFIG).data(
        depend_follow_main=False,
        filtering_inheritor=True,
    ),
    "14662696-261f-4878-8765-56f17d738b66": ApplicationConfigFrame(**GROUP_ORDER_APP_CONFIG).data(
        depend_follow_main=False,
        filtering_inheritor=True,
    ),
    "f491fdf3-1384-4a82-b155-12ef6673c901": ApplicationConfigFrame(**PRODUCT_MODIFICATION_APP_CONFIG).data(
        depend_follow_main=False,
        filtering_inheritor=True,
    ),
    "b1d60043-ba66-4a52-8080-172b110cdd35": ApplicationConfigFrame(**PRODUCT_MODIFICATION_BOM_APP_CONFIG).data(
        depend_follow_main=False,
        filtering_inheritor=True,
    ),
    "3fc09568-e3ff-4fd3-a70d-4d069ac1521d": ApplicationConfigFrame(**EQUIPMENT_LOAN_APP_CONFIG).data(
        depend_follow_main=False,
        filtering_inheritor=True,
    ),
    "e02cd98d-79a4-4462-8c1a-cf14fe8f7062": ApplicationConfigFrame(**REPORT_LEASE_APP_CONFIG).data(
        depend_follow_main=False,
        filtering_inheritor=True,
    ),
    "f5954e02-6ad1-4ebf-a4f2-0b598820f5f0": ApplicationConfigFrame(**EQUIPMENT_RETURN_APP_CONFIG).data(
        depend_follow_main=False,
        filtering_inheritor=True,
    ),
    "0a788054-1d79-4dfd-9371-8bc6a23971f3": ApplicationConfigFrame(**PAYMENT_PLAN_APP_CONFIG).data(
        depend_follow_main=False,
        filtering_inheritor=True,
    ),
    "36f25733-a6e7-43ea-b710-38e2052f0f6d": ApplicationConfigFrame(**SERVICEORDER_APP_CONFIG).data(
        depend_follow_main=False,
        filtering_inheritor=True,
    ),
    "c9e131ec-760c-45af-8ae6-5349f2bb542e": ApplicationConfigFrame(**SERVICEQUOTATION_APP_CONFIG).data(
        depend_follow_main=False,
        filtering_inheritor=True,
    ),
}

