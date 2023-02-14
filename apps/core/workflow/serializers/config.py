from rest_framework import serializers

from apps.core.workflow.models import Workflow, Node, Audit

OPTION_AUDIT = (
    (0, "In form"),
    (1, "Out form"),
    (2, "In workflow"),
)


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
    option_audit = serializers.ChoiceField(choices=OPTION_AUDIT)

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

    class Meta:
        model = Workflow
        fields = (
            'code_application',
            'node',
        )

    def create(self, validated_data):
        # initial
        node_list = None
        audit_list = None
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
                        if 'audit' in node:
                            del node['audit']
                        Node.object_global.create(
                            **node,
                            workflow=workflow
                        )
                    else:
                        if 'audit' in node:
                            audit_list = node['audit']
                            del node['audit']
                        node = Node.object_global.create(
                            **node,
                            workflow=workflow
                        )
                        if audit_list:
                            for audit in audit_list:
                                Audit.object_global.create(
                                    **audit,
                                    node=node
                                )

        return workflow
