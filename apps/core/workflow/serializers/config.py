from rest_framework import serializers

from apps.core.workflow.models import Workflow, Node, Collaborator, Zone

OPTION_COLLABORATOR = (
    (0, "In form"),
    (1, "Out form"),
    (2, "In workflow"),
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
    employee_list = serializers.ListField(
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
            'field_of_employee',
            'employee_list',
            'node_zone',
            'collaborator',
            'order'
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
    class Meta:
        model = Workflow
        fields = (
            'id',
            'title',
            'code_application',
            'code',
            'is_active',
        )


class WorkflowDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workflow
        fields = (
            'id',
            'code_application',
            'code'
        )


class WorkflowCreateSerializer(serializers.ModelSerializer):
    node = NodeCreateSerializer(
        many=True,
        required=False
    )
    zone = ZoneCreateSerializer(
        many=True,
        required=False
    )

    class Meta:
        model = Workflow
        fields = (
            'title',
            'code_application',
            'node',
            'zone',
            'is_multi_company',
            'is_define_zone',
        )

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
                        workflow=workflow
                    )
                    if zone:
                        zone_created_data.update({order: zone.id})

        # create node for workflow
        if workflow and node_list:
            for node in node_list:
                if 'option_collaborator' in node:
                    # mapping zone
                    if 'node_zone' in node:
                        node_zone_list = node['node_zone']
                        del node['node_zone']
                        node.update({'zone': []})
                        if node_zone_list:
                            for node_zone in node_zone_list:
                                if node_zone in zone_created_data:
                                    node['zone'].append(zone_created_data[node_zone])
                    # check option & create node
                    if node['option'] != 2:
                        if 'collaborator' in node:
                            del node['collaborator']
                        Node.object_global.create(
                            **node,
                            workflow=workflow
                        )
                    else:
                        if 'collaborator' in node:
                            collaborator_list = node['collaborator']
                            del node['collaborator']
                        node = Node.object_global.create(
                            **node,
                            workflow=workflow
                        )
                        if collaborator_list:
                            bulk_info = []
                            for collaborator in collaborator_list:
                                # mapping zone
                                if 'collaborator_zone' in collaborator:
                                    collaborator_zone_list = collaborator['collaborator_zone']
                                    del collaborator['collaborator_zone']
                                    collaborator.update({'zone': []})
                                    if collaborator_zone_list:
                                        for collaborator_zone in collaborator_zone_list:
                                            if collaborator_zone in zone_created_data:
                                                collaborator['zone'].append(zone_created_data[collaborator_zone])

                                bulk_info.append(Collaborator(
                                    **collaborator,
                                    node=node
                                ))
                            if bulk_info:
                                Collaborator.object_global.bulk_create(bulk_info)

        return workflow
