from rest_framework import serializers

from apps.core.base.models import ApplicationProperty
from apps.core.hr.models import Employee
from apps.core.workflow.models import Node, Zone, Association  # pylint: disable-msg=E0611
from apps.shared import HRMsg, BaseMsg


# Collaborator
class CollabInFormSerializer(serializers.Serializer):  # noqa
    property = serializers.CharField(
        max_length=550,
        required=False
    )
    zone = serializers.ListField(
        child=serializers.IntegerField(required=False),
        required=False
    )

    @classmethod
    def validate_property(cls, value):
        try:
            proper = ApplicationProperty.objects.get(id=value)
            return {
                'id': str(proper.id),
                'title': proper.title,
                'code': proper.code
            }
        except ApplicationProperty.DoesNotExist:
            raise serializers.ValidationError({'detail': BaseMsg.PROPERTY_NOT_EXIST})


class CollabOutFormSerializer(serializers.Serializer):  # noqa
    employee_list = serializers.ListField(
        child=serializers.CharField(required=False),
        required=False
    )
    zone = serializers.ListField(
        child=serializers.IntegerField(required=False),
        required=False
    )

    @classmethod
    def validate_employee_list(cls, value):
        employee_list = Employee.objects.filter_current(
            fill__tenant=True,
            fill__company=True,
            id__in=value
        )
        if employee_list.count() == len(value):
            return [
                {'id': str(employee.id), 'full_name': employee.get_full_name(2)}
                for employee in employee_list
            ]
        raise serializers.ValidationError({'detail': HRMsg.EMPLOYEES_NOT_EXIST})


class CollabInWorkflowSerializer(serializers.Serializer):  # noqa
    employee = serializers.CharField(
        required=False
    )
    zone = serializers.ListField(
        child=serializers.IntegerField(required=False),
        required=False
    )

    @classmethod
    def validate_employee(cls, value):
        try:
            employee = Employee.objects.prefetch_related('role').get(id=value)
            return {
                'id': str(employee.id),
                'full_name': employee.get_full_name(2),
                'role': [
                    {'id': str(role[0]), 'title': role[1]}
                    for role in employee.role.values_list(
                        'id',
                        'title'
                    )
                ]
            }
        except Employee.DoesNotExist as exc:
            raise serializers.ValidationError({'detail': HRMsg.EMPLOYEE_NOT_EXIST}) from exc


# Node
class NodeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Node
        fields = (
            'id',
            'title',
            'code',
            'remark',
            'is_system',
            'order'
        )


class NodeDetailSerializer(serializers.ModelSerializer):
    actions = serializers.JSONField()
    zone_initial_node = serializers.JSONField()
    collab_in_form = serializers.JSONField()
    collab_out_form = serializers.JSONField()
    collab_in_workflow = serializers.JSONField()
    condition = serializers.JSONField()

    class Meta:
        model = Node
        fields = (
            'id',
            'title',
            'code',
            'remark',
            'actions',
            'is_system',
            'code_node_system',
            'zone_initial_node',
            'option_collaborator',
            'collab_in_form',
            'collab_out_form',
            'collab_in_workflow',
            'order',
            'coordinates',
            'condition'
        )


class NodeCreateSerializer(serializers.ModelSerializer):
    collab_in_form = CollabInFormSerializer(
        required=False
    )
    collab_out_form = CollabOutFormSerializer(
        required=False
    )
    collab_in_workflow = CollabInWorkflowSerializer(
        many=True,
        required=False
    )
    actions = serializers.ListField(
        child=serializers.IntegerField(required=False),
        required=False
    )
    condition = serializers.JSONField(required=False)
    zone_initial_node = serializers.JSONField(required=False)
    coordinates = serializers.JSONField(required=False)

    class Meta:
        model = Node
        fields = (
            'title',
            'remark',
            'actions',
            'option_collaborator',
            'zone_initial_node',
            'order',
            'is_system',
            'code_node_system',
            'condition',
            'collab_in_form',
            'collab_out_form',
            'collab_in_workflow',
            'coordinates'
        )


# Zone
class ZoneDetailSerializer(serializers.ModelSerializer):
    property_list = serializers.SerializerMethodField()

    class Meta:
        model = Zone
        fields = (
            'id',
            'title',
            'remark',
            'property_list',
            'order'
        )

    @classmethod
    def get_property_list(cls, obj):
        return [
            {'id': proper[0], 'title': proper[1], 'code': proper[2]}
            for proper in obj.properties.values_list(
                'id',
                'title',
                'code'
            )
        ]


class ZoneCreateSerializer(serializers.ModelSerializer):
    property_list = serializers.ListField(
        child=serializers.CharField(required=True),
        required=True,
    )

    class Meta:
        model = Zone
        fields = (
            'title',
            'remark',
            'property_list',
            'order'
        )


# Association
class AssociationCreateSerializer(serializers.ModelSerializer):
    node_in = serializers.IntegerField()
    node_out = serializers.IntegerField()
    condition = serializers.JSONField()

    class Meta:
        model = Association
        fields = (
            'node_in',
            'node_out',
            'condition'
        )
