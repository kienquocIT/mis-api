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
            'id': "d3bd3202-d92c-427a-a4da-9b2043dc2615",
            'tenant_id': "98730aaf-efd4-403d-9da7-418fc49696e2",
            'plan_id': "4e082324-45e2-4c27-a5aa-e16a758d5627",
            'purchase_order': "PO022",
            'is_limited': False,
            'license_quantity': None,
            'date_active': "2023-02-06 07:39:00.000000",
            'date_end': "2023-08-06 07:39:00.000000",
        },
        {
            'id': "30e78436-091a-4a2a-a96e-92f2d27b64ea",
            'tenant_id': "98730aaf-efd4-403d-9da7-418fc49696e2",
            'plan_id': "a939c80b-6cb6-422c-bd42-34e0adf91802",
            'purchase_order': "PO022",
            'is_limited': False,
            'license_quantity': None,
            'date_active': "2023-02-06 07:39:00.000000",
            'date_end': "2023-08-06 07:39:00.000000",
        },
        {
            'id': "a256580d-298e-4d2b-a6dd-307a6be22b87",
            'tenant_id': "c4c3a81a-3bc4-4ae3-ad10-f010f1d2bdac",
            'plan_id': "a939c80b-6cb6-422c-bd42-34e0adf91802",
            'purchase_order': "PO023",
            'is_limited': True,
            'license_quantity': 30,
            'date_active': "2023-02-08 02:00:00.000000",
            'date_end': "2023-08-08 02:00:00.000000"
        },
        {
            'id': "76beb796-fcbb-4231-9a55-ed21b9f16d0d",
            'tenant_id': "4aa530c3-bd4b-4165-bbbb-f89735a1c66a",
            'plan_id': "395eb68e-266f-45b9-b667-bd2086325522",
            'purchase_order': "PO001",
            'is_limited': True,
            'license_quantity': 10,
            'date_active': "2023-01-13 07:44:00.000000",
            'date_end': "2023-03-13 07:44:00.000000"
        },
        {
            'id': "6d08677a-df6d-4ee2-b18c-ee5c21fdf6ab",
            'tenant_id': "9a600efe-7214-446c-9154-1dec004c8de9",
            'plan_id': "a939c80b-6cb6-422c-bd42-34e0adf91802",
            'purchase_order': "PO008",
            'is_limited': True,
            'license_quantity': 10,
            'date_active': "2023-01-16 04:16:00.000000",
            'date_end': "2023-06-16 04:16:00.000000",
            'license_buy_type': 1,
        }
    ]
    for data in data_list:
        if not TenantPlan.objects.filter(
                tenant_id=data['tenant_id'],
                plan_id=data['plan_id']
        ).exists():
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





