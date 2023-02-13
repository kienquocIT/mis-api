from rest_framework import serializers

from apps.core.workflow.models import Workflow, Node, Audit


# Audit
class AuditCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Audit
        fields = (
            'employee',
            'zone'
        )


# Node
class NodeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Node
        fields = (
            'id',
            'remarks',
            'is_system'
        )


class NodeCreateSerializer(serializers.ModelSerializer):
    audit = AuditCreateSerializer()

    class Meta:
        model = Node
        fields = (
            'workflow',
            'title',
            'remarks',
            'actions',
            'option_audit',
            'employee_list',
            'zone',
            'audit'
        )


class NodeUpdateSerializer(serializers.ModelSerializer):
    audit = AuditCreateSerializer(
        many=True,
        required=False
    )

    class Meta:
        model = Node
        fields = (
            'workflow',
            'title',
            'remarks',
            'actions',
            'audit'
        )


# Workflow
class WorkflowListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workflow
        fields = (
            'id',
            'code_application',
            'code'
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

    class Meta:
        model = Workflow
        fields = (
            'code_application',
            'node',
        )

    def create(self, validated_data):
        # initial
        node_list = None
        if 'node' in validated_data:
            node_list = validated_data['node']
            del validated_data['node']

        # create workflow
        workflow = Workflow.object_global.create(**validated_data)

        # create node for workflow
        if workflow and node_list:
            for node in node_list:
                if 'option' in node:
                    if node['option'] != 2:
                        pass

                if 'audit' in node:
                    audit = node['audit']
                    del node['audit']

                node = Node.object_global

