__all__ = ['MemberOfProjectAddSerializer', 'MemberOfProjectDetailSerializer', 'MemberOfProjectUpdateSerializer']

from rest_framework import serializers

from apps.core.hr.serializers.common import validate_license_used
from apps.core.tenant.models import TenantPlan
from apps.sales.project.extend_func import pj_get_alias_permit_from_app
from apps.sales.project.models import ProjectMapMember, PlanMemberProject
from apps.shared import Caching, DisperseModel
from apps.shared.permissions.util import PermissionController
from apps.shared.translations.opportunity import OpportunityMsg


class MemberOfProjectDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectMapMember
        fields = (
            'id',
            'date_modified',
            'permit_view_this_project',
            'permit_add_member',
            'permit_add_gaw',
            'permission_by_configured',
        )


class MemberOfProjectUpdateSerializer(serializers.ModelSerializer):
    permission_by_configured = serializers.JSONField( # noqa
        required=False,
        help_text=str(
            [{
                "id": "UUID or None",
                "app_id": "UUID",
                "plan_data": "UUID",
                "create": bool,
                "view": bool,
                "edit": bool,
                "delete": bool,
                "range": 'CHOICE("1", "2", "3", "4")',
            }]
        ),
    )

    def validate_permission_by_configured(self, attrs):
        return PermissionController(tenant_id=self.instance.tenant_id).valid(attrs=attrs, has_space=False)

    class Meta:
        model = ProjectMapMember
        fields = (
            'permit_view_this_project',
            'permit_add_member',
            'permit_add_gaw',
            'permission_by_configured',
        )

    def validate(self, validate_data):
        return validate_license_used(validate_data=validate_data)

    @staticmethod
    def set_up_data_plan_app(validated_data, instance=None):
        cls_query = PlanMemberProject # noqa
        filter_query = {'project_member': instance}
        plan_application_dict = {}
        plan_app_data = []
        bulk_info = []
        if 'plan_app' in validated_data:
            plan_app_data = validated_data['plan_app']
            del validated_data['plan_app']
            if instance:
                # delete old M2M PlanEmployee
                plan_x_old = cls_query.objects.filter(**filter_query)
                if plan_x_old:
                    plan_x_old.delete()
        if plan_app_data:
            for plan_app in plan_app_data:
                plan_code = None
                app_code_list = []
                if 'plan' in plan_app:
                    plan_code = plan_app['plan'].code if plan_app['plan'] else None
                if 'application' in plan_app:
                    app_code_list = [app.code for app in plan_app['application']] if plan_app['application'] else []
                if plan_code and app_code_list:
                    plan_application_dict.update({plan_code: app_code_list})
                    bulk_info.append(
                        cls_query(
                            **{
                                'plan': plan_app['plan'],
                                'application': [str(app.id) for app in plan_app['application']]
                            }
                        )
                    )
        return plan_application_dict, plan_app_data, bulk_info

    @staticmethod
    def create_plan_update_tenant_plan(instance, plan_app_data, bulk_info):
        if instance and plan_app_data and bulk_info:
            # create M2M PlanEmployee
            for info in bulk_info:
                info.project_member = instance
            PlanMemberProject.objects.bulk_create(bulk_info)
            # update TenantPlan
            for plan_data in plan_app_data:
                if 'plan' in plan_data and 'license_used' in plan_data:
                    tenant_plan = TenantPlan.objects.filter(
                        tenant=instance.tenant,
                        plan=plan_data['plan']
                    ).first()
                    if tenant_plan:
                        tenant_plan.license_used = plan_data['license_used']
                        tenant_plan.save()
        Caching().clean_by_prefix_many(table_name_list=['hr_PlanEmployee', 'tenant_TenantPlan'])
        return True

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance


class MemberOfProjectAddSerializer(serializers.Serializer):  # noqa
    members = serializers.ListField(
        child=serializers.UUIDField()
    )

    @classmethod
    def validate_members(cls, attrs):
        if len(attrs) > 0:
            objs = DisperseModel(app_model='hr.Employee').get_model().objects.filter_current(
                fill__tenant=True, fill__company=True, id__in=attrs
            )
            if objs.count() == len(attrs):
                return objs
            raise serializers.ValidationError({'members': OpportunityMsg.MEMBER_NOT_EXIST})
        raise serializers.ValidationError({'members': OpportunityMsg.MEMBER_REQUIRED})

    def create(self, validated_data):
        project_id = self.context.get('project_id', None)
        tenant_id = validated_data.get('tenant_id')
        company_id = validated_data.get('company_id')
        members = validated_data.pop('members')
        objs = [
            ProjectMapMember(
                project_id=project_id,
                member=member_obj,
                tenant_id=tenant_id,
                company_id=company_id,
                permission_by_configured=pj_get_alias_permit_from_app(employee_obj=member_obj)
            )
            for member_obj in members
        ]
        return ProjectMapMember.objects.bulk_create(objs)[0]
