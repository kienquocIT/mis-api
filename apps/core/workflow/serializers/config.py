from rest_framework import serializers

from apps.core.base.models import Application
from apps.core.hr.models import Employee
from apps.core.workflow.models import Workflow, Node, Collaborator, Zone, Association  # pylint: disable-msg=E0611
from apps.core.workflow.serializers.config_sub import NodeCreateSerializer, ZoneDetailSerializer, \
    ZoneCreateSerializer, AssociationCreateSerializer


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
            Zone.objects.filter(
                workflow=obj
            ),
            many=True
        ).data

    @classmethod
    def node_zone_data(
            cls,
            node,
            option,
            is_initial=False
    ):
        node_zone_list = []
        if is_initial:
            if node.zone_initial_node:
                node_zone_list = Zone.objects.filter(
                    id__in=node.zone_initial_node
                ).values_list(
                    'id',
                    'title',
                    'order',
                )
        else:
            if option == 0:
                node_zone_list = Zone.objects.filter(
                    id__in=node.collab_in_form.get('zone', [])
                ).values_list(
                    'id',
                    'title',
                    'order',
                )
            elif option == 1:
                node_zone_list = Zone.objects.filter(
                    id__in=node.collab_out_form.get('zone', [])
                ).values_list(
                    'id',
                    'title',
                    'order',
                )
        zone_data = [
            {'id': node_zone[0], 'title': node_zone[1], 'order': node_zone[2]}
            for node_zone in node_zone_list
        ]
        return zone_data

    @classmethod
    def node_system(
            cls,
            node,
            result,
            zone_data
    ):
        result.append({
            'id': node.id,
            'title': node.title,
            'code': node.code,
            'remark': node.remark,
            'actions': node.actions,
            'is_system': node.is_system,
            'code_node_system': node.code_node_system,
            'zone': zone_data,
            'order': node.order,
            'coordinates': node.coordinates
        })
        return True

    @classmethod
    def node_in_form(
            cls,
            node,
            result,
            zone_data
    ):
        collab_in_form = node.collab_in_form
        if collab_in_form:
            collab_in_form.update({'zone': zone_data})
        result.append({
            'id': node.id,
            'title': node.title,
            'code': node.code,
            'remark': node.remark,
            'actions': node.actions,
            'is_system': node.is_system,
            'code_node_system': node.code_node_system,
            'option_collaborator': node.option_collaborator,
            'collab_in_form': collab_in_form,
            'order': node.order,
            'coordinates': node.coordinates
        })
        return True

    @classmethod
    def node_out_form(
            cls,
            node,
            result,
            zone_data
    ):
        employee_list = Employee.objects.filter(
            id__in=node.collab_out_form.get('employee_list', [])
        )
        employee_data = [
            {'id': employee.id, 'full_name': employee.get_full_name(2)}
            for employee in employee_list
        ]
        collab_out_form = node.collab_out_form
        if collab_out_form:
            collab_out_form.update({
                'employee_list': employee_data,
                'zone': zone_data
            })
        result.append({
            'id': node.id,
            'title': node.title,
            'code': node.code,
            'remark': node.remark,
            'actions': node.actions,
            'is_system': node.is_system,
            'code_node_system': node.code_node_system,
            'option_collaborator': node.option_collaborator,
            'collab_out_form': collab_out_form,
            'order': node.order,
            'coordinates': node.coordinates
        })
        return True

    @classmethod
    def node_in_workflow(cls, node, result):
        collaborator_data = []
        in_workflow_collaborator = Collaborator.objects.select_related(
            'employee'
        ).prefetch_related(
            'employee__role',
        ).filter(
            node=node
        )
        if in_workflow_collaborator:
            for collaborator in in_workflow_collaborator:
                role_data = [
                    {'id': role[0], 'title': role[1]}
                    for role in collaborator.employee.role.values_list(
                        'id',
                        'title'
                    )
                ]
                zone_in_workflow_data = [
                    {'id': zone[0], 'title': zone[1], 'order': zone[2]}
                    for zone in Zone.objects.filter(
                        id__in=collaborator.zone
                    ).values_list(
                        'id',
                        'title',
                        'order',
                    )
                ]
                collaborator_data.append({
                    'employee': {
                        'id': collaborator.employee_id,
                        'full_name': collaborator.employee.get_full_name(2),
                        'role': role_data,
                    },
                    'zone': zone_in_workflow_data,
                })
        result.append({
            'id': node.id,
            'title': node.title,
            'code': node.code,
            'remark': node.remark,
            'actions': node.actions,
            'is_system': node.is_system,
            'code_node_system': node.code_node_system,
            'option_collaborator': node.option_collaborator,
            'collab_in_workflow': collaborator_data,
            'order': node.order,
            'coordinates': node.coordinates
        })
        return True

    @classmethod
    def get_node(cls, obj):
        result = []
        node_list = Node.objects.filter(
            workflow=obj
        )
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
        association_list = Association.objects.select_related('node_in', 'node_out').filter(
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


# common class for create/ update workflow
class CommonCreateUpdate:

    @classmethod
    def set_up_data(
            cls,
            validated_data,
            instance=None
    ):
        node_list = None
        zone_list = None
        association_list = None
        zone_created_data = {}
        node_created_data = {}
        if 'association' in validated_data:
            association_list = validated_data['association']
            del validated_data['association']
            # delete old association when update WF
            if instance:
                old_association = Association.objects.filter(workflow=instance)
                if old_association:
                    old_association.delete()
        if 'node' in validated_data:
            node_list = validated_data['node']
            del validated_data['node']
            # delete old node when update WF
            if instance:
                old_node = Node.objects.filter(workflow=instance)
                if old_node:
                    old_node.delete()
        if 'zone' in validated_data:
            zone_list = validated_data['zone']
            del validated_data['zone']
            # delete old zone when update WF
            if instance:
                old_zone = Zone.objects.filter(workflow=instance)
                if old_zone:
                    old_zone.delete()
        return node_list, zone_list, association_list, zone_created_data, node_created_data

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
                zone_list = collab.get('zone', [])
                cls.mapping_zone_detail(
                    zone_list=zone_list,
                    zone_created_data=zone_created_data,
                    result=result,
                    collab=collab
                )
            elif option == 1:
                collab = data_dict.get('collab_out_form', {})
                zone_list = collab.get('zone', [])
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
                    zone_list = collab.get('zone', [])
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
                        zone_created_data.update({order: str(zone.id)})
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
        node_list, zone_list, association_list, zone_created_data, node_created_data = CommonCreateUpdate().set_up_data(
            validated_data=validated_data
        )
        # create workflow
        workflow = Workflow.objects.create(**validated_data)
        # create zone for workflow
        CommonCreateUpdate().create_zone_for_workflow(
            workflow=workflow,
            zone_list=zone_list,
            zone_created_data=zone_created_data
        )
        # create node for workflow
        CommonCreateUpdate().create_node_for_workflow(
            workflow=workflow,
            node_list=node_list,
            zone_created_data=zone_created_data,
            node_created_data=node_created_data
        )
        # create association for workflow
        CommonCreateUpdate().create_association_for_workflow(
            workflow=workflow,
            node_list=node_list,
            association_list=association_list,
            node_created_data=node_created_data
        )
        return workflow


class WorkflowUpdateSerializer(serializers.ModelSerializer):
    application = serializers.UUIDField(required=False)
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

    def update(self, instance, validated_data):
        """
            step 1: set up data for update
            step 2: delete old data:
                    - delete old data Zone
                    - delete old data Node
                    - delete old data Association
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
        # set up data for update
        node_list, zone_list, association_list, zone_created_data, node_created_data = CommonCreateUpdate().set_up_data(
            validated_data=validated_data,
            instance=instance
        )
        # update workflow
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        # create zone for workflow
        CommonCreateUpdate().create_zone_for_workflow(
            workflow=instance,
            zone_list=zone_list,
            zone_created_data=zone_created_data
        )
        # create node for workflow
        CommonCreateUpdate().create_node_for_workflow(
            workflow=instance,
            node_list=node_list,
            zone_created_data=zone_created_data,
            node_created_data=node_created_data
        )
        # create association for workflow
        CommonCreateUpdate().create_association_for_workflow(
            workflow=instance,
            node_list=node_list,
            association_list=association_list,
            node_created_data=node_created_data
        )
        return instance
