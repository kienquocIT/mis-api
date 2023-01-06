from rest_framework import serializers
from apps.core.company.models import Company
from apps.core.tenant.models import Tenant


# Group Level Serializer
class CompanyListSerializer(serializers.ModelSerializer):
    tenant_auto_create_company = serializers.SerializerMethodField()
    tenant_representative_fullname = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = (
            'id',
            'title',
            'code',
            'tenant_id',
            'tenant_representative_fullname',
            'date_created',
            'representative_fullname',
            'tenant_auto_create_company',
        )

    def get_tenant_representative_fullname(self, obj):
        tenant_representative_fullname = Tenant.objects.get(id=obj.tenant_id).representative_fullname
        return tenant_representative_fullname

    def get_tenant_auto_create_company(self, obj):
        tenant_auto_create_company = Tenant.objects.get(id=obj.tenant_id).auto_create_company
        return tenant_auto_create_company

    def validate_tenant_id(self, attrs):
        try:
            return Tenant.objects.get(id=attrs).id
        except Exception as e:
            raise serializers.ValidationError("Tenant does not exist.")

    def validate_is_auto_create_company(self, attrs):
        try:
            return Tenant.objects.get(id=attrs).auto_create_company
        except Exception as e:
            raise serializers.ValidationError("Tenant does not exist.")


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

    def validate_tenant(self, attrs):
        try:
            return Tenant.objects.get(id=attrs)
        except Exception as e:
            raise serializers.ValidationError("Tenant does not exist.")


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

    def validate_tenant_id(self, attrs):
        try:
            return Tenant.objects.get(id=attrs)
        except Exception as e:
            raise serializers.ValidationError("Tenant does not exist.")
