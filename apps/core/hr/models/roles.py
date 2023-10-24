from django.db import models

from apps.core.hr.models.private_extends import PermissionAbstractModel
from apps.core.models import TenantAbstractModel
from apps.shared import SimpleAbstractModel


class Role(TenantAbstractModel):
    abbreviation = models.CharField(
        verbose_name='abbreviation of role (Business analysis -> BA)',
        max_length=10,
        blank=True,
        null=True
    )
    employee = models.ManyToManyField(
        'hr.Employee',
        through="RoleHolder",
        symmetrical=False,
        blank=True,
        related_name='role_map_employee'
    )
    plan = models.ManyToManyField(
        'base.SubscriptionPlan',
        through="PlanRole",
        symmetrical=False,
        blank=True,
        related_name='role_map_plan',
    )

    # as sum data permissions
    permissions_parsed_sample = {
        'hr.employee.view': {
            '4': {},
            'ids': {
                '{doc_id}': {},
            },
            'opp': {
                '{opp_id}': {
                    'me': {},
                    'all': {},
                },
            },
            'prj': {
                '{project_id}': {
                    'me': {},
                    'all': {},
                },
            },
        },
        'hr.employee.edit': {'4': {}},
        '{app_label}.{model_code}.{perm_code}': {'{range_code}': {}},
    }
    permissions_parsed = models.JSONField(default=dict, verbose_name='Data was parsed')

    def sync_plan_app(self, plan_app_data_dict):
        ids_valid = []
        for obj in PlanRole.objects.filter(plan_id__in=plan_app_data_dict.keys(), role=self):
            data = plan_app_data_dict.get(str(obj.plan_id), None)
            if data:
                ids_valid.append(str(obj.plan_id))
                obj.application = data['application']
                obj.application_m2m.clear()
                for app_id in data['application']:
                    PlanRoleApp.objects.create(plan_role=obj, application_id=app_id)

        if len(ids_valid) < len(plan_app_data_dict.keys()):
            for plan_id, data in plan_app_data_dict.items():
                if plan_id not in ids_valid:
                    obj = PlanRole.objects.create(plan_id=plan_id, role=self, application=data['application'])
                    for app_id in data['application']:
                        PlanRoleApp.objects.create(plan_role=obj, application_id=app_id)
        return super().save()

    class Meta:
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class RoleHolder(SimpleAbstractModel):
    employee = models.ForeignKey(
        'hr.Employee',
        on_delete=models.CASCADE,
        null=True,
    )

    role = models.ForeignKey(
        'hr.Role',
        on_delete=models.CASCADE,
        null=True,
    )


class PlanRole(SimpleAbstractModel):
    plan = models.ForeignKey(
        'base.SubscriptionPlan',
        on_delete=models.CASCADE,
        related_name='role_plans',
    )
    role = models.ForeignKey(
        'hr.Role',
        on_delete=models.CASCADE,
        related_name='role_plan_app',
    )
    application = models.JSONField(default=list)
    application_m2m = models.ManyToManyField(
        'base.Application',
        through='PlanRoleApp',
        related_name='role_apps',
        symmetrical=False,
        blank=True,
    )

    class Meta:
        verbose_name = 'Plan of Role'
        verbose_name_plural = 'Plan of Role'
        default_permissions = ()
        permissions = ()


class PlanRoleApp(SimpleAbstractModel):
    plan_role = models.ForeignKey(
        'hr.PlanRole',
        on_delete=models.CASCADE,
        related_name='app_of_plan_role',
    )
    application = models.ForeignKey(
        'base.Application',
        on_delete=models.CASCADE,
        related_name='app_use_by_plan_role',
    )

    class Meta:
        verbose_name = 'App of Plan Role'
        verbose_name_plural = 'App of Plan Role'
        unique_together = ('plan_role', 'application')
        default_permissions = ()
        permissions = ()


class RolePermission(SimpleAbstractModel, PermissionAbstractModel):
    role = models.OneToOneField(Role, on_delete=models.CASCADE)

    def sync_parsed_to_main(self):
        self.role.permissions_parsed = self.permissions_parsed
        self.role.save(update_fields=['permissions_parsed'])

    def get_app_allowed(self) -> tuple[list[str], list[str]]:
        app_ids, app_prefix = [], []
        for obj in PlanRoleApp.objects.select_related('application').filter(plan_role__role=self.role):
            app_ids.append(str(obj.application_id))
            app_prefix.append(obj.application.get_prefix_permit())
        return app_ids, app_prefix

    def save(self, *args, **kwargs):
        sync_parsed = kwargs.pop('sync_parsed', False)
        super().save(*args, **kwargs)
        if sync_parsed is True:
            self.sync_parsed_to_main()

    class Meta:
        verbose_name = 'Permission of Role'
        verbose_name_plural = 'Permission of Role'
        default_permissions = ()
        permissions = ()
