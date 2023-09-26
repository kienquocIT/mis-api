from rest_framework import serializers

from apps.core.base.models import Application
from apps.core.hr.models import Employee
from apps.sales.opportunity.models import Opportunity, OpportunitySaleTeamMember, OpportunityMemberPermitData
from apps.sales.task.models import OpportunityTask
from apps.shared.translations.opportunity import OpportunityMsg

__all__ = ['OpportunityAddMemberSerializer', 'OpportunityMemberDetailSerializer', 'OpportunityMemberDeleteSerializer',
           'OpportunityMemberPermissionUpdateSerializer']


class OpportunityMemberSerializer(serializers.Serializer):  # noqa
    id = serializers.UUIDField()

    @classmethod
    def validate_id(cls, value):
        try:  # noqa
            emp = Employee.objects.get(
                id=value
            )
            return emp
        except Employee.DoesNotExist:
            raise serializers.ValidationError({'employee': OpportunityMsg.MEMBER_NOT_EXIST})


class OpportunityAddMemberSerializer(serializers.ModelSerializer):
    members = serializers.ListField(child=OpportunityMemberSerializer())
    employee_current = serializers.UUIDField(required=True)
    opportunity = serializers.UUIDField(required=True)

    class Meta:
        model = Opportunity
        fields = (
            'employee_current',
            'opportunity',
            'members',
        )

    def validate(self, validate_data):
        if len(validate_data['members']) > 0:
            member_add = OpportunitySaleTeamMember.objects.filter(
                opportunity_id=validate_data['opportunity'],
                member=validate_data['employee_current']
            )
            if member_add.exists():
                if not self.check_perm_add_member(member_add.first()):
                    raise serializers.ValidationError(
                        {
                            'employee_current': OpportunityMsg.EMPLOYEE_CAN_ADD_MEMBER
                        }
                    )
            else:
                raise serializers.ValidationError(
                    {
                        'employee_current': OpportunityMsg.EMPLOYEE_NOT_IN_SALE_TEAM
                    }
                )
        return validate_data

    @staticmethod
    def check_perm_add_member(obj):
        return obj.permit_add_member

    def update(self, instance, validated_data):
        sale_team_data = instance.opportunity_sale_team_datas
        bulk_data = []
        for member in validated_data['members']:
            bulk_data.append(
                OpportunitySaleTeamMember(
                    opportunity=instance,
                    member=member['id'],
                    permit_app=OpportunityMemberPermitData.PERMIT_DATA,
                )
            )
            sale_team_data.append(
                {
                    'member': {
                        'id': str(member['id'].id),
                        'full_name': member['id'].get_full_name(),
                        'code': member['id'].code,
                        'group': {
                            'id': str(member['id'].group_id),
                            'title': member['id'].group.title
                        }
                    }
                }
            )

        instance.opportunity_sale_team_datas = sale_team_data
        instance.save(update_fields=['opportunity_sale_team_datas'])
        OpportunitySaleTeamMember.objects.bulk_create(bulk_data)

        return instance


class OpportunityMemberDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpportunitySaleTeamMember
        fields = '__all__'


class OpportunityMemberDeleteSerializer(serializers.ModelSerializer):
    employee_delete = serializers.UUIDField(required=True)
    opportunity = serializers.UUIDField(required=True)

    class Meta:
        model = OpportunitySaleTeamMember
        fields = (
            'employee_delete',
            'opportunity',
        )

    def validate(self, validate_data):
        member_delete = OpportunitySaleTeamMember.objects.filter(
            opportunity_id=validate_data['opportunity'],
            member_id=validate_data['employee_delete']
        )
        if member_delete.exists():
            if not OpportunityAddMemberSerializer.check_perm_add_member(member_delete.first()):
                raise serializers.ValidationError(
                    {
                        'member': OpportunityMsg.EMPLOYEE_CAN_NOT_DELETE
                    }
                )
        else:
            raise serializers.ValidationError(
                {
                    'member': OpportunityMsg.EMPLOYEE_NOT_IN_SALE_TEAM
                }
            )
        return validate_data

    @classmethod
    def check_task_not_completed(cls, instance):
        tasks = OpportunityTask.objects.filter(
            opportunity=instance.opportunity,
            assign_to=instance.member
        ).select_related('task_status')

        return all(task.task_status.task_kind == 2 for task in tasks)

    @classmethod
    def update_opportunity_sale_team_data_backup(cls, instance):
        opportunity = instance.opportunity
        sale_team_data = []
        for member in opportunity.opportunity_sale_team_datas:
            if member['member']['id'] != str(instance.member_id):
                sale_team_data.append(member)
        opportunity.opportunity_sale_team_datas = sale_team_data
        opportunity.save(update_fields=['opportunity_sale_team_datas'])
        return True

    def update(self, instance, validated_data):

        if not self.check_task_not_completed(instance):
            raise serializers.ValidationError(
                {
                    'member': OpportunityMsg.EXIST_TASK_NOT_COMPLETED
                }
            )
        self.update_opportunity_sale_team_data_backup(instance)
        instance.delete()
        return instance


class ApplicationPermitSerializer(serializers.Serializer):  # noqa
    app = serializers.UUIDField()
    is_create = serializers.BooleanField()
    is_edit = serializers.BooleanField()
    is_view_own_activity = serializers.BooleanField()
    is_view_team_activity = serializers.BooleanField()

    @classmethod
    def validate_app(cls, value):
        try:  # noqa
            if value is not None:
                obj = Application.objects.get(
                    id=value
                )
                return str(obj.id)
        except Application.DoesNotExist:
            raise serializers.ValidationError({'application': OpportunityMsg.APPLICATION_NOT_EXIST})
        return None


class OpportunityMemberPermissionUpdateSerializer(serializers.ModelSerializer):
    app_permit = serializers.ListField(child=ApplicationPermitSerializer())
    employee_current = serializers.UUIDField()

    class Meta:
        model = OpportunitySaleTeamMember
        fields = (
            'app_permit',
            'permit_view_this_opp',
            'permit_add_member',
            'employee_current',
        )

    @classmethod
    def check_perm_edit(cls, instance, employee_current):
        return employee_current == instance.opportunity.employee_inherit_id

    def update(self, instance, validated_data):
        if self.check_perm_edit(instance, validated_data['employee_current']):
            permit_app_data = instance.permit_app

            for item in validated_data['app_permit']:
                data = {
                    'is_create': item['is_create'],
                    'is_edit': item['is_edit'],
                    'is_view_own_activity': item['is_view_own_activity'],
                    'is_view_team_activity': item['is_view_team_activity'],
                }
                permit_app_data[item['app']] = data

            instance.permit_app = permit_app_data
            instance.permit_view_this_opp = validated_data['permit_view_this_opp']
            instance.permit_add_member = validated_data['permit_add_member']
            instance.save()
        else:
            raise serializers.ValidationError(
                {
                    'employee_current': OpportunityMsg.NOT_EDIT_PERM_MEMBER
                }
            )
        return instance
