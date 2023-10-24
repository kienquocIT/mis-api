__all__ = [
    'PlanAppDistributionController',
]

from apps.shared import ListHandler

from apps.core.tenant.models import TenantPlan

from .employee import Employee, PlanEmployee, PlanEmployeeApp
from .roles import RoleHolder, PlanRole, PlanRoleApp
from .summary import DistributionPlan, DistributionApplication


class PlanAppDistributionController:
    @classmethod
    def get_plan_ids__of_employee(cls, employee_obj, role_ids):
        plan_ids = [
            str(ite) for ite in
            PlanEmployee.objects.filter(employee=employee_obj).values_list('plan_id', flat=True)
        ]
        plan_ids += [
            str(ite) for ite in
            PlanRole.objects.filter(role_id__in=role_ids).values_list('plan_id', flat=True)
        ]

        return plan_ids

    @classmethod
    def get_app_ids__of_employee(cls, employee_obj, role_ids) -> (list[str], dict[str, str]):
        app_ids = []
        plan_of_app_by_ids = {}
        for item in PlanEmployeeApp.objects.select_related('plan_employee').filter(
                plan_employee__employee=employee_obj
        ).values('application_id', 'plan_employee__plan_id'):
            app_ids.append(str(item['application_id']))
            plan_of_app_by_ids[str(item['application_id'])] = str(item['plan_employee__plan_id'])

        for item in PlanRoleApp.objects.select_related('plan_role').filter(
                plan_role__role_id__in=role_ids
        ).values('application_id', 'plan_role__plan_id'):
            app_ids.append(str(item['application_id']))
            plan_of_app_by_ids[str(item['application_id'])] = str(item['plan_role__plan_id'])

        return app_ids, plan_of_app_by_ids

    @classmethod
    def update_used_tenant_plan(cls, tenant_plan_objs, tenant_id, company_id):
        for tenant_plan_obj in tenant_plan_objs:
            plan_used = DistributionPlan.objects.filter(
                tenant_id=tenant_id, company_id=company_id,
                tenant_plan=tenant_plan_obj, is_active=True,
            ).count()
            tenant_plan_obj.license_used = plan_used
            tenant_plan_obj.save()

        return True

    def __init__(self, employee_obj):
        if isinstance(employee_obj, Employee):
            self.employee_obj = employee_obj
        else:
            raise ValueError('employee_id_or_obj must be ID of Employee or Employee Object')

        self.role_ids = [
            str(ite) for ite in RoleHolder.objects.filter(employee=self.employee_obj).values_list('role_id', flat=True)
        ]

    def sync_plan(self):
        distributed_plan_ids = [
            str(ite) for ite in
            DistributionPlan.objects.filter(employee=self.employee_obj).values_list('plan', flat=True)
        ]
        currently_plan_ids = self.get_plan_ids__of_employee(employee_obj=self.employee_obj, role_ids=self.role_ids)
        plan_ids_remove, plan_ids_keep, plan_ids_new = ListHandler.diff_two_list(
            arr_a=distributed_plan_ids, arr_b=currently_plan_ids
        )

        # destroy plan was removed
        if plan_ids_remove:
            tenant_plan_remove_recheck = []
            for obj in DistributionPlan.objects.filter(employee=self.employee_obj, plan_id__in=plan_ids_remove):
                if obj.tenant_plan:
                    tenant_plan_remove_recheck.append(obj.tenant_plan)
                else:
                    print('Skipp remove because object (DistributionPlan) not has value tenant_plan', obj.id)

                obj_dist = DistributionApplication.objects.filter(distribution_plan=obj, employee=self.employee_obj)
                if obj_dist:
                    obj_dist.delete()
                obj.delete()

            self.update_used_tenant_plan(
                tenant_plan_objs=tenant_plan_remove_recheck,
                tenant_id=self.employee_obj.tenant_id,
                company_id=self.employee_obj.company_id,
            )

        if plan_ids_keep:
            for obj in DistributionPlan.objects.filter(
                    employee=self.employee_obj, plan_id__in=plan_ids_keep, is_active=False
            ):
                obj.is_active = True
                obj.save()

        # new plan was added
        if plan_ids_new:
            tenant_plan_new_recheck = []
            bulk_create_obj = []
            for idn in plan_ids_new:
                tenant_plan_matched = TenantPlan.objects.filter(tenant=self.employee_obj.tenant, plan_id=idn).first()
                if tenant_plan_matched:
                    tenant_plan_new_recheck.append(tenant_plan_matched)
                    bulk_create_obj.append(
                        DistributionPlan(
                            tenant=self.employee_obj.tenant,
                            company=self.employee_obj.company,
                            employee=self.employee_obj,
                            plan_id=idn,
                            tenant_plan=tenant_plan_matched,
                        )
                    )
                else:
                    print('license for app was expired or not found!', idn)

            DistributionPlan.objects.bulk_create(bulk_create_obj)
            self.update_used_tenant_plan(
                tenant_plan_objs=tenant_plan_new_recheck,
                tenant_id=self.employee_obj.tenant_id,
                company_id=self.employee_obj.company_id,
            )
        return True

    def sync_app(self):
        distributed_app_ids = [
            str(ite) for ite in
            DistributionApplication.objects.filter(employee=self.employee_obj).values_list('app_id', flat=True)
        ]
        currently_app_ids, mapping_app_with_plan = self.get_app_ids__of_employee(
            employee_obj=self.employee_obj, role_ids=self.role_ids
        )
        app_ids_remove, app_ids_keep, app_ids_new = ListHandler.diff_two_list(
            arr_a=distributed_app_ids, arr_b=currently_app_ids
        )

        # destroy app was removed
        if app_ids_remove:
            objs = DistributionApplication.objects.filter(employee=self.employee_obj, app_id__in=app_ids_remove)
            if objs:
                objs.delete()

        # active keep if was inactive
        if app_ids_keep:
            for obj in DistributionApplication.objects.filter(
                    employee=self.employee_obj, app_id__in=app_ids_keep, is_active=False
            ):
                obj.is_active = True
                obj.save()

        # new app was added
        if app_ids_new:
            bulk_create_obj = []
            for idn in app_ids_new:
                plan_mapped_obj = DistributionPlan.objects.filter(
                    employee=self.employee_obj, plan_id=mapping_app_with_plan[idn], is_active=True,
                ).first()
                if plan_mapped_obj:
                    bulk_create_obj.append(
                        DistributionApplication(
                            distribution_plan=plan_mapped_obj,
                            app_id=idn,
                            tenant=self.employee_obj.tenant,
                            company=self.employee_obj.company,
                            employee=self.employee_obj,
                        )
                    )
                else:
                    print('App regis was skipped because Plan Tenant not found!', idn)
            DistributionApplication.objects.bulk_create(bulk_create_obj)

        return True

    def sync_all(self):
        self.sync_plan()
        self.sync_app()
        return True

    @classmethod
    def uninstall_all(cls, tenant_id, company_id, employee_id):
        apps = DistributionApplication.objects.filter(employee_id=employee_id)
        if apps:
            apps.delete()

        plans = DistributionPlan.objects.filter(employee_id=employee_id)
        if plans:
            plans.delete()

        used_tenant_plan = TenantPlan.objects.filter(tenant_id=tenant_id)
        if used_tenant_plan:
            cls.update_used_tenant_plan(tenant_plan_objs=used_tenant_plan, tenant_id=tenant_id, company_id=company_id)
        return True
