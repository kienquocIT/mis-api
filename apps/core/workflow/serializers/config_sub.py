from rest_framework import serializers

from apps.core.base.models import ApplicationProperty
from apps.core.hr.models import Employee
from apps.core.workflow.models import Node, Zone, Association, CollaborationInForm, \
    CollaborationOutForm, CollabInWorkflow  # pylint: disable-msg=E0611
from apps.shared import HRMsg, BaseMsg


# # COLLAB IN FORM
class CollabInFormSerializer(serializers.ModelSerializer):  # noqa
    app_property = serializers.CharField(
        max_length=550,
        required=False
    )
    zone = serializers.ListField(
        child=serializers.IntegerField(required=False),
        required=False
    )
    zone_hidden = serializers.ListField(
        child=serializers.IntegerField(required=False),
        required=False
    )

    class Meta:
        model = CollaborationInForm
        fields = (
            'id',
            'app_property',
            'zone',
            'zone_hidden',
        )

    @classmethod
    def validate_app_property(cls, value):
        try:
            proper = ApplicationProperty.objects.get(id=value)
            return {
                'id': str(proper.id),
                'title': proper.title,
                'code': proper.code
            }
        except ApplicationProperty.DoesNotExist:
            raise serializers.ValidationError({'app_property': BaseMsg.PROPERTY_NOT_EXIST})


class CollabInFormListSerializer(serializers.ModelSerializer):  # noqa
    app_property = serializers.SerializerMethodField()
    zone = serializers.SerializerMethodField()
    zone_hidden = serializers.SerializerMethodField()

    class Meta:
        model = CollaborationInForm
        fields = (
            'id',
            'app_property',
            'zone',
            'zone_hidden',
        )

    @classmethod
    def get_app_property(cls, obj):
        return {
            'id': obj.app_property_id,
            'title': obj.app_property.title,
            'code': obj.app_property.code,
        } if obj.app_property else {}

    @classmethod
    def get_zone(cls, obj):
        return [
            {'id': zone.id, 'title': zone.title, 'code': zone.code, 'order': zone.order}
            for zone in obj.zone.all()
        ]

    @classmethod
    def get_zone_hidden(cls, obj):
        return [
            {'id': zone.id, 'title': zone.title, 'code': zone.code, 'order': zone.order}
            for zone in obj.zone_hidden.all()
        ]


# COLLAB OUT FORM
class CollabOutFormSerializer(serializers.ModelSerializer):  # noqa
    employee_list = serializers.ListField(
        child=serializers.UUIDField(required=False),
        required=False
    )
    zone = serializers.ListField(
        child=serializers.IntegerField(required=False),
        required=False
    )
    zone_hidden = serializers.ListField(
        child=serializers.IntegerField(required=False),
        required=False
    )

    class Meta:
        model = CollaborationOutForm
        fields = (
            'id',
            'employee_list',
            'zone',
            'zone_hidden',
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
        raise serializers.ValidationError({'employee_list': HRMsg.EMPLOYEES_NOT_EXIST})


class CollabOutFormListSerializer(serializers.ModelSerializer):  # noqa
    employee_list = serializers.SerializerMethodField()
    zone = serializers.SerializerMethodField()
    zone_hidden = serializers.SerializerMethodField()

    class Meta:
        model = CollaborationOutForm
        fields = (
            'id',
            'employee_list',
            'zone',
            'zone_hidden',
        )

    @classmethod
    def get_employee_list(cls, obj):
        return [
            {
                'id': employee.id,
                'full_name': employee.get_full_name(2),
                'code': employee.code,
                'role': [
                    {'id': role.id, 'title': role.title, 'code': role.code}
                    for role in employee.role.all()
                ]
            } for employee in obj.employees.all()
        ]

    @classmethod
    def get_zone(cls, obj):
        return [
            {'id': zone.id, 'title': zone.title, 'code': zone.code, 'order': zone.order}
            for zone in obj.zone.all()
        ]

    @classmethod
    def get_zone_hidden(cls, obj):
        return [
            {'id': zone.id, 'title': zone.title, 'code': zone.code, 'order': zone.order}
            for zone in obj.zone_hidden.all()
        ]


# COLLAB IN WORKFLOW
class CollabInWorkflowSerializer(serializers.ModelSerializer):  # noqa
    in_wf_option = serializers.IntegerField()
    employee = serializers.UUIDField(
        required=False,
        allow_null=True,
    )
    zone = serializers.ListField(
        child=serializers.IntegerField(required=False),
        required=False
    )
    zone_hidden = serializers.ListField(
        child=serializers.IntegerField(required=False),
        required=False
    )

    class Meta:
        model = CollabInWorkflow
        fields = (
            'id',
            'in_wf_option',
            'position_choice',
            'employee',
            'zone',
            'zone_hidden',
        )

    @classmethod
    def validate_employee(cls, value):
        try:
            if value is None:
                return {}
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
        except Employee.DoesNotExist:
            raise serializers.ValidationError({'employee': HRMsg.EMPLOYEE_NOT_EXIST})


class CollabInWorkflowListSerializer(serializers.ModelSerializer):  # noqa
    employee = serializers.SerializerMethodField()
    zone = serializers.SerializerMethodField()
    zone_hidden = serializers.SerializerMethodField()

    class Meta:
        model = CollabInWorkflow
        fields = (
            'id',
            'in_wf_option',
            'position_choice',
            'employee',
            'zone',
            'zone_hidden',
        )

    @classmethod
    def get_employee(cls, obj):
        return {
            'id': obj.employee_id,
            'full_name': obj.employee.get_full_name(2),
            'code': obj.employee.code,
            'group': {
                'id': obj.employee.group_id,
                'title': obj.employee.group.title,
                'code': obj.employee.group.code
            } if obj.employee.group else {},
            'role': [
                {'id': role.id, 'title': role.title, 'code': role.code}
                for role in obj.employee.role.all()
            ],
        } if obj.employee else {}

    @classmethod
    def get_zone(cls, obj):
        return [
            {'id': zone.id, 'title': zone.title, 'code': zone.code, 'order': zone.order}
            for zone in obj.zone.all()
        ]

    @classmethod
    def get_zone_hidden(cls, obj):
        return [
            {'id': zone.id, 'title': zone.title, 'code': zone.code, 'order': zone.order}
            for zone in obj.zone_hidden.all()
        ]


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
    collab_in_form = serializers.SerializerMethodField()
    collab_out_form = serializers.SerializerMethodField()
    collab_in_workflow = serializers.SerializerMethodField()
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

    @classmethod
    def get_collab_in_form(cls, obj):
        if obj.is_system is False and obj.option_collaborator == 0:
            return CollabInFormListSerializer(
                CollaborationInForm.objects.filter(node=obj).select_related(
                    'app_property',
                ).prefetch_related(
                    'zone',
                    'zone_hidden',
                ).first()
            ).data
        return {}

    @classmethod
    def get_collab_out_form(cls, obj):
        if obj.is_system is False and obj.option_collaborator == 1:
            return CollabOutFormListSerializer(
                CollaborationOutForm.objects.filter(node=obj).prefetch_related(
                    'employees',
                    'zone',
                    'zone_hidden',
                ).first()
            ).data
        return {}

    @classmethod
    def get_collab_in_workflow(cls, obj):
        if obj.is_system is False and obj.option_collaborator == 2:
            return CollabInWorkflowListSerializer(
                CollabInWorkflow.objects.filter(node=obj).select_related(
                    'employee',
                    'employee__group',
                ).prefetch_related(
                    'zone',
                    'zone_hidden',
                ),
                many=True
            ).data
        return []


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
    zone_hidden_initial_node = serializers.JSONField(required=False)
    coordinates = serializers.JSONField(required=False)

    class Meta:
        model = Node
        fields = (
            'title',
            'code',
            'remark',
            'actions',
            'option_collaborator',
            'zone_initial_node',
            'zone_hidden_initial_node',
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
