from apps.core.account.models import User
from apps.core.base.models import ApplicationProperty
from apps.core.company.models import CompanyUserEmployee, Company, CompanyLicenseTracking
from apps.core.hr.models import PlanEmployee
from apps.core.tenant.models import TenantPlan, Tenant
from apps.core.workflow.models import Node, Workflow, Association
from apps.shared import CONDITION_LOGIC


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


# TEST WORKFLOW
def create_initial_node():
    data = [
        Node(**{
            'id': 'abccf657-7dce-4a14-9601-f6c4c4f2722a',
            'title': 'Initial Node',
            'code': 'Initial',
            'is_system': True,
            'order': 1,
        }),
        Node(**{
            'id': '1fbb680e-3521-424a-8523-9f7a34ce867e',
            'title': 'Approved Node',
            'code': 'Approved',
            'is_system': True,
            'order': 2,
        }),
        Node(**{
            'id': '580f887c-1280-44ea-b275-8cb916543b10',
            'title': 'Completed Node',
            'code': 'Completed',
            'is_system': True,
            'order': 3,
        })
    ]
    Node.object_global.bulk_create(data)

    return True


def create_data_property():
    data = {
        'id': '582a4296-299d-4856-adf2-84c1a7be3d08',
        'application_id': '50348927-2c4f-4023-b638-445469c66953',
        'title': 'Doanh thu',
        'code': 'revenue',
        'type': 'text',
        'compare_operator': {
            '=': 'equal',
            '>': 'greater than',
            '<': 'less than',
            '>=': 'greater or equal',
            '<=': 'less or equal',
            '!=': 'not equal'
        }
    }
    ApplicationProperty.objects.create(**data)
    return True


def create_data_workflow():
    workflow_data = {
        'id': 'a86f8b07-02f3-42da-90c7-3fcefe1dae2b',
        'application_id': '50348927-2c4f-4023-b638-445469c66953',
        'title': 'workflow test',
        'code': 'test',
    }
    node_data = [
        {
            'id': '1c70776b-9722-4553-bed9-ea3a238ce072',
            'workflow_id': 'a86f8b07-02f3-42da-90c7-3fcefe1dae2b',
            'title': 'node initial',
            'is_system': True,
            'code_node_system': 'Initial'
        },
        {
            'id': 'e31ccba9-7007-4017-8076-2e7c06d5ed97',
            'workflow_id': 'a86f8b07-02f3-42da-90c7-3fcefe1dae2b',
            'title': 'node CEO Duy?t'
        },
    ]
    association_data = {
        'id': '2e02dd3b-54b8-4557-b2f6-2c6d3f496846',
        'node_in_id': '1c70776b-9722-4553-bed9-ea3a238ce072',
        'node_out_id': 'e31ccba9-7007-4017-8076-2e7c06d5ed97',
        'condition': [
            {'property': 'total_revenue', 'operator': '>', 'value': 100},
            'AND',
            {'property': 'total_revenue', 'operator': '>', 'value': 100},
            'AND',
            {'property': 'total_revenue', 'operator': '>', 'value': 100},
            'AND',
            [
                {'property': 'total_revenue', 'operator': '>', 'value': 100},
                'AND',
                {'property': 'total_revenue', 'operator': '>', 'value': 100},
                'AND',
                {'property': 'total_revenue', 'operator': '>', 'value': 100},
            ],
            'AND',
            [
                {'property': 'total_revenue', 'operator': '>', 'value': 100},
                'OR',
                {'property': 'total_revenue', 'operator': '>', 'value': 100},
                'OR',
                {'property': 'total_revenue', 'operator': '>', 'value': 100},
            ],
        ]
    }
    Workflow.objects.create(**workflow_data)
    for node in node_data:
        Node.objects.create(**node)
    Association.objects.create(**association_data)
    return True


def get_true_false(condition_data):
    tmp = True
    return tmp


def check_condition(condition_list):
    result = []
    for idx in range(0, len(condition_list)):
        if idx % 2 == 0:
            if isinstance(condition_list[idx], dict):
                result.append(get_true_false(condition_list[idx]))
            elif isinstance(condition_list[idx], list):
                result.append(check_condition(
                    condition_list=condition_list[idx],
                ))
        else:
            result.append(condition_list[idx].lower())

    return result


def get_condition_tree(condition_obj):
    """ return a tree for a condition object """

    children = condition_obj.condition_parent.all()

    if not children:
        # this condition has no children, recursion ends here
        return {'title': condition_obj.title, 'children': []}

    # this condition has children, get every child's family tree
    return {
        'title': condition_obj.title,
        'children': [get_condition_tree(child) for child in children],
    }


def get_node_condition(node_id):
    result = []
    association_list = Association.objects.filter(
        node_in_id=node_id,
    ).values('condition')
    if association_list:
        for association in association_list:
            tmp = check_condition(
                condition_list=association['condition'],
            )

    return result
