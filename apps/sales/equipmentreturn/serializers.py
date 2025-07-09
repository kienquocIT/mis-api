from rest_framework import serializers
from apps.core.workflow.tasks import decorator_run_workflow
from apps.masterdata.saledata.models import Account, WareHouse
from apps.sales.equipmentloan.models import EquipmentLoan, EquipmentLoanItem, EquipmentLoanItemDetail
from apps.sales.equipmentreturn.models import (
    EquipmentReturn, EquipmentReturnItem, EquipmentReturnItemDetail
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
    account_mapped = serializers.UUIDField()
    equipment_return_item_list = serializers.JSONField(default=list)
    warehouse_return_list = serializers.JSONField(default=list)

    class Meta:
        model = EquipmentReturn
        fields = (
            'title',
            'account_mapped',
            'document_date',
            'equipment_return_item_list',
            'warehouse_return_list'
        )

    @classmethod
    def validate_account_mapped(cls, value):
        try:
            return Account.objects.get(id=value)
        except Account.DoesNotExist:
            raise serializers.ValidationError({'account_mapped': "Account does not exist."})

    @classmethod
    def validate_equipment_return_item_list(cls, equipment_return_item_list):
        for item in equipment_return_item_list:
            loan_item_obj = EquipmentLoanItem.objects.filter(id=item.get('loan_item_id')).first()
            if not loan_item_obj:
                raise serializers.ValidationError({'loan_item_mapped': "Loan item does not exist."})
            item['loan_item_mapped_id'] = str(item.get('loan_item_id'))
            item['return_product_id'] = str(loan_item_obj.loan_product_id)
            item['return_product_data'] = loan_item_obj.loan_product_data

            for lot_return in item.get('lot_return_list', []):
                loan_item_detail_obj = EquipmentLoanItemDetail.objects.filter(
                    id=lot_return.get('loan_item_detail_id')
                ).first()
                if not loan_item_detail_obj:
                    raise serializers.ValidationError({'loan_item_detail_mapped': "Loan item detail does not exist."})
                loan_remain_quantity = (loan_item_detail_obj.loan_product_pw_lot_quantity -
                                        loan_item_detail_obj.lot_returned_quantity)
                if loan_remain_quantity < float(lot_return.get('picked_quantity', 0)):
                    raise serializers.ValidationError({'err': "Return quantity > remain quantity."})
                lot_return['return_product_pw_lot_id'] = str(loan_item_detail_obj.loan_product_pw_lot_id)
                lot_return['return_product_pw_lot_data'] = loan_item_detail_obj.loan_product_pw_lot_data
                lot_return['loan_item_detail_mapped_id'] = lot_return.get('loan_item_detail_id')

            for serial_return in item.get('serial_return_list', []):
                loan_item_detail_obj = EquipmentLoanItemDetail.objects.filter(
                    id=serial_return.get('loan_item_detail_id')
                ).first()
                if not loan_item_detail_obj:
                    raise serializers.ValidationError({'loan_item_detail_mapped': "Loan item detail does not exist."})
                if loan_item_detail_obj.is_returned_serial is True:
                    raise serializers.ValidationError({'err': "This serial has been returned."})
                serial_return['return_product_pw_serial_id'] = str(loan_item_detail_obj.loan_product_pw_serial_id)
                serial_return['return_product_pw_serial_data'] = loan_item_detail_obj.loan_product_pw_serial_data
                serial_return['loan_item_detail_mapped_id'] = serial_return.get('loan_item_detail_id')
        return equipment_return_item_list

    @classmethod
    def validate_warehouse_return_list(cls, warehouse_return_list):
        warehouse_return_list_parsed = []
        for item in warehouse_return_list:
            warehouse_obj = WareHouse.objects.filter(id=item).first()
            if not warehouse_obj:
                raise serializers.ValidationError({'return_to_warehouse': "Warehouse does not exist."})
            warehouse_return_list_parsed.append({
                'return_to_warehouse_id': item,
                'return_to_warehouse_data': {
                    'id': str(warehouse_obj.id),
                    'code': warehouse_obj.code,
                    'title': warehouse_obj.title,
                }
            })
        return warehouse_return_list_parsed

    def validate(self, validate_data):
        len_equipment_return_item_list = len(validate_data.get('equipment_return_item_list', []))
        len_warehouse_return_list = len(validate_data.get('warehouse_return_list', []))
        if len_equipment_return_item_list != len_warehouse_return_list:
            raise serializers.ValidationError({'err': "Missing data in line detail table."})

        # kiểm tra cấu hình kho ảo cho mượn hàng
        if not WareHouse.objects.filter_on_company(use_for=1).exists():
            raise serializers.ValidationError({
                'virtual_warehouse': "The virtual warehouse for Equipment Loan has not configured."
            })

        if 'account_mapped' in validate_data:
            account_mapped = validate_data.get('account_mapped')
            validate_data['account_mapped_data'] = {
                'id': str(account_mapped.id),
                'code': account_mapped.code,
                'name': account_mapped.name,
                'tax_code': account_mapped.tax_code,
            }
        return validate_data

    @decorator_run_workflow
    def create(self, validated_data):
        equipment_return_item_list = validated_data.pop('equipment_return_item_list', [])
        warehouse_return_list = validated_data.pop('warehouse_return_list', [])

        er_obj = EquipmentReturn.objects.create(**validated_data)

        EquipmentReturnCommonFunction.create_equipment_return_item(
            er_obj, equipment_return_item_list, warehouse_return_list
        )
        return er_obj


class EquipmentReturnDetailSerializer(AbstractDetailSerializerModel):
    equipment_return_item_list = serializers.SerializerMethodField()

    class Meta:
        model = EquipmentReturn
        fields = (
            'id',
            'code',
            'title',
            'account_mapped_data',
            'date_created',
            'document_date',
            'equipment_return_item_list',
        )

    @classmethod
    def get_equipment_return_item_list(cls, obj):
        equipment_return_item_list = []
        for item in obj.equipment_return_items.all():
            equipment_return_item_list.append({
                'id': item.id,
                'data_product': item.return_product_data,
                'return_quantity': item.return_quantity,
                'lot_return_list': [{
                    'lot_number': child.return_product_pw_lot_data.get(
                        'lot_number'
                    ) if child.return_product_pw_lot_data else '',
                    'picked_quantity': child.return_product_pw_lot_quantity,
                    'loan_item_detail_id': child.loan_item_detail_mapped_id
                } for child in item.equipment_return_item_detail.filter(return_product_pw_lot__isnull=False)],
                'serial_return_list': [{
                    'serial_number': child.return_product_pw_serial_data.get(
                        'serial_number'
                    ) if child.return_product_pw_serial_data else '',
                    'loan_item_detail_id': child.loan_item_detail_mapped_id
                } for child in item.equipment_return_item_detail.filter(return_product_pw_serial__isnull=False)],
                'loan_item_id': item.loan_item_mapped_id,
                'return_to_warehouse_data': item.return_to_warehouse_data,
            })
        return equipment_return_item_list


class EquipmentReturnUpdateSerializer(AbstractCreateSerializerModel):
    title = serializers.CharField(max_length=100)
    account_mapped = serializers.UUIDField()
    equipment_return_item_list = serializers.JSONField(default=list)
    warehouse_return_list = serializers.JSONField(default=list)

    class Meta:
        model = EquipmentReturn
        fields = (
            'title',
            'account_mapped',
            'document_date',
            'equipment_return_item_list',
            'warehouse_return_list'
        )

    @classmethod
    def validate_account_mapped(cls, value):
        return EquipmentReturnCreateSerializer.validate_account_mapped(value)

    @classmethod
    def validate_equipment_return_item_list(cls, equipment_return_item_list):
        return EquipmentReturnCreateSerializer.validate_equipment_return_item_list(equipment_return_item_list)

    @classmethod
    def validate_warehouse_return_list(cls, warehouse_return_list):
        return EquipmentReturnCreateSerializer.validate_warehouse_return_list(warehouse_return_list)

    def validate(self, validate_data):
        return EquipmentReturnCreateSerializer().validate(validate_data)

    @decorator_run_workflow
    def update(self, instance, validated_data):
        equipment_return_item_list = validated_data.pop('equipment_return_item_list', [])
        warehouse_return_list = validated_data.pop('warehouse_return_list', [])

        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()

        EquipmentReturnCommonFunction.create_equipment_return_item(
            instance, equipment_return_item_list, warehouse_return_list
        )

        return instance


class EquipmentReturnCommonFunction:
    @staticmethod
    def create_equipment_return_item_sub(equipment_return_item_obj, lot_return_list, serial_return_list):
        bulk_info_detail_sub = []
        # lot
        for child in lot_return_list:
            if float(child.get('picked_quantity', 0)) > 0:
                bulk_info_detail_sub.append(
                    EquipmentReturnItemDetail(
                        equipment_return_item=equipment_return_item_obj,
                        return_product_pw_lot_id=child.get('return_product_pw_lot_id'),
                        return_product_pw_lot_data=child.get('return_product_pw_lot_data', {}),
                        return_product_pw_lot_quantity=child.get('picked_quantity', 0),
                        loan_item_detail_mapped_id=child.get('loan_item_detail_mapped_id'),
                    )
                )
        # sn
        for child in serial_return_list:
            bulk_info_detail_sub.append(
                EquipmentReturnItemDetail(
                    equipment_return_item=equipment_return_item_obj,
                    return_product_pw_serial_id=child.get('return_product_pw_serial_id'),
                    return_product_pw_serial_data=child.get('return_product_pw_serial_data'),
                    loan_item_detail_mapped_id=child.get('loan_item_detail_mapped_id'),
                )
            )
        return bulk_info_detail_sub

    @staticmethod
    def create_equipment_return_item(er_obj, equipment_return_item_list, warehouse_return_list):
        bulk_info = []
        bulk_info_detail = []
        for order, item in enumerate(equipment_return_item_list):
            if float(item.get('return_quantity', 0)) > 0:
                equipment_return_item_obj = EquipmentReturnItem(
                    equipment_return=er_obj,
                    order=order,
                    loan_item_mapped_id=item.get('loan_item_mapped_id'),
                    return_product_id=item.get('return_product_id'),
                    return_product_data=item.get('return_product_data', {}),
                    return_quantity=item.get('return_quantity', 0),
                    return_to_warehouse_id=warehouse_return_list[order].get('return_to_warehouse_id'),
                    return_to_warehouse_data=warehouse_return_list[order].get('return_to_warehouse_data'),
                )
                bulk_info.append(equipment_return_item_obj)
                bulk_info_detail += EquipmentReturnCommonFunction.create_equipment_return_item_sub(
                    equipment_return_item_obj, item.get('lot_return_list', []), item.get('serial_return_list', [])
                )

        EquipmentReturnItem.objects.filter(equipment_return=er_obj).delete()
        EquipmentReturnItem.objects.bulk_create(bulk_info)
        EquipmentReturnItemDetail.objects.bulk_create(bulk_info_detail)
        return True

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
                'loan_quantity': item.loan_quantity,
                'sum_returned_quantity': item.sum_returned_quantity,
                'loan_product_lot_detail': [{
                    'id': child.id,
                    'lot_id': child.loan_product_pw_lot_id,
                    'lot_data': child.loan_product_pw_lot_data,
                    'picked_quantity': child.loan_product_pw_lot_quantity,
                    'lot_returned_quantity': child.lot_returned_quantity,
                } for child in item.equipment_loan_item_detail.filter(loan_product_pw_lot__isnull=False)],
                'loan_product_sn_detail': [{
                    'id': child.id,
                    'serial_id': child.loan_product_pw_serial_id,
                    'serial_data': child.loan_product_pw_serial_data,
                    'is_returned_serial': child.is_returned_serial,
                } for child in item.equipment_loan_item_detail.filter(loan_product_pw_serial__isnull=False)],
            })
        return equipment_loan_item_list
