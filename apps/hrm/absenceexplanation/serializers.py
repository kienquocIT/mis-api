from rest_framework import serializers

from apps.core.workflow.tasks import decorator_run_workflow
from apps.hrm.absenceexplanation.models import AbsenceExplanation
from apps.shared import AbstractListSerializerModel, AbstractDetailSerializerModel, AbstractCreateSerializerModel


class AbsenceExplanationListSerializer(AbstractListSerializerModel):
    employee = serializers.SerializerMethodField()

    class Meta:
        model = AbsenceExplanation
        fields = (
            'id',
            'code',
            'description',
            'type',
            'employee',
            'date_created',
            'system_status'
        )

    @classmethod
    def get_employee(cls, obj):
        return obj.employee.get_detail_minimal() if obj.employee else {}


class AbsenceExplanationCreateSerializer(AbstractCreateSerializerModel):
    @decorator_run_workflow
    def create(self, validated_data):
        absence_explanation_obj = AbsenceExplanation.objects.create(**validated_data)
        return absence_explanation_obj

    class Meta:
        model = AbsenceExplanation
        fields = (
            'description',
            'employee',
            'type',
            'reason',
            'date',
        )


class AbsenceExplanationDetailSerializer(AbstractDetailSerializerModel):
    employee = serializers.SerializerMethodField()

    class Meta:
        model = AbsenceExplanation
        fields = (
            'id',
            'code',
            'description',
            'type',
            'employee',
            'date',
            'reason',
            'date_created',
            'system_status'
        )

    @classmethod
    def get_employee(cls, obj):
        return obj.employee.get_detail_minimal() if obj.employee else {}


class AbsenceExplanationUpdateSerializer(AbstractCreateSerializerModel):
    @decorator_run_workflow
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    class Meta:
        model = AbsenceExplanation
        fields = (
            'description',
            'employee',
            'type',
            'reason',
            'date'
        )
