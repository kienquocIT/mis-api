from rest_framework import serializers
from apps.core.company.models import Company


class CompanyListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = (
            'title',
            'code',
            'date_created',
            'representative_fullname'
        )


class CompanyCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = (
            'title',
            'code',
            'representative_fullname',
            'address',
            'email',
            'phone',
        )
