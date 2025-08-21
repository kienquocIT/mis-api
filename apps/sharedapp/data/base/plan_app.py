from .plan_app_sub.base import Application_base_data as _Application_base_data
from .plan_app_sub.crm import Application_crm_data as _Application_crm_data
from .plan_app_sub.eoffice import Application_eOffice_data as _Application_eOffice_data
from .plan_app_sub.hrm import Application_hrm_data as _Application_hrm_data
from .plan_app_sub.kms import Application_kms_data as _Application_kms_data

__all__ = [
    "SubscriptionPlan_data",
    "Application_data",
    "PlanApplication_data",
    "FULL_PLAN_ID",
    "check_app_depends_and_mapping",
    "FullPermitHandle",
]

SubscriptionPlan_data = {
    "e42e93b6-5a7d-4d75-b6da-b288045058df": {
        "title": "Base",
        "code": "base",
    },
    "395eb68e-266f-45b9-b667-bd2086325522": {
        "title": "HRM",
        "code": "hrm",
    },
    "4e082324-45e2-4c27-a5aa-e16a758d5627": {
        "title": "Sale",
        "code": "sale",
    },
    "a8ca704a-11b7-4ef5-abd7-f41d05f9d9c8": {
        "title": "E-Office",
        "code": "e-office",
    },
    "a939c80b-6cb6-422c-bd42-34e0adf91802": {
        "title": "Personal",
        "code": "personal",
    },
    "02793f68-3548-45c1-98f5-89899a963091": {
        "title": "KMS",
        "code": "kms",
    },
}

Application_data = {
    **_Application_base_data,
    **_Application_crm_data,
    **_Application_eOffice_data,
    **_Application_hrm_data,
    **_Application_kms_data,
}

_PlanApplication_base_data = {
    "ba2ef9f1-63f4-4cfb-ae2f-9dee6a56da68": {
        "plan_id": "e42e93b6-5a7d-4d75-b6da-b288045058df",  # Base
        "application_id": "ba2ef9f1-63f4-4cfb-ae2f-9dee6a56da68",  # Base
    },
    "269f4421-04d8-4528-bc95-148ffd807235": {
        "plan_id": "e42e93b6-5a7d-4d75-b6da-b288045058df",  # Base
        "application_id": "269f4421-04d8-4528-bc95-148ffd807235",  # Company
    },
    "af9c6fd3-1815-4d5a-aa24-fca9d095cb7a": {
        "plan_id": "e42e93b6-5a7d-4d75-b6da-b288045058df",  # Base
        "application_id": "af9c6fd3-1815-4d5a-aa24-fca9d095cb7a",  # User
    },
    "50348927-2c4f-4023-b638-445469c66953": {
        "plan_id": "e42e93b6-5a7d-4d75-b6da-b288045058df",  # Base
        "application_id": "50348927-2c4f-4023-b638-445469c66953",  # Employee
    },
    "4cdaabcc-09ae-4c13-bb4e-c606eb335b11": {
        "plan_id": "e42e93b6-5a7d-4d75-b6da-b288045058df",  # Base
        "application_id": "4cdaabcc-09ae-4c13-bb4e-c606eb335b11",  # Role
    },
    "e17b9123-8002-4c9b-921b-7722c3c9e3a5": {
        "plan_id": "e42e93b6-5a7d-4d75-b6da-b288045058df",  # Base
        "application_id": "e17b9123-8002-4c9b-921b-7722c3c9e3a5",  # Group
    },
    "d05237c5-0488-40aa-9384-b214412852bf": {
        "plan_id": "e42e93b6-5a7d-4d75-b6da-b288045058df",  # Base
        "application_id": "d05237c5-0488-40aa-9384-b214412852bf",  # Group Level
    },
    "71393401-e6e7-4a00-b481-6097154efa64": {
        "plan_id": "e42e93b6-5a7d-4d75-b6da-b288045058df",  # Base
        "application_id": "71393401-e6e7-4a00-b481-6097154efa64",  # Workflow
    },
}

_PlanApplication_hrm_data = {
    "7436c857-ad09-4213-a190-c1c7472e99be": {
        "plan_id": "395eb68e-266f-45b9-b667-bd2086325522",  # HRM
        "application_id": "7436c857-ad09-4213-a190-c1c7472e99be",  # Employee info
    },
    "8308d062-b22c-4f05-b88e-1115f9fe03ee": {
        "plan_id": "395eb68e-266f-45b9-b667-bd2086325522",  # HRM
        "application_id": "8308d062-b22c-4f05-b88e-1115f9fe03ee",  # Absence explanation
    },
}

_PlanApplication_sale_data = {
    "35b38745-ba92-4d97-b1f7-4675a46585d3": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "35b38745-ba92-4d97-b1f7-4675a46585d3",  # Account Group
    },
    "b22a58d3-cc9e-4913-a06d-beee11afba60": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "b22a58d3-cc9e-4913-a06d-beee11afba60",  # Account Type
    },
    "37eb1961-8103-46c5-ad2e-236f3a6585f5": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "37eb1961-8103-46c5-ad2e-236f3a6585f5",  # Industry
    },
    "1102a36d-5dbe-48f6-845e-a6e0e69e04b2": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "1102a36d-5dbe-48f6-845e-a6e0e69e04b2",  # Currency
    },
    "d3903adb-61a9-4b18-90ed-542ce7acedc8": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "d3903adb-61a9-4b18-90ed-542ce7acedc8",  # Salutation
    },
    "828b785a-8f57-4a03-9f90-e0edf96560d7": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "828b785a-8f57-4a03-9f90-e0edf96560d7",  # Contact
    },
    "4e48c863-861b-475a-aa5e-97a4ed26f294": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "4e48c863-861b-475a-aa5e-97a4ed26f294",  # Account
    },
    "eb5c547f-3a68-4113-8aa3-a1f938c9d3a7": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "eb5c547f-3a68-4113-8aa3-a1f938c9d3a7",  # UOM group
    },
    "90f07280-e2f4-4406-aa23-ba255a22ec2d": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "90f07280-e2f4-4406-aa23-ba255a22ec2d",  # Product type
    },
    "053c0804-162a-4357-a1c2-2161e6606cc2": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "053c0804-162a-4357-a1c2-2161e6606cc2",  # Product category
    },
    "d6e7d038-aef7-4e4e-befd-b13895974ec5": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "d6e7d038-aef7-4e4e-befd-b13895974ec5",  # Manufacturer
    },
    "7bc78f47-66f1-4104-a6fa-5ca07f3f2275":{
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "7bc78f47-66f1-4104-a6fa-5ca07f3f2275",  # UOM
    },
    "720d14f9-e031-4ffe-acb9-3c7763c134fc":{
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "720d14f9-e031-4ffe-acb9-3c7763c134fc",  # Tax
    },
    "133e105e-cb3f-4845-8fba-bbb2516c5de2":{
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "133e105e-cb3f-4845-8fba-bbb2516c5de2",  # Tax category
    },
    "296a1410-8d72-46a8-a0a1-1821f196e66c": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "296a1410-8d72-46a8-a0a1-1821f196e66c",  # Opportunity
    },
    "b9650500-aba7-44e3-b6e0-2542622702a3": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "b9650500-aba7-44e3-b6e0-2542622702a3",  # Quotation
    },
    "a870e392-9ad2-4fe2-9baa-298a38691cf2": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "a870e392-9ad2-4fe2-9baa-298a38691cf2",  # Sale Order
    },
    "a8badb2e-54ff-4654-b3fd-0d2d3c777538": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "a8badb2e-54ff-4654-b3fd-0d2d3c777538",  # Product
    },
    "022375ce-c99c-4f11-8841-0a26c85f2fc2": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "022375ce-c99c-4f11-8841-0a26c85f2fc2",  # Expenses
    },
    "80b8cd4f-cfba-4f33-9642-a4dd6ee31efd": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "80b8cd4f-cfba-4f33-9642-a4dd6ee31efd",  # WareHouse
    },
    "3d8ad524-5dd9-4a8b-a7cd-a9a371315a2a": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "3d8ad524-5dd9-4a8b-a7cd-a9a371315a2a",  # Picking
    },
    "1373e903-909c-4b77-9957-8bcf97e8d6d3": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "1373e903-909c-4b77-9957-8bcf97e8d6d3",  # Delivery
    },
    "10a5e913-fa51-4127-a632-a8347a55c4bb": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "10a5e913-fa51-4127-a632-a8347a55c4bb",  # Prices
    },
    "e6a00a1a-d4f9-41b7-b0de-bb1efbe8446a": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "e6a00a1a-d4f9-41b7-b0de-bb1efbe8446a",  # Shipping
    },
    "f57b9e92-cb01-42e3-b7fe-6166ecd18e9c": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "f57b9e92-cb01-42e3-b7fe-6166ecd18e9c",  # Promotion
    },
    "57725469-8b04-428a-a4b0-578091d0e4f5": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "57725469-8b04-428a-a4b0-578091d0e4f5",  # Advance Payment
    },
    "1010563f-7c94-42f9-ba99-63d5d26a1aca": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "1010563f-7c94-42f9-ba99-63d5d26a1aca",  # Payment
    },
    "3407d35d-27ce-407e-8260-264574a216e3": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "3407d35d-27ce-407e-8260-264574a216e3",  # Payment Term
    },
    "65d36757-557e-4534-87ea-5579709457d7": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "65d36757-557e-4534-87ea-5579709457d7",  # Return Advance
    },
    "e66cfb5a-b3ce-4694-a4da-47618f53de4c": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "e66cfb5a-b3ce-4694-a4da-47618f53de4c",  # Task
    },
    "319356b4-f16c-4ba4-bdcb-e1b0c2a2c124": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "319356b4-f16c-4ba4-bdcb-e1b0c2a2c124",  # Document For Customer
    },
    "14dbc606-1453-4023-a2cf-35b1cd9e3efd": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "14dbc606-1453-4023-a2cf-35b1cd9e3efd",  # Call Log
    },
    "dec012bf-b931-48ba-a746-38b7fd7ca73b": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "dec012bf-b931-48ba-a746-38b7fd7ca73b",  # Email Log
    },
    "2fe959e3-9628-4f47-96a1-a2ef03e867e3": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "2fe959e3-9628-4f47-96a1-a2ef03e867e3",  # Meting Log
    },
    # "31c9c5b0-717d-4134-b3d0-cc4ca174b168": {
    #     "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
    #     "application_id": "31c9c5b0-717d-4134-b3d0-cc4ca174b168",  # Contract
    # },
    "d78bd5f3-8a8d-48a3-ad62-b50d576ce173": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "d78bd5f3-8a8d-48a3-ad62-b50d576ce173",  # Purchase Quotation Request
    },
    "f52a966a-2eb2-4851-852d-eff61efeb896": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "f52a966a-2eb2-4851-852d-eff61efeb896",  # Purchase Quotation
    },
    "81a111ef-9c32-4cbd-8601-a3cce884badb": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "81a111ef-9c32-4cbd-8601-a3cce884badb",  # Purchase Order
    },
    "fbff9b3f-f7c9-414f-9959-96d3ec2fb8bf": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "fbff9b3f-f7c9-414f-9959-96d3ec2fb8bf",  # Purchase Request
    },
    "245e9f47-df59-4d4a-b355-7eff2859247f": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "245e9f47-df59-4d4a-b355-7eff2859247f",  # Expense Item
    },
    "dd16a86c-4aef-46ec-9302-19f30b101cf5": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "dd16a86c-4aef-46ec-9302-19f30b101cf5",  # Goods Receipt
    },
    "a943adf4-e00d-4cae-bb3e-78cca3efb09a": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "a943adf4-e00d-4cae-bb3e-78cca3efb09a",  # Goods Detail
    },
    "866f163d-b724-404d-942f-4bc44dc2e2ed": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "866f163d-b724-404d-942f-4bc44dc2e2ed",  # Goods Transfer
    },
    "f26d7ce4-e990-420a-8ec6-2dc307467f2c": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "f26d7ce4-e990-420a-8ec6-2dc307467f2c",  # Goods Issue
    },
    "c5de0a7d-bea3-4f39-922f-06a40a060aba": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "c5de0a7d-bea3-4f39-922f-06a40a060aba",  # Inventory Adjustment
    },
    "c3260940-21ff-4929-94fe-43bc4199d38b": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "c3260940-21ff-4929-94fe-43bc4199d38b",  # Report Revenue
    },
    "2a709d75-35a7-49c8-84bf-c350164405bc": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "2a709d75-35a7-49c8-84bf-c350164405bc",  # Report Product
    },
    "d633036a-8937-4f9d-a227-420e061496fc": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "d633036a-8937-4f9d-a227-420e061496fc",  # Report Customer
    },
    "298c8b6f-6a62-493f-b0ac-d549a4541497": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "298c8b6f-6a62-493f-b0ac-d549a4541497",  # Report Pipeline
    },
    "e4ae0a2c-2130-4a65-b644-1b79db3d033b": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "e4ae0a2c-2130-4a65-b644-1b79db3d033b",  # Revenue Plan
    },
    "1d7291dd-1e59-4917-83a3-1cc07cfc4638": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "1d7291dd-1e59-4917-83a3-1cc07cfc4638",  # AR Invoice
    },
    "c05a6cf4-efff-47e0-afcf-072017b8141a": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "c05a6cf4-efff-47e0-afcf-072017b8141a",  # AP Invoice
    },
    "0242ba77-8b02-4589-8ed9-239788083f2b": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "0242ba77-8b02-4589-8ed9-239788083f2b",  # Goods return
    },
    "69e84b95-b347-4f49-abdf-0ec80d6eb5bd": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "69e84b95-b347-4f49-abdf-0ec80d6eb5bd",  # Report Cashflow
    },
    "c22a9e96-e56e-4636-9083-8ee1c66cb1b2": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "c22a9e96-e56e-4636-9083-8ee1c66cb1b2",  # Report Inventory
    },
    "710c5a94-3a29-4e0e-973c-e6cace96c1e7": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "710c5a94-3a29-4e0e-973c-e6cace96c1e7",  # Final Acceptance
    },
    "e696a636-0f36-4b20-970d-70035d6e1e37": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "e696a636-0f36-4b20-970d-70035d6e1e37",  # Report Purchasing
    },
    "c04b2295-307f-49ed-80ab-1ca7f2b32d00": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "c04b2295-307f-49ed-80ab-1ca7f2b32d00",  # Lead
    },
    "49fe2eb9-39cd-44af-b74a-f690d7b61b67": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale
        "application_id": "49fe2eb9-39cd-44af-b74a-f690d7b61b67",  # Projects
    },
    "255d9f44-905f-4bc7-8256-316a6959b683": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale
        "application_id": "255d9f44-905f-4bc7-8256-316a6959b683",  # Project baseline
    },
    "ac21e8e4-fe32-41f4-9887-ee077677735c": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "ac21e8e4-fe32-41f4-9887-ee077677735c",  # Budget Plan
    },
    "b9fa8d62-4387-4fa5-9be3-d76d77614687": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "b9fa8d62-4387-4fa5-9be3-d76d77614687",  # Report Budget
    },
    "20ad27de-ea68-48a9-82bf-8833d7ab6da7": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "20ad27de-ea68-48a9-82bf-8833d7ab6da7",  # Registration
    },
    "57a32d5a-3580-43b7-bf31-953a1afc68f4": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "57a32d5a-3580-43b7-bf31-953a1afc68f4",  # Goods stock plan
    },
    "58385bcf-f06c-474e-a372-cadc8ea30ecc": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "58385bcf-f06c-474e-a372-cadc8ea30ecc",  # Contract Approval
    },
    "2de9fb91-4fb9-48c8-b54e-c03bd12f952b": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "2de9fb91-4fb9-48c8-b54e-c03bd12f952b",  # BOM
    },
    "a4a99ba0-5596-4ff8-8bd9-68414b5af579": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "a4a99ba0-5596-4ff8-8bd9-68414b5af579",  # Production Order
    },
    "b698df99-3e8e-4183-ba5d-0eb55aeba1b2": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "b698df99-3e8e-4183-ba5d-0eb55aeba1b2",  # Work Order
    },
    "ad1e1c4e-2a7e-4b98-977f-88d069554657": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "ad1e1c4e-2a7e-4b98-977f-88d069554657",  # Bidding
    },
    "3a369ba5-82a0-4c4d-a447-3794b67d1d02": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "3a369ba5-82a0-4c4d-a447-3794b67d1d02",  # Consulting
    },
    "010404b3-bb91-4b24-9538-075f5f00ef14": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "010404b3-bb91-4b24-9538-075f5f00ef14",  # Lease Order
    },
    "7ba35923-d8ff-4f6d-bf80-468a7190a63b": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "7ba35923-d8ff-4f6d-bf80-468a7190a63b",  # Cash infow
    },
    "c51857ef-513f-4dbf-babd-26d68950ad6e": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "c51857ef-513f-4dbf-babd-26d68950ad6e",  # Cash outfow
    },
    "b690b9ff-670a-474b-8ae2-2c17d7c30f40": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "b690b9ff-670a-474b-8ae2-2c17d7c30f40",  # Recon
    },
    "a9bb7b64-4f3c-412d-9e08-3b713d58d31d": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "a9bb7b64-4f3c-412d-9e08-3b713d58d31d",  # JE
    },
    "488a6284-6341-4c51-b837-fb6964e51d82": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "488a6284-6341-4c51-b837-fb6964e51d82",  # Partner Center/ Lists
    },
    "fc552ebb-eb98-4d7b-81cd-e4b5813b7815": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "fc552ebb-eb98-4d7b-81cd-e4b5813b7815",  # Fixed asset
    },
    "2952f630-30e9-4a6a-a108-fb1dc4b9cdb1": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "2952f630-30e9-4a6a-a108-fb1dc4b9cdb1",  # Instrument Tool
    },
    "a196c182-01d4-4450-a4ef-86c16b536daa": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "a196c182-01d4-4450-a4ef-86c16b536daa",  # Goods Recovery
    },
    "bf724e39-fdd0-45ab-a343-d19c9c559e28": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "bf724e39-fdd0-45ab-a343-d19c9c559e28",  # Fixed asset write off
    },
    "5db2cba4-564f-4386-8b89-86e2457d60e0": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "5db2cba4-564f-4386-8b89-86e2457d60e0",  # Instrument tool write off
    },
    "14662696-261f-4878-8765-56f17d738b66": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "14662696-261f-4878-8765-56f17d738b66",  # Group Order
    },
    "f491fdf3-1384-4a82-b155-12ef6673c901": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "f491fdf3-1384-4a82-b155-12ef6673c901",  # Product Modification
    },
    "b1d60043-ba66-4a52-8080-172b110cdd35": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "b1d60043-ba66-4a52-8080-172b110cdd35",  # Product Modification BOM
    },
    "3fc09568-e3ff-4fd3-a70d-4d069ac1521d": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "3fc09568-e3ff-4fd3-a70d-4d069ac1521d",  # Equipment Loan
    },
    "e02cd98d-79a4-4462-8c1a-cf14fe8f7062": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "e02cd98d-79a4-4462-8c1a-cf14fe8f7062",  # Report Lease
    },
    "f5954e02-6ad1-4ebf-a4f2-0b598820f5f0": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "f5954e02-6ad1-4ebf-a4f2-0b598820f5f0",  # Equipment Return
    },
    "0a788054-1d79-4dfd-9371-8bc6a23971f3": {
        "plan_id": "4e082324-45e2-4c27-a5aa-e16a758d5627",  # Sale Data
        "application_id": "0a788054-1d79-4dfd-9371-8bc6a23971f3",  # Payment Plan
    },
}

_PlanApplication_eOffice_data = {
    "baff033a-c416-47e1-89af-b6653534f06e": {
        "plan_id": "a8ca704a-11b7-4ef5-abd7-f41d05f9d9c8",  # E-office
        "application_id": "baff033a-c416-47e1-89af-b6653534f06e",  # Leave
    },
    "7738935a-0442-4fd4-a7ff-d06a22aaeccf": {
        "plan_id": "a8ca704a-11b7-4ef5-abd7-f41d05f9d9c8",  # E-office
        "application_id": "7738935a-0442-4fd4-a7ff-d06a22aaeccf",  # Leave available
    },
    "87ce1662-ca9d-403f-a32e-9553714ebc6d": {
        "plan_id": "a8ca704a-11b7-4ef5-abd7-f41d05f9d9c8",  # E-office
        "application_id": "87ce1662-ca9d-403f-a32e-9553714ebc6d",  # Business trip
    },
    "55ba3005-6ccc-4807-af27-7cc45e99e3f6": {
        "plan_id": "a8ca704a-11b7-4ef5-abd7-f41d05f9d9c8",  # E-office
        "application_id": "55ba3005-6ccc-4807-af27-7cc45e99e3f6",  # Asset, Tools provide
    },
    "6078deaa-96b3-4743-97e3-5457454fa7aa": {
        "plan_id": "a8ca704a-11b7-4ef5-abd7-f41d05f9d9c8",  # E-office
        "application_id": "6078deaa-96b3-4743-97e3-5457454fa7aa",  # Meeting Schedule
    },
    "41abd4e9-da89-450b-a44a-da1d6f8a5cd2": {
        "plan_id": "a8ca704a-11b7-4ef5-abd7-f41d05f9d9c8",  # E-office
        "application_id": "41abd4e9-da89-450b-a44a-da1d6f8a5cd2",  # Asset, Tools Delivery
    },
    "08e41084-4379-4778-9e16-c09401f0a66e": {
        "plan_id": "a8ca704a-11b7-4ef5-abd7-f41d05f9d9c8",  # E-office
        "application_id": "08e41084-4379-4778-9e16-c09401f0a66e",  # Asset, Tools Return
    },
}

_PlanApplication_kms_data = {
    "7505d5db-42fe-4cde-ae5e-dbba78e2df03": {
        "plan_id": "02793f68-3548-45c1-98f5-89899a963091",  # KMS
        "application_id": "7505d5db-42fe-4cde-ae5e-dbba78e2df03",  # Document approval
    },
    "6944d486-66a0-4521-bd28-681d5df42ff3": {
        "plan_id": "02793f68-3548-45c1-98f5-89899a963091",  # KMS
        "application_id": "6944d486-66a0-4521-bd28-681d5df42ff3",  # Document approval
    },
}

PlanApplication_data = {
    **_PlanApplication_base_data,
    **_PlanApplication_hrm_data,
    **_PlanApplication_sale_data,
    **_PlanApplication_eOffice_data,
    **_PlanApplication_kms_data,
}


class FullPermitHandle:
    @classmethod
    def parse_one_permit_allow(
            cls, app_data, plan_data, range_code,
            is_view=False, is_create=False, is_edit=False, is_delete=False,
            sub_data: list = None,
    ):
        sub_data = [] if sub_data is None else sub_data
        return {
            'id': None,
            'app_id': app_data['id'],
            'app_data': {
                'id': app_data['id'],
                'title': app_data['title'],
                'code': app_data['code'],
                'model_code': app_data['model_code'],
                'app_label': app_data['app_label'],
                'option_permission': app_data['option_permission'],
            } if 'title' in app_data else {},
            'plan_id': plan_data['id'],
            'plan_data': {
                'id': plan_data['id'], 'title': plan_data['title'], 'code': plan_data['code']
            } if 'title' in plan_data else {},
            'create': is_create,
            'view': is_view,
            'edit': is_edit,
            'delete': is_delete,
            'range': range_code,
            'sub': sub_data
        }

    @classmethod
    def parse_permit_code_to_dict(cls, data):
        if data == 'view':
            return {'is_view': True}
        if data == 'create':
            return {'is_create': True}
        if data == 'edit':
            return {'is_edit': True}
        if data == 'delete':
            return {'is_delete': True}
        return {}

    @classmethod
    def get_by_app(cls, app_data, plan_data):
        result = []
        for permit, config in app_data.get('permit_mapping', {}).items():
            permit_has_range = config.get('range', [])
            for range_code in permit_has_range:
                result.append(
                    cls.parse_one_permit_allow(
                        app_data=app_data, plan_data=plan_data, range_code=range_code,
                        **cls.parse_permit_code_to_dict(permit),
                    )
                )
        return result

    @classmethod
    def full_permit(cls):
        result = []
        for _key, value in PlanApplication_data.items():
            if _key != value['application_id']:
                raise ValueError('PlanApplication ID must be equal Application ID.')
            plan_data = {'id': value['plan_id'], **SubscriptionPlan_data[value['plan_id']]}
            app_data = {'id': value['application_id'], **Application_data[value['application_id']]}
            result += cls.get_by_app(app_data=app_data, plan_data=plan_data)
        return result


FULL_PERMISSIONS_BY_CONFIGURED = FullPermitHandle.full_permit()
FULL_PLAN_ID = SubscriptionPlan_data.keys()


class CheckingDependsOnApp:
    RANGE_ALLOWED = ['1', '2', '3', '4', '*', '==']

    @classmethod
    def make_sure_range_support(cls, range_or_range_list):
        if isinstance(range_or_range_list, list):
            for range_x in range_or_range_list:
                cls.make_sure_range_support(range_x)
        else:
            if range_or_range_list not in cls.RANGE_ALLOWED:
                raise ValueError(
                    'Range "%s" not in RANGE_ALLOWED = %s.' % (
                        str(range_or_range_list),
                        str(cls.RANGE_ALLOWED)
                    )
                )

    @classmethod
    def check_depends_on_app_correct(cls, app_depend_on):
        if app_depend_on:
            if isinstance(app_depend_on, dict):
                for app_id, permit_config in app_depend_on.items():
                    app_data = Application_data.get(app_id, None)
                    if app_data:
                        data_permit_map = app_data.get('permit_mapping', [])
                        data_permit_keys = list(set(data_permit_map.keys()))
                        for permit_key, allow_range_code in permit_config.items():
                            cls.make_sure_range_support(allow_range_code)
                            if not allow_range_code or (
                                    isinstance(allow_range_code, list) and len(allow_range_code) == 0
                            ):
                                raise ValueError(
                                    'The application ID "%s" require range for depends on apps.' % (str(app_id))
                                )

                            if permit_key not in data_permit_keys:
                                raise ValueError(
                                    'The application ID "%s" permit not in permit allow of app depended. '
                                    'DATA: "%s" not in %s.' % (
                                        str(app_id),
                                        str(permit_key),
                                        str(data_permit_keys),
                                    )
                                )
                            else:
                                range_mapped_by_key = data_permit_map[permit_key].get('range', [])
                                cls.make_sure_range_support(range_mapped_by_key)
                                if '*' not in range_mapped_by_key:
                                    if allow_range_code == '==':
                                        ...
                                    elif allow_range_code not in range_mapped_by_key:
                                        raise ValueError(
                                            'The application ID "%s" use range not allow by original apps. '
                                            'DATA: %s not in %s.' % (
                                                str(app_id),
                                                str(allow_range_code),
                                                str(range_mapped_by_key)
                                            )
                                        )
                    else:
                        raise ValueError('The application ID "%s" is not found.' % (str(app_id)))
            else:
                raise ValueError('Depends on should be match dict type. DATA: %s.' % (str(app_depend_on)))
        return True

    @classmethod
    def get_app_in_permit_mapping(cls, permit_mapping):
        app_ids = []
        if permit_mapping and isinstance(permit_mapping, dict):
            for permit, data in permit_mapping.items():
                app_depend_on = data.get('app_depends_on', {})
                app_ids += list(set(app_depend_on.keys()))
                cls.check_depends_on_app_correct(app_depend_on)
        return list(set(app_ids))

    @staticmethod
    def not_app_in_depends(depend_ids, mapping_app_ids):
        depend_ids = list(set(depend_ids))
        mapping_app_ids = list(set(mapping_app_ids))
        not_in_apps = []
        for _item_x in mapping_app_ids:
            if _item_x not in depend_ids:
                not_in_apps.append(_item_x)
        return not_in_apps


def check_app_depends_and_mapping():
    errors = []
    for _id, data in Application_data.items():
        app_depend_on = list(set(data.get('app_depend_on', [])))
        permit_mapping = data.get('permit_mapping', {})

        # check app_depend_on compare with app in permit_mapping.
        app_ids = CheckingDependsOnApp.get_app_in_permit_mapping(permit_mapping=permit_mapping)
        if len(app_depend_on) != len(app_ids):
            errors.append(
                {
                    _id: [
                        f"Apps in permit_mapping but not exist in depends on: "
                        f"{', '.join(CheckingDependsOnApp.not_app_in_depends(app_depend_on, app_ids))}",
                    ]
                }
            )

        #

    if errors:
        for err_data in errors:
            print(err_data)
        print('Some errors raise in Application depends!')
        return False
    print('All application depends is correct!')
    return True
