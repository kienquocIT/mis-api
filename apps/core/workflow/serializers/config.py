from rest_framework import serializers

from apps.core.base.models import Application, ApplicationProperty
from apps.core.hr.models import Employee
from apps.core.workflow.models import Workflow, Node, Collaborator, Zone, Association  # pylint: disable-msg=E0611
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
        child=serializers.UUIDField(required=False),
        required=False
    )
    zone = serializers.ListField(
        child=serializers.IntegerField(required=False),
        required=False
    )

    @classmethod
    def validate_employee_list(cls, value):
        employee_list = Employee.object.filter(id__in=value).count()
        if employee_list == len(value):
            return value
        raise serializers.ValidationError({'detail': HRMsg.EMPLOYEES_NOT_EXIST})


class CollabInWorkflowSerializer(serializers.Serializer):  # noqa
    employee = serializers.UUIDField(
        required=False
    )
    zone = serializers.ListField(
        child=serializers.IntegerField(required=False),
        required=False
    )

    @classmethod
    def validate_employee(cls, value):
        try:
            Employee.object.get(id=value)
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
            'collab_in_workflow'
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
            'is_applied',
            'date_applied',
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
    def node_zone_data(
            cls,
            node,
            option,
            is_initial=False
    ):
        zone_data = []
        node_zone_list = None
        if is_initial:
            if node.zone_initial_node:
                node_zone_list = Zone.objects.filter(
                    id__in=node.zone_initial_node
                ).values(
                    'id',
                    'title'
                )
        else:
            if option == 0:
                node_zone_list = Zone.objects.filter(
                    id__in=node.collab_in_form.get('zone', [])
                ).values(
                    'id',
                    'title'
                )
            elif option == 1:
                node_zone_list = Zone.objects.filter(
                    id__in=node.collab_out_form.get('zone', [])
                ).values(
                    'id',
                    'title'
                )
        if node_zone_list:
            for node_zone in node_zone_list:
                zone_data.append({
                    'id': node_zone['id'],
                    'title': node_zone['title']
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
        collab_in_form = node.collab_in_form
        if collab_in_form:
            collab_in_form.update({'zone': zone_data})
        result.append({
            'id': node.id,
            'title': node.title,
            'remark': node.remark,
            'actions': node.actions,
            'is_system': node.is_system,
            'code_node_system': node.code_node_system,
            'option_collaborator': node.option_collaborator,
            'collab_in_form': collab_in_form,
            'order': node.order,
        })
        return True

    @classmethod
    def node_out_form(cls, node, result, zone_data):
        employee_data = []
        employee_list = Employee.object.filter(id__in=node.collab_out_form.get('employee_list', []))
        if employee_list:
            for employee in employee_list:
                employee_data.append({
                    'id': employee.id,
                    'full_name': employee.get_full_name(2)
                })
        collab_out_form = node.collab_out_form
        if collab_out_form:
            collab_out_form.update({
                'employee_list': employee_data,
                'zone': zone_data
            })
        result.append({
            'id': node.id,
            'title': node.title,
            'remark': node.remark,
            'actions': node.actions,
            'is_system': node.is_system,
            'code_node_system': node.code_node_system,
            'option_collaborator': node.option_collaborator,
            'collab_out_form': collab_out_form,
            'order': node.order,
        })
        return True

    @classmethod
    def node_in_workflow(cls, node, result):
        collaborator_data = []
        in_workflow_collaborator = Collaborator.objects.filter(
            node=node
        )
        if in_workflow_collaborator:
            for collaborator in in_workflow_collaborator:
                zone_in_workflow_data = []
                if collaborator.zone:
                    zone_list = Zone.objects.filter(id__in=collaborator.zone).values(
                        'id',
                        'title'
                    )
                    if zone_list:
                        for zone in zone_list:
                            zone_in_workflow_data.append({
                                'id': zone['id'],
                                'title': zone['title']
                            })
                collaborator_data.append({
                    'employee': {
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
            'collab_in_workflow': collaborator_data,
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
                    if node.option_collaborator == 0 and node.is_system is True:
                        zone_data = cls.node_zone_data(
                            node=node,
                            option=0,
                            is_initial=True
                        )
                        cls.node_system(
                            node=node,
                            result=result,
                            zone_data=zone_data
                        )
                    # option in form
                    elif node.option_collaborator == 0 and node.is_system is False:
                        zone_data = cls.node_zone_data(
                            node=node,
                            option=0,
                        )
                        cls.node_in_form(
                            node=node,
                            result=result,
                            zone_data=zone_data
                        )
                    # option out form
                    elif node.option_collaborator == 1:
                        zone_data = cls.node_zone_data(
                            node=node,
                            option=1,
                        )
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
        ).values(
            'condition',

            'node_in_id',
            'node_in__title',
            'node_in__is_system',
            'node_in__code_node_system',
            'node_in__condition',
            'node_in__order',

            'node_out_id',
            'node_out__title',
            'node_out__is_system',
            'node_out__code_node_system',
            'node_out__condition',
            'node_out__order',
        )
        if association_list:
            for association in association_list:
                result.append({
                    'node_in': {
                        'id': association['node_in_id'],
                        'title': association['node_in__title'],
                        'is_system': association['node_in__is_system'],
                        'code_node_system': association['node_in__code_node_system'],
                        'condition': association['node_in__condition'],
                        'order': association['node_in__order']
                    },
                    'node_out': {
                        'id': association['node_out_id'],
                        'title': association['node_out__title'],
                        'is_system': association['node_out__is_system'],
                        'code_node_system': association['node_out__code_node_system'],
                        'condition': association['node_out__condition'],
                        'order': association['node_out__order'],
                    },
                    'condition': association['condition']
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
    def mapping_zone_detail(
            cls,
            zone_list,
            zone_created_data,
            result,
            collab
    ):
        for zone in zone_list:
            if zone in zone_created_data:
                result.append(zone_created_data[zone])
        collab.update({'zone': result})
        return True

    @classmethod
    def mapping_zone(
            cls,
            option,
            data_dict,
            zone_created_data,
            is_initial=False,
            is_in_workflow=False
    ):
        result = []
        if is_initial:
            zone_list = data_dict.get('zone_initial_node', [])
            for zone in zone_list:
                if zone in zone_created_data:
                    result.append(zone_created_data[zone])
            data_dict.update({'zone_initial_node': result})
        elif is_in_workflow:
            if 'collaborator_zone' in data_dict:
                zone_list = data_dict['collaborator_zone']
                del data_dict['collaborator_zone']
                for zone in zone_list:
                    if zone in zone_created_data:
                        result.append(zone_created_data[zone])
                data_dict.update({'zone': result})
        else:
            if option == 0:
                collab = data_dict.get('collab_in_form', {})
                zone_list = collab.get('zone')
                cls.mapping_zone_detail(
                    zone_list=zone_list,
                    zone_created_data=zone_created_data,
                    result=result,
                    collab=collab
                )
            elif option == 1:
                collab = data_dict.get('collab_out_form', {})
                zone_list = collab.get('zone')
                cls.mapping_zone_detail(
                    zone_list=zone_list,
                    zone_created_data=zone_created_data,
                    result=result,
                    collab=collab
                )
            elif option == 2:
                collab_list = data_dict.get('collab_in_workflow', [])
                for collab in collab_list:
                    result = []
                    zone_list = collab.get('zone')
                    cls.mapping_zone_detail(
                        zone_list=zone_list,
                        zone_created_data=zone_created_data,
                        result=result,
                        collab=collab
                    )
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
    def create_node_data(
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
        return node_create

    @classmethod
    def create_collaborator_in_workflow(
            cls,
            node,
            workflow,
            collaborator_list,
            zone_created_data
    ):
        if collaborator_list:
            bulk_info = []
            for collaborator in collaborator_list:
                # mapping zone
                cls.mapping_zone(
                    option=2,
                    data_dict=collaborator,
                    zone_created_data=zone_created_data,
                    is_in_workflow=True
                )
                bulk_info.append(Collaborator(
                    **collaborator,
                    node=node,
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
                option=None,
                data_dict=node,
                zone_created_data=zone_created_data,
                is_initial=True
            )
            cls.create_node_data(
                node=node,
                workflow=workflow,
                node_created_data=node_created_data
            )
        else:
            if 'option_collaborator' in node:
                # check option & create node

                if node['option_collaborator'] == 0:
                    # mapping zone
                    cls.mapping_zone(
                        option=0,
                        data_dict=node,
                        zone_created_data=zone_created_data
                    )
                elif node['option_collaborator'] == 1:
                    # mapping zone
                    cls.mapping_zone(
                        option=1,
                        data_dict=node,
                        zone_created_data=zone_created_data
                    )
                elif node['option_collaborator'] == 2:
                    # mapping zone
                    cls.mapping_zone(
                        option=2,
                        data_dict=node,
                        zone_created_data=zone_created_data
                    )
                node_create = cls.create_node_data(
                    node=node,
                    workflow=workflow,
                    node_created_data=node_created_data
                )
                if node_create and node['option_collaborator'] == 2:
                    cls.create_collaborator_in_workflow(
                        node=node_create,
                        workflow=workflow,
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
        """
            step 1: set up data for create
            step 2: create workflow
            step 3: create zone for workflow (
                function: create_zone_for_workflow()
            )
            ** when create success Zone will add to zone_created_data use for create Node
                {1: 'zoneID1', 2: 'zoneID2', ...}
            step 4: create node for workflow (
                1/ function: create_node_for_workflow()
                2/ function: create_node()
                    (in create_node() have mapping_zone() & create_node_data())
            )
                ** when create success Node will add to node_created_data use for create Association
                    {1: 'nodeID1', 2: 'nodeID2', ...}
            step 5: create association for workflow (
                function: create_association_for_workflow()
            )
        """
        # set up data for create
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
