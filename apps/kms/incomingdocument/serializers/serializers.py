from rest_framework import serializers

from apps.core.workflow.tasks import decorator_run_workflow
from apps.kms.incomingdocument.models import KMSIncomingDocument
from apps.shared import AbstractCreateSerializerModel, KMSMsg, AbstractDetailSerializerModel


class KMSIncomingDocumentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = KMSIncomingDocument
        fields = (
            'id',
            'title',
            'remark',
            'sender',
            'effective_date',
            'expired_date',
            'security_level'
        )


class KMSIncomingDocumentCreateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=100)

    @decorator_run_workflow
    def create(self, validate_data):
        incoming_doc = KMSIncomingDocument.objects.create(**validate_data)
        return incoming_doc

    class Meta:
        model = KMSIncomingDocument
        fields = (
            'title',
            'remark',
            'sender',
            'effective_date',
            'expired_date',
            'security_level'
        )


class KMSIncomingDocumentDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = KMSIncomingDocument
        fields = (
            'id',
            'title',
            'remark',
            'sender',
            'effective_date',
            'expired_date',
            'security_level'
        )
