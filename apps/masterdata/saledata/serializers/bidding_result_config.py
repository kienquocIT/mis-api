from rest_framework import serializers
from apps.masterdata.saledata.models.bidding_result_config import (
    BiddingResultConfig
)

class BiddingResultConfigListSerializer(serializers.ModelSerializer):
    employee = serializers.SerializerMethodField()

    class Meta:
        model = BiddingResultConfig
        fields = ('id', 'employee')

    @classmethod
    def get_employee(cls, obj):
        return {
            'id': obj.employee.id,
            'name': obj.employee.last_name + ' ' + obj.employee.first_name,
        }

class BiddingResultConfigCreateListSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        bulk_data = []
        for data in validated_data:
            bulk_data.append({
                "employee_id": data["id"]
            })
        return BiddingResultConfig.objects.bulk_create(bulk_data)

class BiddingResultConfigCreateSerializer(serializers.ModelSerializer):
    class Meta:
        list_serializer_class = BiddingResultConfigCreateListSerializer


