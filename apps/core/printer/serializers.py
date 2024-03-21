from rest_framework import serializers

from apps.core.mailer.handle_html import HTMLController
from apps.core.printer.models import PrintTemplates
from apps.shared import BaseMsg


class PrintTemplateListSerializer(serializers.ModelSerializer):
    contents = serializers.SerializerMethodField()

    @classmethod
    def get_contents(cls, obj):
        return HTMLController.unescape(obj.contents)

    class Meta:
        model = PrintTemplates
        fields = ('id', 'title', 'contents', 'application', 'is_default', 'is_active', 'remarks')


class PrintTemplateDetailSerializer(serializers.ModelSerializer):
    contents = serializers.SerializerMethodField()

    @classmethod
    def get_contents(cls, obj):
        return HTMLController.unescape(obj.contents)

    application = serializers.SerializerMethodField()

    @classmethod
    def get_application(cls, obj):
        return {
            'id': obj.application.id,
            'title': obj.application.title,
        } if obj.application else {}

    class Meta:
        model = PrintTemplates
        fields = ('id', 'title', 'contents', 'application', 'is_default', 'is_active', 'remarks')


class PrintTemplateCreateSerializer(serializers.ModelSerializer):
    is_active = serializers.BooleanField(default=False)

    @classmethod
    def validate_contents(cls, attrs):
        if not attrs or HTMLController(html_str=attrs).is_html():
            return attrs
        raise serializers.ValidationError(
            {
                'contents': BaseMsg.NOT_IS_HTML,
            }
        )

    class Meta:
        model = PrintTemplates
        fields = ('contents', 'application', 'title', 'remarks', 'is_active')


class PrintTemplateUpdateSerializer(serializers.ModelSerializer):
    @classmethod
    def validate_contents(cls, attrs):
        if not attrs or HTMLController(html_str=attrs).is_html():
            return attrs
        raise serializers.ValidationError(
            {
                'contents': BaseMsg.NOT_IS_HTML,
            }
        )

    class Meta:
        model = PrintTemplates
        fields = ('contents', 'title', 'is_default', 'is_active', 'remarks')
