from rest_framework import serializers

from apps.masterdata.saledata.models import DOC_CATEGORY_CHOICES
from apps.masterdata.saledata.models.document import (
    DocumentType
)
from apps.shared import ( BaseMsg, )

# Document
class DocumentTypeListSerializer(serializers.ModelSerializer):

    class Meta:
        model = DocumentType
        fields = ('id', 'code', 'title', 'is_default', 'doc_type_category',)


class DocumentTypeCreateSerializer(serializers.ModelSerializer):
    code = serializers.CharField(max_length=100)
    title = serializers.CharField(max_length=100)

    class Meta:
        model = DocumentType
        fields = ('code', 'title', 'doc_type_category')

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

    @classmethod
    def validate_doc_type_category(cls, value):
        if value:
            valid_categories = [choice[0] for choice in DOC_CATEGORY_CHOICES]
            if value in valid_categories:
                return value
            raise serializers.ValidationError({"category": BaseMsg.NOT_EXIST})
        raise serializers.ValidationError({"category": BaseMsg.REQUIRED})


class DocumentTypeUpdateSerializer(serializers.ModelSerializer):
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

    def validate_code(self, value):
        if value:
            if DocumentType.objects.filter_current(
                    fill__tenant=True, fill__company=True, code=value
                ).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError(BaseMsg.CODE_IS_EXISTS)
            return value
        raise serializers.ValidationError({"code": BaseMsg.REQUIRED})

class DocumentTypeDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = DocumentType
        fields = ('id', 'code', 'title', 'is_default', 'doc_type_category')
