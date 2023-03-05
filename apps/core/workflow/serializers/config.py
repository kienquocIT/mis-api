from rest_framework import serializers

from apps.core.base.models import Application, ApplicationProperty
from apps.core.hr.models import Employee
from apps.core.workflow.models import Workflow, Node, Collaborator, Zone
from apps.shared import WorkflowMsg

OPTION_COLLABORATOR = (
    (0, WorkflowMsg.COLLABORATOR_IN),
    (1, WorkflowMsg.COLLABORATOR_OUT),
    (2, WorkflowMsg.COLLABORATOR_WF),
)


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


class NodeCreateSerializer(serializers.ModelSerializer):
    collaborator = CollaboratorCreateSerializer(
        many=True,
        required=False
    )
    option_collaborator = serializers.ChoiceField(
        choices=OPTION_COLLABORATOR,
        required=False
    )
    node_zone = serializers.ListField(
        child=serializers.IntegerField(required=False),
        required=False
    )
    actions = serializers.ListField(
        child=serializers.IntegerField(required=False),
        required=False
    )
    collaborator_list = serializers.ListField(
        child=serializers.UUIDField(required=False),
        required=False
    )

    class Meta:
        model = Node
        fields = (
            'workflow',
            'title',
            'remark',
            'actions',
            'option_collaborator',
            'field_select_collaborator',
            'collaborator_list',
            'node_zone',
            'collaborator',
            'order',
            'is_system',
            'code_node_system'
        )


class NodeUpdateSerializer(serializers.ModelSerializer):
    collaborator = CollaboratorCreateSerializer(
        many=True,
        required=False
    )

    class Meta:
        model = Node
        fields = (
            'workflow',
            'title',
            'remark',
            'actions',
            'collaborator'
        )


# Zone
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


# Workflow
class WorkflowListSerializer(serializers.ModelSerializer):
    application = serializers.SerializerMethodField()

    class Meta:
        model = Workflow
        fields = (
            'id',
            'title',
            'application',
            'code',
            'is_active',
        )

    def get_application(self, obj):
        if obj.application:
            return {
                'id': obj.application_id,
                'title': obj.application.title
            }
        return {}


class WorkflowDetailSerializer(serializers.ModelSerializer):
    actions_rename = serializers.JSONField()
    application = serializers.SerializerMethodField()
    zone = serializers.SerializerMethodField()
    node = serializers.SerializerMethodField()

    class Meta:
        model = Workflow
        fields = (
            'id',
            'application',
            'is_multi_company',
            'is_define_zone',
            'actions_rename',
            'zone',
            'node',
            'is_active',
        )

    def get_application(self, obj):
        if obj.application:
            return {
                'id': obj.application_id,
                'title': obj.application.title
            }
        return {}

    def get_zone(self, obj):
        result = []
        zone_list = Zone.object_global.filter(workflow=obj)
        if zone_list:
            for zone in zone_list:
                if zone.property_list:
                    property_list = ApplicationProperty.objects.filter(
                        id__in=zone.property_list
                    )
                    if property_list:
                        pass
                result.append({
                    'id': zone.id,
                    'title': zone.title,
                    'remark': zone.remark,
                    'property_list': []
                })
        return result

    def get_node(self, obj):
        result = []
        node_list = Node.object_global.filter(workflow=obj)
        if node_list:
            for node in node_list:
                if node.option_collaborator:
                    zone_data = []
                    if node.zone:
                        node_zone_list = Zone.object_global.filter(id__in=node.zone)
                        if node_zone_list:
                            for node_zone in node_zone_list:
                                zone_data.append({
                                    'id': node_zone.id,
                                    'title': node_zone.title
                                })
                    # option in form
                    if node.option_collaborator == 0:
                        result.append({
                            'id': node.id,
                            'title': node.title,
                            'remark': node.remark,
                            'actions': node.actions,
                            'option_collaborator': node.option_collaborator,
                            'field_select_collaborator': node.field_select_collaborator,
                            'zone': zone_data

                        })
                    # option out form
                    elif node.option_collaborator == 1:
                        employee_data = []
                        if node.collaborator_list:
                            employee_list = Employee.object_global.filter(id__in=node.collaborator_list)
                            if employee_list:
                                for employee in employee_list:
                                    employee_data.append({
                                        'id': employee.id,
                                        'title': employee.title
                                    })
                        result.append({
                            'id': node.id,
                            'title': node.title,
                            'remark': node.remark,
                            'actions': node.actions,
                            'option_collaborator': node.option_collaborator,
                            'collaborator_list': employee_data,
                            'zone': zone_data
                        })
                    # option in workflow
                    elif node.option_collaborator == 2:
                        collaborator_data = []
                        in_workflow_collaborator = Collaborator.object_global.filter(
                            node=node
                        ).select_related('employee')
                        if in_workflow_collaborator:
                            for collaborator in in_workflow_collaborator:
                                zone_in_workflow_data = []
                                if collaborator.zone:
                                    zone_list = Zone.object_global.filter(id__in=collaborator.zone)
                                    if zone_list:
                                        for zone in zone_list:
                                            zone_in_workflow_data.append({
                                                'id': zone.id,
                                                'title': zone.title
                                            })
                                collaborator_data.append({
                                    'collaborator': {
                                        'id': collaborator.employee_id,
                                        'title': collaborator.employee.title
                                    },
                                    'zone': zone_in_workflow_data
                                })
                        result.append({
                            'id': node.id,
                            'title': node.title,
                            'remark': node.remark,
                            'actions': node.actions,
                            'option_collaborator': node.option_collaborator,
                            'collaborator_list': collaborator_data,
                        })
        return result


class WorkflowCreateSerializer(serializers.ModelSerializer):
    application = serializers.UUIDField()
    node = NodeCreateSerializer(
        many=True,
        required=False
    )
    zone = ZoneCreateSerializer(
        many=True,
        required=False
    )
    actions_rename = serializers.ListField(
        child=serializers.JSONField(required=False),
        required=False
    )

    class Meta:
        model = Workflow
        fields = (
            'title',
            'application',
            'node',
            'zone',
            'is_multi_company',
            'is_define_zone',
            'actions_rename'
        )

    def validate_application(self, value):
        try:
            return Application.objects.get(id=value)
        except Exception as e:
            raise serializers.ValidationError("Application does not exist.")

    def mapping_zone(self, key, data_dict, zone_created_data):
        if key in data_dict:
            zone_list = data_dict[key]
            del data_dict[key]
            data_dict.update({'zone': []})
            if zone_list:
                for zone in zone_list:
                    if zone in zone_created_data:
                        data_dict['zone'].append(zone_created_data[zone])
        return True

    def create(self, validated_data):
        # initial
        node_list = None
        collaborator_list = None
        zone_list = None
        zone_created_data = {}
        if 'node' in validated_data:
            node_list = validated_data['node']
            del validated_data['node']
        if 'zone' in validated_data:
            zone_list = validated_data['zone']
            del validated_data['zone']

        # create workflow
        workflow = Workflow.object_global.create(**validated_data)

        # create zone
        if workflow and zone_list:
            bulk_info = []
            for zone in zone_list:
                if 'order' in zone:
                    order = zone['order']
                    # del zone['order']
                    zone = Zone.object_global.create(
                        **zone,
                        workflow=workflow,
                        tenant_id=workflow.tenant_id,
                        company_id=workflow.company_id,
                    )
                    if zone:
                        zone_created_data.update({order: zone.id})

        # create node for workflow
        if workflow and node_list:
            for node in node_list:
                if 'is_system' in node:
                    if node['is_system'] is True:
                        # mapping zone
                        self.mapping_zone(
                            key='node_zone',
                            data_dict=node,
                            zone_created_data=zone_created_data
                        )
                    else:
                        if 'option_collaborator' in node:
                            # mapping zone
                            self.mapping_zone(
                                key='node_zone',
                                data_dict=node,
                                zone_created_data=zone_created_data
                            )
                            # check option & create node
                            if node['option_collaborator'] != 2:
                                if 'collaborator' in node:
                                    del node['collaborator']
                                Node.object_global.create(
                                    **node,
                                    workflow=workflow,
                                    tenant_id=workflow.tenant_id,
                                    company_id=workflow.company_id,
                                )
                            else:
                                if 'collaborator' in node:
                                    collaborator_list = node['collaborator']
                                    del node['collaborator']
                                node = Node.object_global.create(
                                    **node,
                                    workflow=workflow,
                                    tenant_id=workflow.tenant_id,
                                    company_id=workflow.company_id,
                                )
                                if collaborator_list:
                                    bulk_info = []
                                    for collaborator in collaborator_list:
                                        # mapping zone
                                        self.mapping_zone(
                                            key='collaborator_zone',
                                            data_dict=collaborator,
                                            zone_created_data=zone_created_data
                                        )
                                        bulk_info.append(Collaborator(
                                            **collaborator,
                                            node=node,
                                            tenant_id=workflow.tenant_id,
                                            company_id=workflow.company_id,
                                        ))
                                    if bulk_info:
                                        Collaborator.object_global.bulk_create(bulk_info)

        return workflow
