from apps.core.company.models import CompanyUserEmployee
from apps.core.tenant.models import TenantPlan


def update_company_created_user():
    company_user_emp = CompanyUserEmployee.object_normal.filter(user__isnull=False)
    if company_user_emp:
        for item in company_user_emp:
            item.is_created_company = True
            item.save()
    print('update done.')
    return True


def update_tenant_plan():
    data_list = [
        {
            'id': "8e83942e-1665-45d7-8c57-bdcfd84d0fc0",
            'tenant_id': "5434d55e-b2f7-4b0a-8f9c-42c4a4adae91",
            'plan_id': "395eb68e-266f-45b9-b667-bd2086325522",
            'purchase_order': "PO019",
            'is_limited': True,
            'license_quantity': 30,
            'date_active': "2023-01-30 07:16:00.000000",
            'date_end': "2024-01-30 07:16:00.000000",
        },
        {
            'id': "5e01c595-3f69-4707-b698-67a80915ecfe",
            'tenant_id': "5434d55e-b2f7-4b0a-8f9c-42c4a4adae91",
            'plan_id': "a939c80b-6cb6-422c-bd42-34e0adf91802",
            'purchase_order': "PO019",
            'is_limited': True,
            'license_quantity': 30,
            'date_active': "2023-01-30 07:16:00.000000",
            'date_end': "2024-01-30 07:16:00.000000"
        },
        {
            'id': "9fbf5b68-851c-4895-b29c-2f66b06d73b4",
            'tenant_id': "2a6de9c2-291f-439f-a750-c7c335945021",
            'plan_id': "a939c80b-6cb6-422c-bd42-34e0adf91802",
            'purchase_order': "PO021",
            'is_limited': True,
            'license_quantity': 10,
            'date_active': "2023-02-02 10:38:00.000000",
            'date_end': "2023-05-02 10:38:00.000000"
        }
    ]
    for data in data_list:
        TenantPlan.objects.create(**data)

    print('update done.')
    return True
