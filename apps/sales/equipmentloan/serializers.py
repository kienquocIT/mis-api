from rest_framework import serializers

from apps.core.base.models import Application
from apps.core.workflow.tasks import decorator_run_workflow
from apps.masterdata.saledata.models import (
    Product, ProductWareHouseLot, ProductWareHouseSerial, ProductWareHouse, Account, WareHouse
)
from apps.sales.equipmentloan.models import (
    EquipmentLoan, EquipmentLoanItemDetail, EquipmentLoanItem, EquipmentLoanAttachmentFile
)
from apps.shared import (
    AbstractListSerializerModel, AbstractCreateSerializerModel, AbstractDetailSerializerModel,
    SerializerCommonHandle, SerializerCommonValidate
)


__all__ = [
    'EquipmentLoanListSerializer',
    'EquipmentLoanCreateSerializer',
    'EquipmentLoanDetailSerializer',
    'EquipmentLoanUpdateSerializer',
    'ELProductListSerializer',
    'ELWarehouseListByProductSerializer',
    'ELProductLotListSerializer',
    'ELProductSerialListSerializer',
]

# main
class EquipmentLoanListSerializer(AbstractListSerializerModel):
    employee_created = serializers.SerializerMethodField()

    class Meta:
        model = EquipmentLoan
        fields = (
            'id',
            'title',
            'code',
            'account_mapped_data',
            'date_created',
            'loan_date',
            'return_date',
            'return_status',
            'employee_created',
            'product_loan_data'
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


class EquipmentLoanCreateSerializer(AbstractCreateSerializerModel):
    title = serializers.CharField(max_length=100)
    account_mapped = serializers.UUIDField()
    equipment_loan_item_list = serializers.JSONField(default=list)
    attachment = serializers.ListSerializer(child=serializers.CharField(), required=False)

    class Meta:
        model = EquipmentLoan
        fields = (
            'title',
            'account_mapped',
            'document_date',
            'loan_date',
            'return_date',
            'equipment_loan_item_list',
            'attachment'
        )

    @classmethod
    def validate_account_mapped(cls, value):
        try:
            return Account.objects.get(id=value)
        except Account.DoesNotExist:
            raise serializers.ValidationError({'account_mapped': "Account does not exist."})

    @classmethod
    def validate_equipment_loan_item_list(cls, equipment_loan_item_list):
        for item in equipment_loan_item_list:
            if float(item.get('loan_quantity', 0)) <= 0:
                raise serializers.ValidationError({'loan_quantity': "Loan quantity must be > 0."})
            loan_product = Product.objects.filter(id=item.get('loan_product_id')).first()
            if not loan_product:
                raise serializers.ValidationError({'loan_product_id': "Loan product does not exist."})
            item['loan_product_id'] = str(loan_product.id)
            item['loan_product_data'] = {
                'id': str(loan_product.id),
                'code': loan_product.code,
                'title': loan_product.title,
                'description': loan_product.description,
                'general_traceability_method': loan_product.general_traceability_method,
            }
        return equipment_loan_item_list

    def validate_attachment(self, value):
        user = self.context.get('user', None)
        return SerializerCommonValidate.validate_attachment(
            user=user, model_cls=EquipmentLoanAttachmentFile, value=value
        )

    def validate(self, validate_data):
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
        equipment_loan_item_list = validated_data.pop('equipment_loan_item_list', [])
        attachment_list = validated_data.pop('attachment', [])

        el_obj = EquipmentLoan.objects.create(**validated_data)

        EquipmentLoanCommonFunction.create_equipment_loan_item(el_obj, equipment_loan_item_list)
        EquipmentLoanCommonFunction.create_files_mapped(el_obj, attachment_list)

        return el_obj


class EquipmentLoanDetailSerializer(AbstractDetailSerializerModel):
    equipment_loan_item_list = serializers.SerializerMethodField()
    attachment = serializers.SerializerMethodField()

    class Meta:
        model = EquipmentLoan
        fields = (
            'id',
            'code',
            'title',
            'account_mapped_data',
            'date_created',
            'document_date',
            'loan_date',
            'return_date',
            'equipment_loan_item_list',
            'attachment'
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

    @classmethod
    def get_attachment(cls, obj):
        return [item.attachment.get_detail() for item in obj.equipment_loan_attachments.all()]


class EquipmentLoanUpdateSerializer(AbstractCreateSerializerModel):
    title = serializers.CharField(max_length=100)
    account_mapped = serializers.UUIDField()
    equipment_loan_item_list = serializers.JSONField(default=list)
    attachment = serializers.ListSerializer(child=serializers.CharField(), required=False)

    class Meta:
        model = EquipmentLoan
        fields = (
            'title',
            'account_mapped',
            'document_date',
            'loan_date',
            'return_date',
            'return_date',
            'equipment_loan_item_list',
            'attachment'
        )

    @classmethod
    def validate_account_mapped(cls, value):
        return EquipmentLoanCreateSerializer.validate_account_mapped(value)

    @classmethod
    def validate_equipment_loan_item_list(cls, equipment_loan_item_list):
        return EquipmentLoanCreateSerializer.validate_equipment_loan_item_list(equipment_loan_item_list)

    def validate_attachment(self, value):
        user = self.context.get('user', None)
        return SerializerCommonValidate.validate_attachment(
            user=user, model_cls=EquipmentLoanAttachmentFile, value=value
        )

    def validate(self, validate_data):
        return EquipmentLoanCreateSerializer().validate(validate_data)

    @decorator_run_workflow
    def update(self, instance, validated_data):
        equipment_loan_item_list = validated_data.pop('equipment_loan_item_list', [])
        attachment_list = validated_data.pop('attachment', [])

        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()

        EquipmentLoanCommonFunction.create_equipment_loan_item(instance, equipment_loan_item_list)
        EquipmentLoanCommonFunction.create_files_mapped(instance, attachment_list)

        return instance


class EquipmentLoanCommonFunction:
    @staticmethod
    def create_equipment_loan_item_sub(
            equipment_loan_item_obj, loan_product_none_detail, loan_product_lot_detail, loan_product_sn_detail
    ):
        bulk_info_detail_sub = []
        # none
        for child in loan_product_none_detail:
            if float(child.get('picked_quantity', 0)) > 0:
                pw_obj = ProductWareHouse.objects.filter(id=child.get('product_warehouse_id')).first()
                if pw_obj:
                    bulk_info_detail_sub.append(
                        EquipmentLoanItemDetail(
                            equipment_loan_item=equipment_loan_item_obj,
                            loan_product_pw=pw_obj,
                            loan_product_pw_quantity=child.get('picked_quantity', 0)
                        )
                    )
        # lot
        for child in loan_product_lot_detail:
            if float(child.get('picked_quantity', 0)) > 0:
                pw_lot_obj = ProductWareHouseLot.objects.filter(id=child.get('lot_id')).first()
                if pw_lot_obj:
                    bulk_info_detail_sub.append(
                        EquipmentLoanItemDetail(
                            equipment_loan_item=equipment_loan_item_obj,
                            loan_product_pw_lot=pw_lot_obj,
                            loan_product_pw_lot_data={
                                'id': str(pw_lot_obj.id),
                                'lot_number': pw_lot_obj.lot_number,
                                'expire_date': str(pw_lot_obj.expire_date),
                                'manufacture_date': str(pw_lot_obj.manufacture_date),
                            },
                            loan_product_pw_lot_quantity=child.get('picked_quantity', 0)
                        )
                    )
        # sn
        for serial_id in loan_product_sn_detail:
            pw_serial_obj = ProductWareHouseSerial.objects.filter(id=serial_id).first()
            if pw_serial_obj:
                bulk_info_detail_sub.append(
                    EquipmentLoanItemDetail(
                        equipment_loan_item=equipment_loan_item_obj,
                        loan_product_pw_serial=pw_serial_obj,
                        loan_product_pw_serial_data={
                            'id': str(pw_serial_obj.id),
                            'vendor_serial_number': pw_serial_obj.vendor_serial_number,
                            'serial_number': pw_serial_obj.serial_number,
                            'expire_date': str(pw_serial_obj.expire_date),
                            'manufacture_date': str(pw_serial_obj.manufacture_date),
                            'warranty_start': str(pw_serial_obj.warranty_start),
                            'warranty_end': str(pw_serial_obj.warranty_end),
                        }
                    )
                )
        return bulk_info_detail_sub

    @staticmethod
    def create_equipment_loan_item(el_obj, equipment_loan_item_list):
        bulk_info = []
        bulk_info_detail = []
        product_loan_data = []
        for order, equipment_loan_item in enumerate(equipment_loan_item_list):
            loan_product_none_detail = equipment_loan_item.pop('loan_product_none_detail', [])
            loan_product_lot_detail = equipment_loan_item.pop('loan_product_lot_detail', [])
            loan_product_sn_detail = equipment_loan_item.pop('loan_product_sn_detail', [])

            equipment_loan_item_obj = EquipmentLoanItem(equipment_loan=el_obj, order=order, **equipment_loan_item)
            bulk_info.append(equipment_loan_item_obj)
            bulk_info_detail += EquipmentLoanCommonFunction.create_equipment_loan_item_sub(
                equipment_loan_item_obj, loan_product_none_detail, loan_product_lot_detail, loan_product_sn_detail
            )
            product_loan_data.append({
                **equipment_loan_item.get('loan_product_data', {}),
                'quantity': equipment_loan_item.get('loan_quantity', 0)
            })

        EquipmentLoanItem.objects.filter(equipment_loan=el_obj).delete()
        EquipmentLoanItem.objects.bulk_create(bulk_info)
        EquipmentLoanItemDetail.objects.bulk_create(bulk_info_detail)
        el_obj.product_loan_data = product_loan_data
        el_obj.save(update_fields=['product_loan_data'])
        return True

    @staticmethod
    def create_files_mapped(el_obj, attachment_list):
        SerializerCommonHandle.handle_attach_file(
            relate_app=Application.objects.filter(id=EquipmentLoan.get_app_id()).first(),
            model_cls=EquipmentLoanAttachmentFile,
            instance=el_obj,
            attachment_result=attachment_list,
        )
        return True

# related
class ELProductListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
            'id',
            'code',
            'title',
            'description',
            'general_traceability_method'
        )


class ELWarehouseListByProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductWareHouse
        fields = (
            'id',
            'warehouse_data',
            'stock_amount'
        )


class ELProductLotListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductWareHouseLot
        fields = (
            'id',
            'lot_number',
            'quantity_import',
            'expire_date',
            'manufacture_date'
        )


class ELProductSerialListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductWareHouseSerial
        fields = (
            'id',
            'vendor_serial_number',
            'serial_number',
            'expire_date',
            'manufacture_date',
            'warranty_start',
            'warranty_end'
        )
