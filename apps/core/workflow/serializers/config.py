from django.utils import timezone
from django.utils.translation import gettext_lazy as trans

from rest_framework import serializers

from apps.core.base.models import Application
from apps.core.workflow.models import (
    Workflow, Zone, Association, CollaborationOutForm,
    WorkflowConfigOfApp, WORKFLOW_CONFIG_MODE,  # pylint: disable-msg=E0611
)
from apps.core.workflow.serializers.config_common import CommonCreateUpdate
from apps.core.workflow.serializers.config_sub import (
    NodeCreateSerializer, ZoneDetailSerializer,
    ZoneCreateSerializer, AssociationCreateSerializer, NodeDetailSerializer,
)
from apps.shared import WorkflowMsg


# workflow of app
class WorkflowOfAppListSerializer(serializers.ModelSerializer):
    workflow_currently = serializers.SerializerMethodField()
    title_i18n = serializers.SerializerMethodField()

    @classmethod
    def get_workflow_currently(cls, obj):
        return {
            'id': obj.workflow_currently_id,
            'title': obj.workflow_currently.title,
        } if obj.workflow_currently else {}

    @classmethod
    def get_title_i18n(cls, obj):
        return trans(obj.title)

    class Meta:
        model = WorkflowConfigOfApp
        fields = ('id', 'title', 'title_i18n', 'code', 'application_id', 'mode', 'error_total', 'workflow_currently')


class WorkflowOfAppUpdateSerializer(serializers.ModelSerializer):
    mode = serializers.ChoiceField(choices=WORKFLOW_CONFIG_MODE, required=False, help_text=str(WORKFLOW_CONFIG_MODE))
    workflow_currently = serializers.UUIDField(
        required=False, help_text='ID of workflow - had application equal application of ID'
    )

    def validate_workflow_currently(self, attrs):
        if attrs:
            try:
                obj = Workflow.objects.get(pk=attrs, application=self.instance.application)
                return obj
            except Workflow.DoesNotExist:
                pass
            raise serializers.ValidationError(
                {
                    'workflow_currently': 'The record is not found'
                }
            )
        raise serializers.ValidationError(
            {
                'workflow_currently': 'This field should be ID.'
            }
        )

    def validate(self, attrs):
        mode = self.instance.mode
        if 'mode' in attrs:
            mode = attrs['mode']

        wf_current = self.instance.workflow_currently
        if 'workflow_currently' in attrs:
            wf_current = attrs['workflow_currently']

        if mode == 1 and not wf_current:
            raise serializers.ValidationError({'detail': WorkflowMsg.WORKFLOW_APPLY_REQUIRED_WF})

        if mode == 1 and wf_current:
            wf_current.date_applied = timezone.now()
            wf_current.save(update_fields=['date_applied'])

        return attrs

    class Meta:
        model = WorkflowConfigOfApp
        fields = ('mode', 'workflow_currently')


# Workflow Config
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
        return {
            'id': obj.application_id,
            'title': obj.application.title,
            'title_i18n': trans(obj.application.title),
        } if obj.application else {}

    @classmethod
    def get_zone(cls, obj):
        return ZoneDetailSerializer(
            Zone.objects.prefetch_related(
                'properties'
            ).filter(
                workflow=obj
            ),
            many=True
        ).data

    @classmethod
    def get_node(cls, obj):
        return NodeDetailSerializer(obj.node_workflow.all(), many=True).data

    @classmethod
    def get_association(cls, obj):
        return [
            {'node_in': association[0], 'node_out': association[1], 'condition': association[2]}
            for association in Association.objects.filter(
                workflow=obj
            ).values_list(
                'node_in_data',
                'node_out_data',
                'condition',
            )
        ]


class WorkflowCreateSerializer(serializers.ModelSerializer):
    title = serializers.CharField()
    application = serializers.UUIDField()
    node = NodeCreateSerializer(many=True)
    zone = ZoneCreateSerializer(
        many=True,
        required=False
    )
    actions_rename = serializers.ListField(
        child=serializers.JSONField(required=False),
        required=False
    )
    association = AssociationCreateSerializer(many=True)

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
        except Application.DoesNotExist:
            raise serializers.ValidationError({'application': WorkflowMsg.APPLICATION_REQUIRED})

    @classmethod
    def validate_node(cls, value):
        if isinstance(value, list):
            if len(value) > 0:
                return value
            raise serializers.ValidationError({'node': WorkflowMsg.NODE_REQUIRED})
        raise serializers.ValidationError({'node': WorkflowMsg.NODE_IS_ARRAY})

    @classmethod
    def validate_association(cls, value):
        if isinstance(value, list):
            if len(value) > 0:
                return value
            raise serializers.ValidationError({'association': WorkflowMsg.ASSOCIATE_REQUIRED})
        raise serializers.ValidationError({'association': WorkflowMsg.ASSOCIATE_IS_ARRAY})

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
    node = NodeCreateSerializer(many=True)
    zone = ZoneCreateSerializer(
        many=True,
        required=False
    )
    actions_rename = serializers.ListField(
        child=serializers.JSONField(required=False),
        required=False
    )
    association = AssociationCreateSerializer(many=True)

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
        except Application.DoesNotExist:
            raise serializers.ValidationError({'application': WorkflowMsg.APPLICATION_REQUIRED})

    @classmethod
    def validate_node(cls, value):
        if isinstance(value, list):
            if len(value) > 0:
                return value
            raise serializers.ValidationError({'node': WorkflowMsg.NODE_REQUIRED})
        raise serializers.ValidationError({'node': WorkflowMsg.NODE_IS_ARRAY})

    @classmethod
    def validate_association(cls, value):
        if isinstance(value, list):
            if len(value) > 0:
                return value
            raise serializers.ValidationError({'association': WorkflowMsg.ASSOCIATE_REQUIRED})
        raise serializers.ValidationError({'association': WorkflowMsg.ASSOCIATE_IS_ARRAY})

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


# workflow current of app
class WorkflowCurrentOfAppSerializer(serializers.ModelSerializer):
    workflow_currently = serializers.SerializerMethodField()

    @classmethod
    def get_workflow_currently(cls, obj):
        try:
            initial_node = obj.workflow_currently.node_workflow.get(
                is_system=True, code_node_system='initial'
            ) if obj.workflow_currently else None
            if initial_node:
                initial_zones = cls.get_initial_zones(initial_node)
                initial_zones_hidden = cls.get_initial_zones_hidden(initial_node)
                association = cls.get_association(initial_node)
                return {
                    'id': obj.workflow_currently_id,
                    'title': obj.workflow_currently.title,
                    'initial_zones': initial_zones,
                    'initial_zones_hidden': initial_zones_hidden,
                    'is_edit_all_zone': initial_node.is_edit_all_zone,
                    'association': association,
                }
        except Exception as err:
            print(err)
        return {}

    @classmethod
    def get_initial_zones(cls, initial_node):
        initial_zones = []
        for node_zone in initial_node.init_node_zone_node.filter(
                node=initial_node
        ).select_related('zone').prefetch_related('zone__properties'):
            if node_zone.zone:
                for prop in node_zone.zone.properties.all():
                    initial_zones.append({'id': prop.id, 'title': prop.title, 'code': prop.code})
        return initial_zones

    @classmethod
    def get_initial_zones_hidden(cls, initial_node):
        initial_zones_hidden = []
        for node_zone_hidden in initial_node.init_node_zone_hidden_node.filter(
                node=initial_node
        ).select_related('zone').prefetch_related('zone__properties'):
            if node_zone_hidden.zone:
                for prop in node_zone_hidden.zone.properties.all():
                    initial_zones_hidden.append({'id': prop.id, 'title': prop.title, 'code': prop.code})
        return initial_zones_hidden

    @classmethod
    def get_collab_out_form(cls, collab):
        collab_out_form = []
        for employee in collab.employees.select_related('group').all():
            collab_out_form.append({
                'id': employee.id,
                'first_name': employee.first_name,
                'last_name': employee.last_name,
                'email': employee.email,
                'full_name': employee.get_full_name(2),
                'code': employee.code,
                'group': {
                    'id': employee.group_id,
                    'title': employee.group.title,
                    'code': employee.group.code
                } if employee.group else {},
                'is_active': employee.is_active,
            })
        return collab_out_form

    @classmethod
    def get_association(cls, initial_node):
        association = []
        for associate in initial_node.transition_node_input.select_related('node_out'):
            if associate.node_out:
                collab_out_form = []
                if associate.node_out.option_collaborator == 1:  # out form
                    collab = CollaborationOutForm.objects.get(node=associate.node_out)
                    collab_out_form = cls.get_collab_out_form(collab=collab)
                association.append({
                    'id': associate.id,
                    'node_out': {
                        'id': associate.node_out_id,
                        'title': associate.node_out.title,
                        'code': associate.node_out.code,
                        'option_collaborator': associate.node_out.option_collaborator,
                        'collab_out_form': collab_out_form,
                    },
                    'condition': associate.condition,
                })
        return association

    class Meta:
        model = WorkflowConfigOfApp
        fields = ('id', 'title', 'code', 'application_id', 'mode', 'error_total', 'workflow_currently')
