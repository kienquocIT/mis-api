__all__ = ["ApplicationProperty_data"]

AppProp_SaleData_Contact_data = {
    # 828b785a-8f57-4a03-9f90-e0edf96560d7 # SaleData.Contact
    "1732206e-c2f4-42bf-98c2-9cc3d5294de6": {
        "application_id": "828b785a-8f57-4a03-9f90-e0edf96560d7",
        "title": "Owner",
        "code": "owner",
        "type": 5,
        "content_type": "hr_Employee",
    },
    "3e9235f9-e7d0-4b9c-87ce-ad3e66aa41c2": {
        "application_id": "828b785a-8f57-4a03-9f90-e0edf96560d7",
        "title": "Job Title",
        "code": "job_title",
        "type": 1,
    },
    "1fea72e9-542b-48d3-adb1-5516b931160f": {
        "application_id": "828b785a-8f57-4a03-9f90-e0edf96560d7",
        "title": "Biography",
        "code": "biography",
        "type": 1,
    },
    "e0f5900c-0723-4f75-b614-18e4b5b060f3": {
        "application_id": "828b785a-8f57-4a03-9f90-e0edf96560d7",
        "title": "Avatar",
        "code": "avatar",
        "type": 1,
    },
    "e762cb70-d7d9-4500-88c8-0144f35576c6": {
        "application_id": "828b785a-8f57-4a03-9f90-e0edf96560d7",
        "title": "Fullname",
        "code": "fullname",
        "type": 1,
    },
    "938f4ae5-9bcf-40c2-97bb-fc949b55e700": {
        "application_id": "828b785a-8f57-4a03-9f90-e0edf96560d7",
        "title": "Salutation",
        "code": "salutation",
        "type": 5,
        "content_type": "saledata_Salutation",
    },
    "33dd2595-9974-4c21-bba0-374eb31decdc": {
        "application_id": "828b785a-8f57-4a03-9f90-e0edf96560d7",
        "title": "Phone",
        "code": "phone",
        "type": 1,
    },
    "7f3fe89f-8168-47f9-8a88-ee344012d220": {
        "application_id": "828b785a-8f57-4a03-9f90-e0edf96560d7",
        "title": "Mobile",
        "code": "mobile",
        "type": 1,
    },
    "3dfdbdf3-4abc-4955-bef5-e2ba543887d1": {
        "application_id": "828b785a-8f57-4a03-9f90-e0edf96560d7",
        "title": "Email",
        "code": "email",
        "type": 1,
    },
    "6b2c8c9c-d640-4c4b-9933-e5810c8b8889": {
        "application_id": "828b785a-8f57-4a03-9f90-e0edf96560d7",
        "title": "Report To",
        "code": "report_to",
        "type": 5,
        "content_type": "saledata_Contact",
    },
    "7744b2e9-b5e3-459e-85ad-5145f0b0e775": {
        "application_id": "828b785a-8f57-4a03-9f90-e0edf96560d7",
        "title": "Address Information",
        "code": "address_information",
        "type": 1,
    },
    "e35b22d1-e5a4-4d75-a5b3-e152aa32026d": {
        "application_id": "828b785a-8f57-4a03-9f90-e0edf96560d7",
        "title": "Additional Information",
        "code": "additional_information",
        "type": 1,
    },
    "a6a64634-2cf7-41f8-a6fd-3f8f2fae77d2": {
        "application_id": "828b785a-8f57-4a03-9f90-e0edf96560d7",
        "title": "Account Name",
        "code": "account_name",
        "type": 5,
        "content_type": "saledata.Account",
    },
}

AppProp_SaleData_Account_data = {
    # 4e48c863-861b-475a-aa5e-97a4ed26f294 # SaleData.Account
    "6609da8f-66d0-4d90-ba20-711ef6e8e49e": {
        "application_id": "4e48c863-861b-475a-aa5e-97a4ed26f294",
        "title": "Name",
        "code": "title",
        "type": 1,
    },
}

ApplicationProperty_data = {
    **AppProp_SaleData_Contact_data,
    **AppProp_SaleData_Account_data,
}
