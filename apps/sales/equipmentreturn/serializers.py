from rest_framework import serializers
from apps.core.workflow.tasks import decorator_run_workflow
from apps.sales.equipmentloan.models import EquipmentLoan
from apps.sales.equipmentreturn.models import (
    EquipmentReturn
)
from apps.shared import (
    AbstractListSerializerModel, AbstractCreateSerializerModel, AbstractDetailSerializerModel
)


__all__ = [
    'EquipmentReturnListSerializer',
    'EquipmentReturnCreateSerializer',
    'EquipmentReturnDetailSerializer',
    'EquipmentReturnUpdateSerializer',
    'EREquipmentLoanListByAccountSerializer',
]

# main
class EquipmentReturnListSerializer(AbstractListSerializerModel):
    employee_created = serializers.SerializerMethodField()

    class Meta:
        model = EquipmentReturn
        fields = (
            'id',
            'title',
            'code',
            'account_mapped_data',
            'date_created',
            'employee_created',
        )

    @classmethod
    def get_employee_created(cls, obj):
        return {
            'id': obj.employee_created_id,
            'code': obj.employee_created.code,
            'full_name': obj.employee_created.get_full_name(2),
            'group': {
                'id': obj.employee_created.group_id,
                'title': obj.employee_created.group.title,
                'code': obj.employee_created.group.code
            } if obj.employee_created.group else {}
        } if obj.employee_created else {}


class EquipmentReturnCreateSerializer(AbstractCreateSerializerModel):
    title = serializers.CharField(max_length=100)

    class Meta:
        model = EquipmentReturn
        fields = (
            'title',
        )

    @decorator_run_workflow
    def create(self, validated_data):
        er_obj = EquipmentReturn.objects.create(**validated_data)
        return er_obj


class EquipmentReturnDetailSerializer(AbstractDetailSerializerModel):

    class Meta:
        model = EquipmentReturn
        fields = (
            'id',
            'code',
            'title',
        )


class EquipmentReturnUpdateSerializer(AbstractCreateSerializerModel):
    title = serializers.CharField(max_length=100)

    class Meta:
        model = EquipmentReturn
        fields = (
            'title',
        )

    @decorator_run_workflow
    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()

        return instance

# related
class EREquipmentLoanListByAccountSerializer(serializers.ModelSerializer):
    equipment_loan_item_list = serializers.SerializerMethodField()

    class Meta:
        model = EquipmentLoan
        fields = (
            'id',
            'title',
            'code',
            'loan_date',
            'equipment_loan_item_list'
        )

    @classmethod
    def get_equipment_loan_item_list(cls, obj):
        equipment_loan_item_list = []
        for item in obj.equipment_loan_items.all():
            equipment_loan_item_list.append({
                'id': item.id,
                'loan_product_data': item.loan_product_data,
                'loan_product_none_detail': [{
                    'product_warehouse_id': child.loan_product_pw_id,
                    'picked_quantity': child.loan_product_pw_quantity
                } for child in item.equipment_loan_item_detail.filter(loan_product_pw__isnull=False)],
                'loan_product_lot_detail': [{
                    'lot_id': child.loan_product_pw_lot_id,
                    'picked_quantity': child.loan_product_pw_lot_quantity
                } for child in item.equipment_loan_item_detail.filter(loan_product_pw_lot__isnull=False)],
                'loan_product_sn_detail': item.equipment_loan_item_detail.filter(
                    loan_product_pw_serial__isnull=False
                ).values_list('loan_product_pw_serial_id', flat=True),
                'loan_quantity': item.loan_quantity,
            })
        return equipment_loan_item_list
