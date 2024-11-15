from rest_framework import serializers

from apps.core.hr.models import Employee
from apps.masterdata.saledata.models.bidding_result_config import (
    BiddingResultConfig, BiddingResultConfigEmployee
)

class BiddingResultConfigListSerializer(serializers.ModelSerializer):
    employee = serializers.SerializerMethodField()

    class Meta:
        model = BiddingResultConfig
        fields = ('id', 'employee')

    @classmethod
    def get_employee(cls, obj):
        return [{
            'id': item.employee.id,
            'full_name': item.employee.get_full_name(),
        } for item in obj.bidding_result_config_employee_bid_config.all()]


class BiddingResultConfigCreateSerializer(serializers.ModelSerializer):
    employee = serializers.ListField(child=serializers.CharField())

    class Meta:
        model = BiddingResultConfig
        fields = (
            'employee',
        )

    @classmethod
    def validate_employee(cls, value):
        for item in value:
            try:
                Employee.objects.get(id=item).exists()
            except Employee.DoesNotExist:
                raise serializers.ValidationError({"employee": "Employee does not exist"})
        return value

    def create(self, validated_data):
        config = BiddingResultConfig.objects.create(**validated_data)
        bulk_info = []
        for employee in validated_data.get('employee', []):
            bulk_info.append(BiddingResultConfigEmployee(bidding_result_config=config, employee_id=employee))
        BiddingResultConfig.objects.filter(company=config.company).exclude(id=config.id).delete()
        BiddingResultConfigEmployee.objects.bulk_create(bulk_info)
        return config


class BiddingResultConfigDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = BiddingResultConfig
        fields = ('id',)
