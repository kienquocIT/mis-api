from rest_framework import serializers

from apps.core.base.models import Application
from apps.core.recurrence.models import Recurrence, RecurrenceNext
from apps.shared import BaseMsg


class RecurrenceCommonCreate:
    @classmethod
    def create_subs(cls, instance):
        if instance:
            RecurrenceNext.objects.all().delete()
            RecurrenceNext.objects.bulk_create([RecurrenceNext(
                recurrence=instance,
                tenant_id=instance.tenant_id,
                company_id=instance.company_id,
                employee_created_id=instance.employee_created_id,
                date_next=date_next,
            ) for date_next in instance.next_recurrences])
        return True


# RECURRENCE BEGIN
class RecurrenceListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recurrence
        fields = (
            'id',
            'title',
            'application_data',
            'app_code',
            'doc_template_id',
            'doc_template_data',
            'period',
            'repeat',
            'date_daily',
            'weekday',
            'monthday',
            'date_yearly',
            'date_start',
            'date_end',
            'date_next',
            'next_recurrences',
            'recurrence_status',
        )


class RecurrenceDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recurrence
        fields = (
            'id',
            'title',
            'application_data',
            'app_code',
            'doc_template_id',
            'doc_template_data',
            'period',
            'repeat',
            'date_daily',
            'weekday',
            'monthday',
            'date_yearly',
            'date_start',
            'date_end',
            'date_next',
            'next_recurrences',
            'recurrence_status',
        )


class RecurrenceCreateSerializer(serializers.ModelSerializer):
    application_id = serializers.UUIDField()
    doc_template_id = serializers.UUIDField()

    class Meta:
        model = Recurrence
        fields = (
            'title',
            'application_id',
            'application_data',
            'app_code',
            'doc_template_id',
            'doc_template_data',
            'period',
            'repeat',
            'date_daily',
            'weekday',
            'monthday',
            'date_yearly',
            'date_start',
            'date_end',
            'date_next',
            'next_recurrences',
            'recurrence_status',
        )

    @classmethod
    def validate_application_id(cls, value):
        try:
            return Application.objects.get(id=value).id
        except Application.DoesNotExist:
            raise serializers.ValidationError({'application': BaseMsg.APPLICATION_NOT_EXIST})

    def create(self, validated_data):
        recurrence = Recurrence.objects.create(**validated_data)
        RecurrenceCommonCreate.create_subs(instance=recurrence)
        return recurrence


class RecurrenceUpdateSerializer(serializers.ModelSerializer):
    application_id = serializers.UUIDField()
    doc_template_id = serializers.UUIDField()

    class Meta:
        model = Recurrence
        fields = (
            'title',
            'application_id',
            'application_data',
            'app_code',
            'doc_template_id',
            'doc_template_data',
            'period',
            'repeat',
            'date_daily',
            'weekday',
            'monthday',
            'date_yearly',
            'date_start',
            'date_end',
            'date_next',
            'next_recurrences',
            'recurrence_status',
        )

    @classmethod
    def validate_application_id(cls, value):
        try:
            return Application.objects.get(id=value).id
        except Application.DoesNotExist:
            raise serializers.ValidationError({'application': BaseMsg.APPLICATION_NOT_EXIST})

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        RecurrenceCommonCreate.create_subs(instance=instance)
        return instance
