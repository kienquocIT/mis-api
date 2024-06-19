from rest_framework import serializers

from apps.core.hr.models import DistributionApplication


class AllApplicationOfEmployeeSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()

    @classmethod
    def get_id(cls, obj):
        return obj.app.id

    title = serializers.SerializerMethodField()

    @classmethod
    def get_title(cls, obj):
        return obj.app.title

    code = serializers.SerializerMethodField()

    @classmethod
    def get_code(cls, obj):
        return obj.app.code

    permit_mapping = serializers.SerializerMethodField()

    @classmethod
    def get_permit_mapping(cls, obj):
        return obj.app.permit_mapping

    spacing_allow = serializers.SerializerMethodField()

    @classmethod
    def get_spacing_allow(cls, obj):
        return obj.app.spacing_allow

    class Meta:
        model = DistributionApplication
        fields = ('id', 'title', 'code', 'permit_mapping', 'spacing_allow',)


class AppParsedDetailSerializer(serializers.Serializer):  # noqa
    id = serializers.UUIDField()
    title = serializers.CharField()
    code = serializers.CharField()


class SummaryApplicationOfEmployeeSerializer(serializers.Serializer):  # noqa
    employee = AppParsedDetailSerializer(many=True)
    roles = AppParsedDetailSerializer(many=True)
    summary = AppParsedDetailSerializer(many=True)
