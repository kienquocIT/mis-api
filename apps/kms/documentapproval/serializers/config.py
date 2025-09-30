from rest_framework import serializers

from apps.shared import KMSMsg
from ..models import KMSDocumentType, KMSContentGroup, KMSDocumentTypeApplication


def push_m2m_document_type_application(instance):
    if instance:
        instance.document_type_application_document_type.all().delete()
        KMSDocumentTypeApplication.objects.bulk_create([KMSDocumentTypeApplication(
            document_type=instance,
            application_id=application_data.get('id', None)
        ) for application_data in instance.applications_data])
    return True


class KMSDocumentTypeSerializer(serializers.ModelSerializer):
    folder = serializers.SerializerMethodField()

    class Meta:
        model = KMSDocumentType
        fields = ('id', 'title', 'code', 'folder', 'applications_data')

    @classmethod
    def get_folder(cls, value):
        return {
            'id': str(value.folder.id),
            'title': value.folder.title
        } if value.folder else {}


class KMSDocumentTypeCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = KMSDocumentType
        fields = ('title', 'code', 'folder', 'applications_data')

    def create(self, validated_data):
        instance = KMSDocumentType.objects.create(**validated_data)
        push_m2m_document_type_application(instance=instance)
        return instance


class KMSDocumentTypeUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = KMSDocumentType
        fields = ('id', 'title', 'code', 'folder', 'applications_data')

    def validate_code(self, value):
        if KMSDocumentType.objects.filter(code=value).exclude(id=self.instance.id).exists():
            raise serializers.ValidationError(KMSMsg.DUPLICATE_DATA_CODE)
        return value

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        push_m2m_document_type_application(instance=instance)
        return instance


class KMSContentGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = KMSContentGroup
        fields = ('id', 'title', 'code')

    @classmethod
    def validate_code(cls, value):
        if KMSContentGroup.objects.filter(code=value).exists():
            raise serializers.ValidationError(KMSMsg.DUPLICATE_DATA_CODE)
        return value
