from rest_framework import serializers
from apps.masterdata.saledata.models.document import (
    DocumentType
)
from apps.shared import ( BaseMsg, )

# Document
class DocumentTypeListSerializer(serializers.ModelSerializer):  # noqa

    class Meta:
        model = DocumentType
        fields = ('id', 'code', 'title')


class DocumentTypeCreateSerializer(serializers.ModelSerializer):
    code = serializers.CharField(max_length=100)
    title = serializers.CharField(max_length=100)

    class Meta:
        model = DocumentType
        fields = ('code', 'title')

    @classmethod
    def validate_title(cls, value):
        if value:
            return value
        raise serializers.ValidationError({"title": BaseMsg.REQUIRED})

    @classmethod
    def validate_code(cls, value):
        if value:
            if DocumentType.objects.filter_current(fill__tenant=True, fill__company=True, code=value).exists():
                raise serializers.ValidationError(BaseMsg.CODE_IS_EXISTS)
            return value
        raise serializers.ValidationError({"code": BaseMsg.REQUIRED})

class DocumentTypeDetailSerializer(serializers.ModelSerializer):  # noqa

    class Meta:
        model = DocumentType
        fields = ('id', 'code', 'title')