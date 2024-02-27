from rest_framework import serializers

from apps.core.printer.models import PrintTemplates


class PrintTemplateListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrintTemplates
        fields = ('id', 'title', 'contents', 'application', 'is_using', 'remarks')


class PrintTemplateDetailSerializer(serializers.ModelSerializer):
    application = serializers.SerializerMethodField()

    @classmethod
    def get_application(cls, obj):
        return {
            'id': obj.application.id,
            'title': obj.application.title,
        } if obj.application else {}

    class Meta:
        model = PrintTemplates
        fields = ('id', 'title', 'contents', 'application', 'is_using', 'remarks')


class PrintTemplateCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrintTemplates
        fields = ('contents', 'application', 'title', 'remarks')


class PrintTemplateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrintTemplates
        fields = ('contents', 'title', 'is_using', 'remarks')
