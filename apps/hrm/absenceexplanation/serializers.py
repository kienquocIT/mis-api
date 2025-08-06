from rest_framework import serializers

from apps.hrm.absenceexplanation.models import AbsenceExplanation


class AbsenceExplanationListSerializer(serializers.ModelSerializer):
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
        )

    @classmethod
    def get_employee(cls, obj):
        return obj.employee.get_detail_minimal() if obj.employee else {}


class AbsenceExplanationCreateSerializer(serializers.ModelSerializer):
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
            'date'
        )


class AbsenceExplanationDetailSerializer(serializers.ModelSerializer):
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
        )
