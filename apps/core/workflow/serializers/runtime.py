from rest_framework import serializers

from apps.core.base.models import ApplicationProperty
from apps.core.workflow.models import Runtime, RuntimeStage, RuntimeAssignee
from apps.core.workflow.tasks import call_approval_task
from apps.shared import call_task_background

__all__ = [
    'RuntimeListSerializer',
    'RuntimeMeListSerializer',
    'RuntimeStageListSerializer',
    'RuntimeDetailSerializer',
    'RuntimeAssigneeListSerializer',
    'RuntimeAssigneeUpdateSerializer',
]


class RuntimeListSerializer(serializers.ModelSerializer):
    doc_employee_created = serializers.SerializerMethodField()
    stage_currents = serializers.SerializerMethodField()

    @classmethod
    def get_doc_employee_created(cls, obj):
        if obj.doc_employee_created:
            return {
                'id': obj.doc_employee_created.id,
                'first_name': obj.doc_employee_created.first_name,
                'last_name': obj.doc_employee_created.last_name,
                'full_name': obj.doc_employee_created.get_full_name(),
                'is_active': obj.doc_employee_created.is_active,
            }
        return {}

    @classmethod
    def get_stage_currents(cls, obj):
        if obj.stage_currents:
            return {
                'id': obj.stage_currents.id,
                'title': obj.stage_currents.title,
                'code': obj.stage_currents.code,
            }
        return {}

    class Meta:
        model = Runtime
        fields = (
            'id', 'doc_id', 'doc_title', 'app_id', 'doc_employee_created', 'flow_id', 'state', 'status',
            'date_created', 'date_finished',
            'stage_currents',
        )


class RuntimeMeListSerializer(serializers.ModelSerializer):
    stage_currents = serializers.SerializerMethodField()
    assignees = serializers.SerializerMethodField()

    @classmethod
    def get_stage_currents(cls, obj):
        if obj.stage_currents:
            return {
                'id': obj.stage_currents.id,
                'title': obj.stage_currents.title,
                'code': obj.stage_currents.code,
            }
        return {}

    @classmethod
    def get_assignees(cls, obj):
        return [
            {
                'employee_id': x.employee_id,
                'employee_data': x.employee_data,
                'action_perform': x.action_perform,
                'is_done': x.is_done,
                'date_created': x.date_created,
            } for x in (
                obj.stage_currents.assignee_of_runtime_stage.all()
                if obj.stage_currents and obj.stage_currents.assignee_of_runtime_stage
                else []
            )
        ]

    class Meta:
        model = Runtime
        fields = (
            'id', 'doc_id', 'doc_title', 'app_code', 'app_id', 'doc_employee_created_id', 'flow_id', 'state', 'status',
            'date_created', 'date_finished',
            'stage_currents', 'assignees',
            'doc_pined_id',
        )


class RuntimeStageListSerializer(serializers.ModelSerializer):
    from_stage = serializers.SerializerMethodField()
    to_stage = serializers.SerializerMethodField()
    assignee_and_zone = serializers.SerializerMethodField()
    logs = serializers.SerializerMethodField()

    @classmethod
    def get_from_stage(cls, obj):
        if obj.from_stage:
            return {
                "id": str(obj.from_stage.id),
                "title": obj.from_stage.title,
                "code": obj.from_stage.code,
            }
        return {}

    @classmethod
    def get_to_stage(cls, obj):
        if obj.to_stage:
            return {
                "id": str(obj.to_stage.id),
                "title": obj.to_stage.title,
                "code": obj.to_stage.code,
            }
        return {}

    @classmethod
    def get_assignee_and_zone(cls, obj):
        return [
            {
                "id": str(y.employee_id),
                "full_name": str(y.employee.get_full_name()),
                "zone_and_properties": y.zone_and_properties,
                "is_done": y.is_done,
            } for y in (
                obj.assignee_of_runtime_stage.all()
                if obj.assignee_of_runtime_stage
                else []
            )
        ]

    @classmethod
    def get_logs(cls, obj):
        return [
            {
                "actor_data": log.actor_data,
                "date_created": log.date_created,
                "kind": log.kind,
                "action": log.action,
                "msg": log.msg,
                "is_system": log.is_system,
            } for log in obj.log_of_stage_runtime.all()
        ]

    class Meta:
        model = RuntimeStage
        fields = (
            'id', 'title', 'code', 'node_data', 'actions',
            'exit_node_conditions', 'association_passed_data', 'assignee_count',
            'from_stage', 'to_stage', 'assignee_and_zone', 'log_count', 'date_created',
            'logs',
        )


class ApplicationPropertySubDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationProperty
        fields = ('id', 'remark', 'code', 'type', 'content_type', 'properties', 'compare_operator')


class RuntimeAssigneeListSerializer(serializers.ModelSerializer):
    employee = serializers.SerializerMethodField()
    stage = serializers.SerializerMethodField()
    stage__runtime = serializers.SerializerMethodField()
    doc_title = serializers.SerializerMethodField()
    app_code = serializers.SerializerMethodField()

    @classmethod
    def get_employee(cls, obj):
        if obj.employee:
            return obj.employee.get_detail_minimal()
        return {}

    @classmethod
    def get_stage(cls, obj):
        if obj.stage:
            return {
                'id': obj.stage.id,
                'title': obj.stage.title
            }
        return {}

    @classmethod
    def get_stage__runtime(cls, obj):
        if obj.stage:
            if obj.stage.runtime:
                runtime_obj = obj.stage.runtime
                return {
                    'id': runtime_obj.id,
                    'doc_id': runtime_obj.doc_id,
                    'doc_title': runtime_obj.doc_title,
                    'app_code': runtime_obj.app_code,
                    'flow_id': runtime_obj.flow_id,
                    'state': runtime_obj.state,
                    'status': runtime_obj.status,
                    'doc_pined_id': runtime_obj.doc_pined_id,
                }
        return {}

    @classmethod
    def get_doc_title(cls, obj):
        if obj.stage:
            if obj.stage.runtime:
                return obj.stage.runtime.doc_title
        return ''

    @classmethod
    def get_app_code(cls, obj):
        if obj.stage:
            if obj.stage.runtime:
                return obj.stage.runtime.app_code
        return {}

    class Meta:
        model = RuntimeAssignee
        fields = (
            'id', 'doc_title', 'app_code', 'stage', 'stage__runtime', 'employee', 'is_done', 'date_created'
        )


class RuntimeDetailSerializer(serializers.ModelSerializer):
    action_myself = serializers.SerializerMethodField()
    stage_currents = serializers.SerializerMethodField()
    zones_hidden_myself = serializers.SerializerMethodField()

    @staticmethod
    def get_properties_data(zone_and_properties):
        if len(zone_and_properties) > 0:
            properties_id = []
            for detail in zone_and_properties:
                properties_id += detail['properties']

            property_objs = ApplicationProperty.objects.filter(id__in=properties_id)
            if property_objs:
                return ApplicationPropertySubDetailSerializer(property_objs, many=True).data
        return []

    def get_action_myself(self, obj):
        employee_current_id = self.context.get('employee_current_id', None)
        if employee_current_id and obj.stage_currents:
            if str(employee_current_id) in obj.stage_currents.assignee_and_zone_data:
                stage_assignee_obj = RuntimeAssignee.objects.filter_current(
                    stage=obj.stage_currents,
                    employee_id=employee_current_id,
                    is_done=False,
                ).first()
                if stage_assignee_obj:
                    return {
                        'id': stage_assignee_obj.id,
                        'actions': obj.stage_currents.actions,
                        'zones': self.get_properties_data(stage_assignee_obj.zone_and_properties),
                        'zones_hidden': self.get_properties_data(stage_assignee_obj.zone_hidden_and_properties),
                        'is_edit_all_zone': stage_assignee_obj.is_edit_all_zone,
                    }
        return {}

    @classmethod
    def get_stage_currents(cls, obj):
        if obj.stage_currents:
            return {
                'id': obj.stage_currents.id,
                'title': obj.stage_currents.title,
                'code': obj.stage_currents.code,
                'assignee_count': obj.stage_currents.assignee_count,
            }
        return {}

    def get_zones_hidden_myself(self, obj):
        zone_hidden_list = []
        employee_current_id = self.context.get('employee_current_id', None)
        if employee_current_id and obj.stage_currents:
            stage_assignee_list = RuntimeAssignee.objects.filter_current(
                stage__runtime=obj,
                employee_id=employee_current_id,
            )
            if stage_assignee_list:
                for stage_assignee_obj in stage_assignee_list:
                    zone_hidden_list += self.get_properties_data(stage_assignee_obj.zone_hidden_and_properties)
        return zone_hidden_list

    class Meta:
        model = Runtime
        fields = (
            'id', 'stage_currents', 'date_finished', 'date_created', 'state', 'status', 'action_myself',
            'zones_hidden_myself',
        )


class RuntimeAssigneeUpdateSerializer(serializers.ModelSerializer):
    action = serializers.IntegerField(
        help_text='Action code submit'
    )

    def validate_action(self, attrs):
        if self.instance.stage:
            if attrs in self.instance.stage.actions:
                return attrs
        raise serializers.ValidationError(
            {
                'action': 'Action not support for you'
            }
        )

    def update(self, instance, validated_data):
        action_code = int(validated_data['action'])
        call_task_background(
            call_approval_task,
            *[
                str(instance.id),
                str(instance.employee_id),
                action_code,
            ]
        )
        return instance

    class Meta:
        model = RuntimeAssignee
        fields = ('action',)
