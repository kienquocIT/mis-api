from rest_framework import serializers
from apps.core.workflow.tasks import decorator_run_workflow
from apps.masterdata.saledata.models import Account, WareHouse, ProductWareHouse
from apps.sales.equipmentloan.models import EquipmentLoan, EquipmentLoanItem, EquipmentLoanItemDetail
from apps.sales.equipmentreturn.models import (
    EquipmentReturn, EquipmentReturnItem,
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
    none_loan_items_detail = serializers.JSONField(default=list)
    lot_loan_items_detail = serializers.JSONField(default=list)
    serial_loan_items_detail = serializers.JSONField(default=list)

    class Meta:
        model = EquipmentReturn
        fields = (
            'title',
            'account_mapped',
            'document_date',
            'none_loan_items_detail',
            'lot_loan_items_detail',
            'serial_loan_items_detail'
        )

    @classmethod
    def validate_account_mapped(cls, value):
        try:
            return Account.objects.get(id=value)
        except Account.DoesNotExist:
            raise serializers.ValidationError({'account_mapped': "Account does not exist."})

    @classmethod
    def validate_none_loan_items_detail(cls, none_loan_items_detail):
        # kiểm tra cấu hình kho ảo cho mượn hàng
        virtual_warehouse_obj = WareHouse.objects.filter_on_company(use_for=1).first()
        if not virtual_warehouse_obj:
            raise serializers.ValidationError({'err': "Can not found virtual warehouse for Equipment Return."})

        for item in none_loan_items_detail:
            loan_item_detail_obj = EquipmentLoanItemDetail.objects.filter(
                id=item.get('loan_item_detail_mapped_id')).first()
            if not loan_item_detail_obj:
                raise serializers.ValidationError({'loan_item_detail_mapped': "Loan item detail does not exist."})
            item['loan_item_mapped_detail_id'] = str(item.get('loan_item_detail_mapped_id'))
            item['return_product_id'] = item.get('data_product', {}).get('id')
            item['return_product_data'] = item.get('data_product', {})

            prd_wh_obj = virtual_warehouse_obj.product_warehouse_warehouse.filter(
                product_id=item.get('data_product', {}).get('id')
            ).first()
            if not prd_wh_obj:
                raise serializers.ValidationError({'err': "Can not found this product in virtual warehouse."})

            item['return_product_pw_id'] = str(prd_wh_obj.id)

            before_warehouse_obj = WareHouse.objects.filter_on_company(id=item.get('warehouse_before_id')).first()
            if not before_warehouse_obj:
                raise serializers.ValidationError({'err': "Can not found before warehouse."})
            item['before_warehouse_id'] = str(before_warehouse_obj.id)
            item['before_warehouse_data'] = {
                'id': str(before_warehouse_obj.id),
                'code': before_warehouse_obj.code,
                'title': before_warehouse_obj.title,
            }

            return_to_warehouse_obj = WareHouse.objects.filter_on_company(id=item.get('return_to_warehouse')).first()
            if not return_to_warehouse_obj:
                raise serializers.ValidationError({'err': "Can not found return to warehouse."})
            item['return_to_warehouse_id'] = str(return_to_warehouse_obj.id)
            item['return_to_warehouse_data'] = {
                'id': str(return_to_warehouse_obj.id),
                'code': return_to_warehouse_obj.code,
                'title': return_to_warehouse_obj.title,
            }

        return none_loan_items_detail

    @classmethod
    def validate_lot_loan_items_detail(cls, lot_loan_items_detail):
        # kiểm tra cấu hình kho ảo cho mượn hàng
        virtual_warehouse_obj = WareHouse.objects.filter_on_company(use_for=1).first()
        if not virtual_warehouse_obj:
            raise serializers.ValidationError({'err': "Can not found virtual warehouse for Equipment Return."})

        for item in lot_loan_items_detail:
            loan_item_detail_obj = EquipmentLoanItemDetail.objects.filter(
                id=item.get('loan_item_detail_mapped_id')).first()
            if not loan_item_detail_obj:
                raise serializers.ValidationError({'loan_item_detail_mapped': "Loan item detail does not exist."})
            item['loan_item_mapped_detail_id'] = str(item.get('loan_item_detail_mapped_id'))
            item['return_product_id'] = item.get('data_product', {}).get('id')
            item['return_product_data'] = item.get('data_product', {})

            prd_wh_obj = virtual_warehouse_obj.product_warehouse_warehouse.filter(
                product_id=item.get('data_product', {}).get('id')
            ).first()
            if not prd_wh_obj:
                raise serializers.ValidationError({'err': "Can not found this product in virtual warehouse."})

            prd_wh_lot_obj = prd_wh_obj.product_warehouse_lot_product_warehouse.filter(
                lot_number=item.get('lot_number')
            ).first()
            if not prd_wh_lot_obj:
                raise serializers.ValidationError({'err': "Can not found this lot in virtual warehouse."})
            item['return_product_pw_lot_id'] = str(prd_wh_lot_obj.id)
            item['return_product_pw_lot_data'] = loan_item_detail_obj.loan_product_pw_lot_data

            before_warehouse_obj = WareHouse.objects.filter_on_company(id=item.get('warehouse_before_id')).first()
            if not before_warehouse_obj:
                raise serializers.ValidationError({'err': "Can not found before warehouse."})
            item['before_warehouse_id'] = str(before_warehouse_obj.id)
            item['before_warehouse_data'] = {
                'id': str(before_warehouse_obj.id),
                'code': before_warehouse_obj.code,
                'title': before_warehouse_obj.title,
            }

            return_to_warehouse_obj = WareHouse.objects.filter_on_company(id=item.get('return_to_warehouse')).first()
            if not return_to_warehouse_obj:
                raise serializers.ValidationError({'err': "Can not found return to warehouse."})
            item['return_to_warehouse_id'] = str(return_to_warehouse_obj.id)
            item['return_to_warehouse_data'] = {
                'id': str(return_to_warehouse_obj.id),
                'code': return_to_warehouse_obj.code,
                'title': return_to_warehouse_obj.title,
            }

        return lot_loan_items_detail

    @classmethod
    def validate_serial_loan_items_detail(cls, serial_loan_items_detail):
        # kiểm tra cấu hình kho ảo cho mượn hàng
        virtual_warehouse_obj = WareHouse.objects.filter_on_company(use_for=1).first()
        if not virtual_warehouse_obj:
            raise serializers.ValidationError({'err': "Can not found virtual warehouse for Equipment Return."})

        for item in serial_loan_items_detail:
            loan_item_detail_obj = EquipmentLoanItemDetail.objects.filter(
                id=item.get('loan_item_detail_mapped_id')).first()
            if not loan_item_detail_obj:
                raise serializers.ValidationError({'loan_item_detail_mapped': "Loan item detail does not exist."})
            item['loan_item_mapped_detail_id'] = str(item.get('loan_item_detail_mapped_id'))
            item['return_product_id'] = item.get('data_product', {}).get('id')
            item['return_product_data'] = item.get('data_product', {})

            prd_wh_obj = virtual_warehouse_obj.product_warehouse_warehouse.filter(
                product_id=item.get('data_product', {}).get('id')
            ).first()
            if not prd_wh_obj:
                raise serializers.ValidationError({'err': "Can not found this product in virtual warehouse."})

            prd_wh_sn_obj = prd_wh_obj.product_warehouse_serial_product_warehouse.filter(
                serial_number=item.get('serial_number')
            ).first()
            if not prd_wh_sn_obj:
                raise serializers.ValidationError({'err': "Can not found this serial in virtual warehouse."})
            item['return_product_pw_serial_id'] = str(prd_wh_sn_obj.id)
            item['return_product_pw_serial_data'] = loan_item_detail_obj.loan_product_pw_serial_data

            before_warehouse_obj = WareHouse.objects.filter_on_company(id=item.get('warehouse_before_id')).first()
            if not before_warehouse_obj:
                raise serializers.ValidationError({'err': "Can not found before warehouse."})
            item['before_warehouse_id'] = str(before_warehouse_obj.id)
            item['before_warehouse_data'] = {
                'id': str(before_warehouse_obj.id),
                'code': before_warehouse_obj.code,
                'title': before_warehouse_obj.title,
            }

            return_to_warehouse_obj = WareHouse.objects.filter_on_company(id=item.get('return_to_warehouse')).first()
            if not return_to_warehouse_obj:
                raise serializers.ValidationError({'err': "Can not found return to warehouse."})
            item['return_to_warehouse_id'] = str(return_to_warehouse_obj.id)
            item['return_to_warehouse_data'] = {
                'id': str(return_to_warehouse_obj.id),
                'code': return_to_warehouse_obj.code,
                'title': return_to_warehouse_obj.title,
            }

        return serial_loan_items_detail

    def validate(self, validate_data):
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
        none_loan_items_detail = validated_data.get('none_loan_items_detail', [])
        lot_loan_items_detail = validated_data.get('lot_loan_items_detail', [])
        serial_loan_items_detail = validated_data.get('serial_loan_items_detail', [])
        equipment_return_item_list = none_loan_items_detail + lot_loan_items_detail + serial_loan_items_detail

        er_obj = EquipmentReturn.objects.create(**validated_data)

        EquipmentReturnCommonFunction.create_equipment_return_item(er_obj, equipment_return_item_list)
        return er_obj


class EquipmentReturnDetailSerializer(AbstractDetailSerializerModel):
    class Meta:
        model = EquipmentReturn
        fields = (
            'id',
            'code',
            'title',
            'account_mapped_data',
            'date_created',
            'document_date',
            'none_loan_items_detail',
            'lot_loan_items_detail',
            'serial_loan_items_detail',
        )


class EquipmentReturnUpdateSerializer(AbstractCreateSerializerModel):
    title = serializers.CharField(max_length=100)
    account_mapped = serializers.UUIDField()
    none_loan_items_detail = serializers.JSONField(default=list)
    lot_loan_items_detail = serializers.JSONField(default=list)
    serial_loan_items_detail = serializers.JSONField(default=list)

    class Meta:
        model = EquipmentReturn
        fields = (
            'title',
            'account_mapped',
            'document_date',
            'none_loan_items_detail',
            'lot_loan_items_detail',
            'serial_loan_items_detail'
        )

    @classmethod
    def validate_account_mapped(cls, value):
        return EquipmentReturnCreateSerializer.validate_account_mapped(value)

    @classmethod
    def validate_none_loan_items_detail(cls, none_loan_items_detail):
        return EquipmentReturnCreateSerializer.validate_none_loan_items_detail(none_loan_items_detail)

    @classmethod
    def validate_lot_loan_items_detail(cls, lot_loan_items_detail):
        return EquipmentReturnCreateSerializer.validate_none_loan_items_detail(lot_loan_items_detail)

    @classmethod
    def validate_serial_loan_items_detail(cls, serial_loan_items_detail):
        return EquipmentReturnCreateSerializer.validate_none_loan_items_detail(serial_loan_items_detail)

    def validate(self, validate_data):
        return EquipmentReturnCreateSerializer().validate(validate_data)

    @decorator_run_workflow
    def update(self, instance, validated_data):
        none_loan_items_detail = validated_data.get('none_loan_items_detail', [])
        lot_loan_items_detail = validated_data.get('lot_loan_items_detail', [])
        serial_loan_items_detail = validated_data.get('serial_loan_items_detail', [])
        equipment_return_item_list = none_loan_items_detail + lot_loan_items_detail + serial_loan_items_detail

        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()

        EquipmentReturnCommonFunction.create_equipment_return_item(instance, equipment_return_item_list)

        return instance


class EquipmentReturnCommonFunction:
    @staticmethod
    def create_equipment_return_item(er_obj, equipment_return_item_list):
        bulk_info = []
        for order, item in enumerate(equipment_return_item_list):
            equipment_return_item_obj = EquipmentReturnItem(
                equipment_return=er_obj,
                order=order,
                return_product_id=item.get('return_product_id'),
                return_product_data=item.get('return_product_data', {}),
                return_product_pw_id=item.get('return_product_pw_id'),
                return_product_pw_quantity=item.get('return_product_pw_quantity', 0),
                return_product_pw_lot_id=item.get('return_product_pw_lot_id'),
                return_product_pw_lot_data=item.get('return_product_pw_lot_data', {}),
                return_product_pw_lot_quantity=item.get('return_product_pw_lot_quantity', 0),
                return_product_pw_serial_id=item.get('return_product_pw_serial_id'),
                return_product_pw_serial_data=item.get('return_product_pw_serial_data', {}),
                before_warehouse_id=item.get('before_warehouse_id'),
                before_warehouse_data=item.get('before_warehouse_data', {}),
                return_to_warehouse_id=item.get('return_to_warehouse_id'),
                return_to_warehouse_data=item.get('return_to_warehouse_data', {}),
                loan_item_detail_mapped_id=item.get('loan_item_detail_mapped_id'),
            )
            bulk_info.append(equipment_return_item_obj)

        EquipmentReturnItem.objects.filter(equipment_return=er_obj).delete()
        EquipmentReturnItem.objects.bulk_create(bulk_info)
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
                'loan_product_none_detail': [{
                    'id': child.id,
                    'product_warehouse_id': child.loan_product_pw_id,
                    'warehouse_data': child.loan_product_pw.warehouse_data,
                    'picked_quantity': child.loan_product_pw_quantity,
                    'returned_quantity': child.returned_quantity,
                } for child in item.equipment_loan_item_detail.filter(loan_product_pw__isnull=False)],
                'loan_product_lot_detail': [{
                    'id': child.id,
                    'warehouse_data': child.loan_product_pw_lot.product_warehouse.warehouse_data,
                    'lot_id': child.loan_product_pw_lot_id,
                    'lot_data': child.loan_product_pw_lot_data,
                    'picked_quantity': child.loan_product_pw_lot_quantity,
                    'lot_returned_quantity': child.lot_returned_quantity,
                } for child in item.equipment_loan_item_detail.filter(loan_product_pw_lot__isnull=False)],
                'loan_product_sn_detail': [{
                    'id': child.id,
                    'warehouse_data': child.loan_product_pw_serial.product_warehouse.warehouse_data,
                    'serial_id': child.loan_product_pw_serial_id,
                    'serial_data': child.loan_product_pw_serial_data,
                    'is_returned_serial': child.is_returned_serial,
                } for child in item.equipment_loan_item_detail.filter(loan_product_pw_serial__isnull=False)],
            })
        return equipment_loan_item_list
