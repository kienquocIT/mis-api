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

    class Meta:
        model = DistributionApplication
        fields = ('id', 'title', 'code', 'permit_mapping')
