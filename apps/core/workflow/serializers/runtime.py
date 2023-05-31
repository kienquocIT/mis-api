from rest_framework import serializers

from apps.core.workflow.models import Runtime

__all__ = [
    'RuntimeListSerializer',
    'RuntimeTaskSerializer',
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


class RuntimeTaskSerializer(serializers.Serializer): # noqa
    action = serializers.IntegerField(
        help_text='Action from config and runtime suggest'
    )
