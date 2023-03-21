from rest_framework import serializers

from apps.core.base.models import Application, ApplicationProperty
from apps.core.hr.models import Employee
from apps.core.workflow.models import Workflow, Node, Collaborator, Zone, Association  # pylint: disable-msg=E0611


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
    collaborator = CollaboratorCreateSerializer(
        many=True,
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
    condition = serializers.JSONField(required=False)

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
            'code_node_system',
            'condition'
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
            ).values(
                'id',
                'title',
                'code'
            )
            if property_list:
                for proper in property_list:
                    result.append({
                        'id': proper['id'],
                        'title': proper['title'],
                        'code': proper['code'],
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

    @classmethod
    def get_application(cls, obj):
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
    association = serializers.SerializerMethodField()

    class Meta:
        model = Workflow
        fields = (
            'id',
            'title',
            'code',
            'application',
            'is_multi_company',
            'is_define_zone',
            'actions_rename',
            'zone',
            'node',
            'association',
            'is_active',
        )

    @classmethod
    def get_application(cls, obj):
        if obj.application:
            return {
                'id': obj.application_id,
                'title': obj.application.title
            }
        return {}

    @classmethod
    def get_zone(cls, obj):
        return ZoneDetailSerializer(
            Zone.objects.filter(workflow=obj).order_by('order'),
            many=True
        ).data

    @classmethod
    def node_zone_data(cls, node):
        zone_data = []
        if node.zone:
            node_zone_list = Zone.objects.filter(id__in=node.zone)
            if node_zone_list:
                for node_zone in node_zone_list:
                    zone_data.append({
                        'id': node_zone.id,
                        'title': node_zone.title
                    })
        return zone_data

    @classmethod
    def node_system(cls, node, result, zone_data):
        result.append({
            'id': node.id,
            'title': node.title,
            'remark': node.remark,
            'actions': node.actions,
            'is_system': node.is_system,
            'code_node_system': node.code_node_system,
            'zone': zone_data,
            'order': node.order,
        })
        return True

    @classmethod
    def node_in_form(cls, node, result, zone_data):
        result.append({
            'id': node.id,
            'title': node.title,
            'remark': node.remark,
            'actions': node.actions,
            'is_system': node.is_system,
            'code_node_system': node.code_node_system,
            'option_collaborator': node.option_collaborator,
            'field_select_collaborator': node.field_select_collaborator,
            'zone': zone_data,
            'order': node.order,
        })
        return True

    @classmethod
    def node_out_form(cls, node, result, zone_data):
        employee_data = []
        if node.collaborator_list:
            employee_list = Employee.objects.filter(id__in=node.collaborator_list)
            if employee_list:
                for employee in employee_list:
                    employee_data.append({
                        'id': employee.id,
                        'full_name': employee.get_full_name(2)
                    })
        result.append({
            'id': node.id,
            'title': node.title,
            'remark': node.remark,
            'actions': node.actions,
            'is_system': node.is_system,
            'code_node_system': node.code_node_system,
            'option_collaborator': node.option_collaborator,
            'collaborator_list': employee_data,
            'zone': zone_data,
            'order': node.order,
        })
        return True

    @classmethod
    def node_in_workflow(cls, node, result):
        collaborator_data = []
        in_workflow_collaborator = Collaborator.objects.filter(
            node=node
        ).select_related('employee')
        if in_workflow_collaborator:
            for collaborator in in_workflow_collaborator:
                zone_in_workflow_data = []
                if collaborator.zone:
                    zone_list = Zone.objects.filter(id__in=collaborator.zone)
                    if zone_list:
                        for zone in zone_list:
                            zone_in_workflow_data.append({
                                'id': zone.id,
                                'title': zone.title
                            })
                collaborator_data.append({
                    'collaborator': {
                        'id': collaborator.employee_id,
                        'full_name': collaborator.employee.get_full_name(2)
                    },
                    'zone': zone_in_workflow_data
                })
        result.append({
            'id': node.id,
            'title': node.title,
            'remark': node.remark,
            'actions': node.actions,
            'is_system': node.is_system,
            'code_node_system': node.code_node_system,
            'option_collaborator': node.option_collaborator,
            'collaborator_list': collaborator_data,
            'order': node.order,
        })
        return True

    @classmethod
    def get_node(cls, obj):
        result = []
        node_list = Node.objects.filter(workflow=obj).order_by('order')
        if node_list:
            for node in node_list:
                if node.option_collaborator or node.option_collaborator == 0:
                    zone_data = cls.node_zone_data(node=node)
                    if node.option_collaborator == 0 and node.is_system is True:
                        cls.node_system(
                            node=node,
                            result=result,
                            zone_data=zone_data
                        )
                    # option in form
                    elif node.option_collaborator == 0 and node.is_system is False:
                        cls.node_in_form(
                            node=node,
                            result=result,
                            zone_data=zone_data
                        )
                    # option out form
                    elif node.option_collaborator == 1:
                        cls.node_out_form(
                            node=node,
                            result=result,
                            zone_data=zone_data
                        )
                    # option in workflow
                    elif node.option_collaborator == 2:
                        cls.node_in_workflow(
                            node=node,
                            result=result,
                        )
        return result

    @classmethod
    def get_association(cls, obj):
        result = []
        association_list = Association.objects.filter(
            workflow=obj
        ).select_related(
            'node_in',
            'node_out',
        )
        if association_list:
            for association in association_list:
                result.append({
                    'node_in': {
                        'id': association.node_in_id,
                        'title': association.node_in.title,
                        'code': association.node_in.code,
                        'is_system': association.node_in.is_system,
                        'code_node_system': association.node_in.code_node_system,
                        'condition': association.node_in.condition,
                        'order': association.node_in.order
                    },
                    'node_out': {
                        'id': association.node_out_id,
                        'title': association.node_out.title,
                        'code': association.node_out.code,
                        'is_system': association.node_out.is_system,
                        'code_node_system': association.node_out.code_node_system,
                        'condition': association.node_out.condition,
                        'order': association.node_out.order
                    },
                    'condition': association.condition
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
    association = AssociationCreateSerializer(
        many=True,
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
            'actions_rename',
            'association'
        )

    @classmethod
    def validate_application(cls, value):
        try:
            return Application.objects.get(id=value)
        except Application.DoesNotExist as exc:
            raise serializers.ValidationError("Application does not exist.") from exc

    @classmethod
    def mapping_zone(cls, key, data_dict, zone_created_data):
        if key in data_dict:
            zone_list = data_dict[key]
            del data_dict[key]
            data_dict.update({'zone': []})
            if zone_list:
                for zone in zone_list:
                    if zone in zone_created_data:
                        data_dict['zone'].append(zone_created_data[zone])
        return True

    @classmethod
    def create_zone_for_workflow(
            cls,
            workflow,
            zone_list,
            zone_created_data
    ):
        if workflow and zone_list:
            for zone in zone_list:
                if 'order' in zone:
                    order = zone['order']
                    zone = Zone.objects.create(
                        **zone,
                        workflow=workflow,
                        tenant_id=workflow.tenant_id,
                        company_id=workflow.company_id,
                    )
                    if zone:
                        zone_created_data.update({order: zone.id})
        return True

    @classmethod
    def create_association_for_workflow(
            cls,
            workflow,
            node_list,
            association_list,
            node_created_data
    ):
        if workflow and node_list and association_list:
            if association_list:
                bulk_info = []
                for association in association_list:
                    if 'node_in' in association and 'node_out' in association:
                        if association['node_in'] in node_created_data and association['node_out'] in node_created_data:
                            association.update({
                                'node_in': node_created_data[association['node_in']],
                                'node_out': node_created_data[association['node_out']],
                            })
                            bulk_info.append(Association(
                                **association,
                                workflow=workflow,
                                tenant_id=workflow.tenant_id,
                                company_id=workflow.company_id
                            ))
                if bulk_info:
                    Association.objects.bulk_create(bulk_info)
        return True

    @classmethod
    def create_node_system(
            cls,
            node,
            workflow,
            node_created_data
    ):
        node_create = Node.objects.create(
            **node,
            workflow=workflow,
            tenant_id=workflow.tenant_id,
            company_id=workflow.company_id,
        )
        if node_create and 'order' in node:
            node_created_data.update({node['order']: node_create})
        return True

    @classmethod
    def create_node_option_in_out_form(
            cls,
            node,
            workflow,
            node_created_data
    ):
        node_create = Node.objects.create(
            **node,
            workflow=workflow,
            tenant_id=workflow.tenant_id,
            company_id=workflow.company_id,
        )
        if node_create and 'order' in node:
            node_created_data.update({node['order']: node_create})
        return True

    @classmethod
    def create_node_option_in_workflow(
            cls,
            node,
            workflow,
            node_created_data,
            collaborator_list,
            zone_created_data
    ):
        node_create = Node.objects.create(
            **node,
            workflow=workflow,
            tenant_id=workflow.tenant_id,
            company_id=workflow.company_id,
        )
        if node_create and 'order' in node:
            node_created_data.update({node['order']: node_create})
        if collaborator_list:
            bulk_info = []
            for collaborator in collaborator_list:
                # mapping zone
                cls.mapping_zone(
                    key='collaborator_zone',
                    data_dict=collaborator,
                    zone_created_data=zone_created_data
                )
                bulk_info.append(Collaborator(
                    **collaborator,
                    node=node_create,
                    tenant_id=workflow.tenant_id,
                    company_id=workflow.company_id,
                ))
            if bulk_info:
                Collaborator.objects.bulk_create(bulk_info)
        return True

    @classmethod
    def create_node(
            cls,
            node,
            zone_created_data,
            workflow,
            node_created_data
    ):
        collaborator_list = None
        if 'collaborator' in node:
            collaborator_list = node['collaborator']
            del node['collaborator']
        if node['is_system'] is True:
            # mapping zone
            cls.mapping_zone(
                key='node_zone',
                data_dict=node,
                zone_created_data=zone_created_data
            )
            cls.create_node_system(
                node=node,
                workflow=workflow,
                node_created_data=node_created_data
            )
        else:
            if 'option_collaborator' in node:
                # mapping zone
                cls.mapping_zone(
                    key='node_zone',
                    data_dict=node,
                    zone_created_data=zone_created_data
                )
                # check option & create node
                if node['option_collaborator'] != 2:
                    cls.create_node_option_in_out_form(
                        node=node,
                        workflow=workflow,
                        node_created_data=node_created_data
                    )
                else:
                    cls.create_node_option_in_workflow(
                        node=node,
                        workflow=workflow,
                        node_created_data=node_created_data,
                        collaborator_list=collaborator_list,
                        zone_created_data=zone_created_data
                    )
        return True

    @classmethod
    def create_node_for_workflow(
            cls,
            workflow,
            node_list,
            zone_created_data,
            node_created_data
    ):
        if workflow and node_list:
            for node in node_list:
                if 'is_system' in node:
                    cls.create_node(
                        node=node,
                        zone_created_data=zone_created_data,
                        workflow=workflow,
                        node_created_data=node_created_data
                    )
        return True

    def create(self, validated_data):
        # initial
        node_list = None
        zone_list = None
        association_list = None
        zone_created_data = {}
        node_created_data = {}
        if 'node' in validated_data:
            node_list = validated_data['node']
            del validated_data['node']
        if 'zone' in validated_data:
            zone_list = validated_data['zone']
            del validated_data['zone']
        if 'association' in validated_data:
            association_list = validated_data['association']
            del validated_data['association']

        # create workflow
        workflow = Workflow.objects.create(**validated_data)

        # create zone for workflow
        self.create_zone_for_workflow(
            workflow=workflow,
            zone_list=zone_list,
            zone_created_data=zone_created_data
        )

        # create node for workflow
        self.create_node_for_workflow(
            workflow=workflow,
            node_list=node_list,
            zone_created_data=zone_created_data,
            node_created_data=node_created_data
        )

        # create association for workflow
        self.create_association_for_workflow(
            workflow=workflow,
            node_list=node_list,
            association_list=association_list,
            node_created_data=node_created_data
        )

        return workflow
