from apps.core.account.models import User
from apps.core.company.models import CompanyUserEmployee, Company, CompanyLicenseTracking
from apps.core.hr.models import PlanEmployee, Employee
from apps.core.tenant.models import TenantPlan, Tenant


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


def mapping_user_to_company_user_employee():
    user_list = User.objects.filter(
        tenant_current_id="c4c3a81a-3bc4-4ae3-ad10-f010f1d2bdac"
    )
    if user_list:
        for user in user_list:
            if not CompanyUserEmployee.object_normal.filter(user_id=user.id).exists():
                CompanyUserEmployee.object_normal.create(
                    user_id=user.id,
                    company_id=user.company_current_id
                )

    print('update done.')
    return True


def update_data_company_license_tracking():
    plan_employee = PlanEmployee.object_normal.all()
    if plan_employee:
        plan_employee.delete()
    tenant_list = Tenant.objects.all()
    if tenant_list:
        for tenant in tenant_list:
            tenant_plan_list = TenantPlan.object_normal.filter(tenant=tenant)
            tenant_company_list = Company.objects.filter(tenant=tenant)
            if tenant_company_list:
                for company in tenant_company_list:
                    bulk_info = []
                    for tenant_plan in tenant_plan_list:
                        bulk_info.append(CompanyLicenseTracking(**{
                            'company_id': company.id,
                            'license_plan': tenant_plan.plan.code,
                            'license_use_count': 0
                        }))
                    if bulk_info:
                        CompanyLicenseTracking.object_normal.bulk_create(bulk_info)

    print('update done.')
    return True





