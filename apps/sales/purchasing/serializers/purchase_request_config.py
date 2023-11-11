from rest_framework import serializers

from apps.core.hr.models import Employee
from apps.sales.purchasing.models import PurchaseRequestConfig, EmployeeReferenceEntireSaleOrder
from apps.shared import PurchaseRequestMsg

__all__ = ['PurchaseRequestConfigDetailSerializer', 'PurchaseRequestConfigUpdateSerializer']


class EmployeeReferenceSerializer(serializers.Serializer):  # noqa
    employee = serializers.UUIDField()

    @classmethod
    def validate_employee(cls, value):
        try:
            emp = Employee.objects.get_current(
                fill__tenant=True,
                fill__company=True,
                id=value
            )
            return {
                'id': str(emp.id),
                'full_name': emp.get_full_name()
            }
        except Employee.DoesNotExist:
            raise serializers.ValidationError({'employee': PurchaseRequestMsg.EMPLOYEE_DOES_NOT_EXIST})


class PurchaseRequestConfigDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = PurchaseRequestConfig
        fields = (
            'employee_reference',
        )


class PurchaseRequestConfigUpdateSerializer(serializers.ModelSerializer):
    employee_reference = serializers.ListField(child=EmployeeReferenceSerializer())

    class Meta:
        model = PurchaseRequestConfig
        fields = (
            'employee_reference',
        )

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()

        EmployeeReferenceEntireSaleOrder.objects.filter(purchase_request_config=instance).delete()

        bulk_data = []
        for emp in validated_data['employee_reference']:
            bulk_data.append(
                EmployeeReferenceEntireSaleOrder(
                    employee_id=emp['employee']['id'],
                    purchase_request_config=instance
                )
            )
        EmployeeReferenceEntireSaleOrder.objects.bulk_create(bulk_data)
        return instance
