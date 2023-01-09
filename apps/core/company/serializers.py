from rest_framework import serializers
from apps.core.company.models import Company
from apps.core.tenant.models import Tenant


# Company Serializer
class CompanyListSerializer(serializers.ModelSerializer):
    tenant_auto_create_company = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = (
            'id',
            'title',
            'code',
            'tenant_id',
            'date_created',
            'representative_fullname',
            'tenant_auto_create_company',
        )

    def get_tenant_auto_create_company(self, obj):
        tenant_auto_create_company = Tenant.objects.get(id=obj.tenant_id).auto_create_company
        return tenant_auto_create_company


class CompanyDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Company
        fields = (
            'title',
            'code',
            'representative_fullname',
            'email',
            'address',
            'phone'
        )


class CompanyCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Company
        fields = (
            'title',
            'code',
            'tenant_id',
            'representative_fullname',
            'address',
            'email',
            'phone',
        )

    def validate_tenant_id(self, attrs):
        try:
            return Tenant.objects.get(id=attrs)
        except Exception as e:
            raise serializers.ValidationError("Tenant does not exist.")


class CompanyUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Company
        fields = (
            'title',
            'code',
            'tenant_id',
            'representative_fullname',
            'address',
            'email',
            'phone',
        )
