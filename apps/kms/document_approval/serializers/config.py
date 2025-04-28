from rest_framework import serializers

from apps.shared import KMSMsg
from ..models import KMSDocumentType, KMSContentGroup


class KMSDocumentTypeSerializer(serializers.ModelSerializer):
    folder = serializers.SerializerMethodField()

    class Meta:
        model = KMSDocumentType
        fields = ('id', 'title', 'code', 'folder')

    @classmethod
    def get_folder(cls, value):
        return {
            'id': str(value.folder.id),
            'title': value.folder.title
        } if value.folder else {}


class KMSDocumentTypeUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = KMSDocumentType
        fields = ('id', 'title', 'code', 'folder')

    @classmethod
    def validate_code(cls, value):
        if KMSDocumentType.objects.filter(code=value).exists():
            raise serializers.ValidationError(KMSMsg.DUPLICATE_DATA_CODE)
        return value


class KMSContentGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = KMSContentGroup
        fields = ('id', 'title', 'code')

    @classmethod
    def validate_code(cls, value):
        if KMSContentGroup.objects.filter(code=value).exists():
            raise serializers.ValidationError(KMSMsg.DUPLICATE_DATA_CODE)
        return value
