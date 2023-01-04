from rest_framework import serializers
from apps.core.tenant.models import Company, Tenant


# Group Level Serializer
class CompanyListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Company
        fields = (
            'title',
            'code',
            'tenant_id',
            'date_created',
            'representative_fullname'
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
