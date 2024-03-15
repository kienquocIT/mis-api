from rest_framework import serializers

from apps.core.mailer.handle_html import HTMLController
from apps.core.mailer.models import MailTemplate, MailTemplateSystem
from apps.shared import BaseMsg


class MailTemplateListSerializer(serializers.ModelSerializer):
    contents = serializers.SerializerMethodField()

    @classmethod
    def get_contents(cls, obj):
        return HTMLController.unescape(obj.contents)

    class Meta:
        model = MailTemplate
        fields = ('id', 'title', 'remarks', 'application', 'is_active', 'is_default', 'contents')


class MailTemplateDetailSerializer(serializers.ModelSerializer):
    contents = serializers.SerializerMethodField()

    @classmethod
    def get_contents(cls, obj):
        return HTMLController.unescape(obj.contents)

    class Meta:
        model = MailTemplate
        fields = ('id', 'title', 'remarks', 'application', 'is_active', 'is_default', 'contents')


class MailTemplateCreateSerializer(serializers.ModelSerializer):
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
        model = MailTemplate
        fields = ('title', 'remarks', 'application', 'is_active', 'contents')


class MailTemplateUpdateSerializer(serializers.ModelSerializer):
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
        model = MailTemplate
        fields = ('title', 'remarks', 'application', 'is_active', 'is_default', 'contents')


class MailTemplateSystemDetailSerializer(serializers.ModelSerializer):
    contents = serializers.SerializerMethodField()

    @classmethod
    def get_contents(cls, obj):
        return HTMLController.unescape(obj.contents)

    class Meta:
        model = MailTemplateSystem
        fields = ('id', 'system_code', 'contents', 'is_active')


class MailTemplateSystemUpdateSerializer(serializers.ModelSerializer):
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
        model = MailTemplateSystem
        fields = ('contents', 'is_active')
