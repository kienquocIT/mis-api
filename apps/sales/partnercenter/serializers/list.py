from rest_framework import serializers

from apps.sales.partnercenter.models import List
from apps.shared import AbstractCreateSerializerModel


class ListCreateSerializer(AbstractCreateSerializerModel):
    filter_condition = serializers.JSONField()

    class Meta:
        model = List
        fields = (
            'title',
            'data_object',
            'filter_condition'
        )

