from rest_framework import serializers

from apps.core.tenant.models import Company, Tenant


# Group Level Serializer
class CompanyCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Company
        fields = (
            'title',
            'code',
            'tenant_id',
        )

    def validate_tenant(self, attrs):
        try:
            return Tenant.objects.get(id=attrs)
        except Exception as e:
            raise serializers.ValidationError("Tenant does not exist.")
