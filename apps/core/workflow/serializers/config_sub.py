from rest_framework import serializers

from apps.core.base.models import ApplicationProperty
from apps.core.hr.models import Employee
from apps.core.workflow.models import Node, Collaborator, Zone, Association  # pylint: disable-msg=E0611
from apps.shared import HRMsg


# Collaborator
class CollaboratorCreateSerializer(serializers.ModelSerializer):
    collaborator_zone = serializers.ListField(
        child=serializers.IntegerField(required=False),
        required=False
    )

    class Meta:
        model = Collaborator
        fields = (
            'employee',
            'collaborator_zone'
        )


class CollabInFormSerializer(serializers.Serializer):  # noqa
    employee_field = serializers.CharField(
        max_length=550,
        required=False
    )
    zone = serializers.ListField(
        child=serializers.IntegerField(required=False),
        required=False
    )


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
        employee_list = Employee.objects.filter(id__in=value).count()
        if employee_list == len(value):
            return value
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
            Employee.objects.get(id=value)
            return value
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
    collaborator = CollaboratorCreateSerializer(
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
            'collaborator',
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
        result = []
        if obj.property_list and isinstance(obj.property_list, list):
            property_list = ApplicationProperty.objects.filter(
                id__in=obj.property_list
            ).values_list(
                'id',
                'title',
                'code'
            )
            if property_list:
                for proper in property_list:
                    result.append({
                        'id': proper[0],
                        'title': proper[1],
                        'code': proper[2],
                    })
        return result


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
