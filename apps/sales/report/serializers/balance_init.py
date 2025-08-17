from django.db import transaction
from rest_framework import serializers
from apps.masterdata.saledata.models import (
    ProductWareHouse, SubPeriods, Periods, Product, WareHouse,
    ProductWareHouseSerial, ProductWareHouseLot
)
from apps.sales.report.utils.inventory_log import ReportInvCommonFunc, ReportInvLog
from apps.sales.report.models import (
    ReportStock, ReportInventoryCost, ReportInventorySubFunction,
    BalanceInitialization, BalanceInitializationSerial, BalanceInitializationLot
)


# balance init
class BalanceInitializationListSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()
    uom = serializers.SerializerMethodField()
    warehouse = serializers.SerializerMethodField()

    class Meta:
        model = BalanceInitialization
        fields = (
            'id',
            'product',
            'uom',
            'warehouse',
            'quantity',
            'value',
            'data_sn',
            'data_lot'
        )

    @classmethod
    def get_product(cls, obj):
        return {
            'id': obj.product_id,
            'title': obj.product.title,
            'code': obj.product.code,
            'description': obj.product.description,
        } if obj.product else {}

    @classmethod
    def get_uom(cls, obj):
        return {
            'id': obj.uom_id,
            'title': obj.uom.title,
            'code': obj.uom.code,
        } if obj.uom else {}

    @classmethod
    def get_warehouse(cls, obj):
        if obj.warehouse:
            return {'id': obj.warehouse_id, 'title': obj.warehouse.title, 'code': obj.warehouse.code}
        warehouse_sub = obj.report_inventory_cost_wh.first()
        return {
            'id': warehouse_sub.warehouse.id,
            'title': warehouse_sub.warehouse.title,
            'code': warehouse_sub.warehouse.code,
        } if warehouse_sub else {}


class BalanceInitializationCreateSerializer(serializers.ModelSerializer):
    balance_init_data = serializers.JSONField(default=dict)

    class Meta:
        model = BalanceInitialization
        fields = ('balance_init_data',)

    def validate(self, validate_data):
        tenant_current = self.context.get('tenant_current')
        company_current = self.context.get('company_current')
        if not tenant_current or not company_current:
            raise serializers.ValidationError({"error": "Tenant or Company is missing."})

        balance_init_data = validate_data.get('balance_init_data', {})
        validate_data = BalanceInitCommonFunction.validate_balance_init_data(
            balance_init_data, tenant_current, company_current
        )
        return validate_data

    @classmethod
    def for_serial(cls, periods, instance, quantity, data_sn):
        if not ProductWareHouse.objects.filter(
                tenant_id=periods.tenant_id,
                company_id=periods.company_id,
                product=instance.product,
                warehouse=instance.warehouse
        ).exists():
            prd_wh_obj = ProductWareHouse.objects.create(
                tenant_id=periods.tenant_id,
                company_id=periods.company_id,
                product=instance.product,
                warehouse=instance.warehouse,
                uom=instance.product.general_uom_group.uom_reference,
                unit_price=instance.value/quantity,
                tax=None,
                stock_amount=quantity,
                receipt_amount=quantity,
                sold_amount=0,
                picked_ready=0,
                used_amount=0,
                product_data={
                    "id": str(instance.product_id),
                    "code": instance.product.code,
                    "title": instance.product.title
                },
                warehouse_data={
                    "id": str(instance.warehouse_id),
                    "code": instance.warehouse.code,
                    "title": instance.warehouse.title
                },
                uom_data={
                    "id": str(instance.product.general_uom_group.uom_reference_id),
                    "code": instance.product.general_uom_group.uom_reference.code,
                    "title": instance.product.general_uom_group.uom_reference.title
                } if instance.product.general_uom_group.uom_reference else {},
                tax_data={}
            )
            bulk_info_sn = []
            for serial in data_sn:
                for key in serial:
                    if serial[key] == '':
                        serial[key] = None
                bulk_info_sn.append(
                    ProductWareHouseSerial(
                        tenant_id=instance.tenant_id,
                        company_id=instance.company_id,
                        product_warehouse=prd_wh_obj,
                        **serial
                    )
                )
            ProductWareHouseSerial.objects.bulk_create(bulk_info_sn)
            return prd_wh_obj
        raise serializers.ValidationError({"Existed": 'This Product-Warehouse already exists.'})

    @classmethod
    def for_lot(cls, periods, instance, quantity, data_lot):
        if not ProductWareHouse.objects.filter(
                tenant_id=periods.tenant_id,
                company_id=periods.company_id,
                product=instance.product,
                warehouse=instance.warehouse
        ).exists():
            prd_wh_obj = ProductWareHouse.objects.create(
                tenant_id=periods.tenant_id,
                company_id=periods.company_id,
                product=instance.product,
                warehouse=instance.warehouse,
                uom=instance.product.general_uom_group.uom_reference,
                unit_price=instance.value/quantity,
                tax=None,
                stock_amount=quantity,
                receipt_amount=quantity,
                sold_amount=0,
                picked_ready=0,
                used_amount=0,
                product_data={
                    "id": str(instance.product_id),
                    "code": instance.product.code,
                    "title": instance.product.title
                },
                warehouse_data={
                    "id": str(instance.warehouse_id),
                    "code": instance.warehouse.code,
                    "title": instance.warehouse.title
                },
                uom_data={
                    "id": str(instance.product.general_uom_group.uom_reference_id),
                    "code": instance.product.general_uom_group.uom_reference.code,
                    "title": instance.product.general_uom_group.uom_reference.title
                } if instance.product.general_uom_group.uom_reference else {},
                tax_data={}
            )
            bulk_info_lot = []
            for lot in data_lot:
                for key in lot:
                    if lot[key] == '':
                        lot[key] = None
                bulk_info_lot.append(
                    ProductWareHouseLot(
                        tenant_id=periods.tenant_id,
                        company_id=periods.company_id,
                        product_warehouse=prd_wh_obj,
                        lot_number=lot.get('lot_number'),
                        quantity_import=ReportInvCommonFunc.cast_quantity_to_unit(
                            instance.product.inventory_uom, float(lot.get('quantity_import', 0))
                        )
                    )
                )
            ProductWareHouseLot.objects.bulk_create(bulk_info_lot)
            return prd_wh_obj
        raise serializers.ValidationError({"Existed": 'This Product-Warehouse already exists.'})

    @classmethod
    def for_none(cls, periods, instance, quantity):
        prd_wh = ProductWareHouse.objects.filter(
                tenant_id=periods.tenant_id,
                company_id=periods.company_id,
                product=instance.product,
                warehouse=instance.warehouse
        ).first()
        if not prd_wh:
            prd_wh_obj = ProductWareHouse.objects.create(
                tenant_id=periods.tenant_id,
                company_id=periods.company_id,
                product=instance.product,
                warehouse=instance.warehouse,
                uom=instance.product.general_uom_group.uom_reference,
                unit_price=instance.value/quantity,
                tax=None,
                stock_amount=quantity,
                receipt_amount=quantity,
                sold_amount=0,
                picked_ready=0,
                used_amount=0,
                product_data={
                    "id": str(instance.product_id),
                    "code": instance.product.code,
                    "title": instance.product.title
                },
                warehouse_data={
                    "id": str(instance.warehouse_id),
                    "code": instance.warehouse.code,
                    "title": instance.warehouse.title
                },
                uom_data={
                    "id": str(instance.product.general_uom_group.uom_reference_id),
                    "code": instance.product.general_uom_group.uom_reference.code,
                    "title": instance.product.general_uom_group.uom_reference.title
                } if instance.product.general_uom_group.uom_reference else {},
                tax_data={}
            )
            return prd_wh_obj
        raise serializers.ValidationError({"Existed": 'This Product-Warehouse already exists.'})

    @classmethod
    def create_product_warehouse_data(cls, instance, validated_data):
        with transaction.atomic():
            period_obj = validated_data['period_obj']
            data_lot = instance.data_lot
            data_sn = instance.data_sn
            quantity = ReportInvCommonFunc.cast_quantity_to_unit(instance.product.inventory_uom, instance.quantity)

            instance.product.stock_amount += quantity
            instance.product.available_amount += quantity
            instance.product.save(update_fields=['stock_amount', 'available_amount'])

            if len(data_sn) > 0:
                return cls.for_serial(period_obj, instance, quantity, data_sn)
            if len(data_lot) > 0:
                return cls.for_lot(period_obj, instance, quantity, data_lot)
            if len(data_lot) == 0 and len(data_sn) == 0:
                return cls.for_none(period_obj, instance, quantity)
            return True

    @classmethod
    def push_to_inventory_report(cls, instance, prd_wh_obj):
        """ Khởi tạo số dư đầu kì """
        doc_data = []
        if len(instance.data_lot) > 0:
            all_lots = prd_wh_obj.product_warehouse_lot_product_warehouse.all()
            for lot in instance.data_lot:
                lot_mapped = all_lots.filter(lot_number=lot.get('lot_number')).first()
                if lot_mapped:
                    unit_price_by_inventory_uom = instance.value/instance.quantity
                    casted_cost = unit_price_by_inventory_uom/instance.product.inventory_uom.ratio
                    doc_data.append({
                        'product': instance.product,
                        'warehouse': instance.warehouse,
                        'system_date': instance.date_created,
                        'posting_date': instance.date_created,
                        'document_date': instance.date_created,
                        'stock_type': 1,
                        'trans_id': '',
                        'trans_code': '',
                        'trans_title': 'Balance init input',
                        'quantity': lot_mapped.quantity_import,
                        'cost': casted_cost,
                        'value': casted_cost * lot_mapped.quantity_import,
                        'lot_data': {
                            'lot_id': str(lot_mapped.id),
                            'lot_number': lot_mapped.lot_number,
                            'lot_expire_date': str(lot_mapped.expire_date) if lot_mapped.expire_date else None
                        }
                    })
        else:
            casted_quantity = ReportInvCommonFunc.cast_quantity_to_unit(
                instance.product.inventory_uom,
                instance.quantity
            )
            doc_data.append({
                'product': instance.product,
                'warehouse': instance.warehouse,
                'system_date': instance.date_created,
                'posting_date': instance.date_created,
                'document_date': instance.date_created,
                'stock_type': 1,
                'trans_id': '',
                'trans_code': '',
                'trans_title': 'Balance init input',
                'quantity': casted_quantity,
                'cost': instance.value / casted_quantity,
                'value': instance.value,
                'lot_data': {}
            })
        ReportInvLog.log(instance, instance.company.software_start_using_time, doc_data, True)
        return True

    @classmethod
    def create_m2m_balance_init_data(cls, instance):
        bulk_info_sn = []
        for serial in instance.data_sn:
            serial_obj = ProductWareHouseSerial.objects.filter(
                product_warehouse__product=instance.product,
                serial_number=serial.get('serial_number')
            ).first()
            if serial_obj:
                bulk_info_sn.append(BalanceInitializationSerial(
                    balance_init=instance,
                    serial_mapped=serial_obj
                ))
        BalanceInitializationSerial.objects.bulk_create(bulk_info_sn)

        bulk_info_lot = []
        for lot in instance.data_lot:
            lot_obj = ProductWareHouseLot.objects.filter(
                product_warehouse__product=instance.product,
                lot_number=lot.get('lot_number')
            ).first()
            if lot_obj:
                bulk_info_lot.append(BalanceInitializationLot(
                    balance_init=instance,
                    lot_mapped=lot_obj,
                    quantity=lot.get('quantity_import')
                ))
        BalanceInitializationLot.objects.bulk_create(bulk_info_lot)
        return True

    def create(self, validated_data):
        instance = BalanceInitialization.objects.create(
            product=validated_data.get('product'),
            warehouse=validated_data.get('warehouse'),
            uom=validated_data.get('uom'),
            quantity=validated_data.get('quantity', 0),
            value=validated_data.get('value', 0),
            data_lot=validated_data.get('data_lot', []),
            data_sn=validated_data.get('data_sn', []),
            tenant=self.context.get('tenant_current'),
            company=self.context.get('company_current'),
            employee_created=self.context.get('employee_current'),
            employee_inherit=self.context.get('employee_current'),
        )
        prd_wh_obj = self.create_product_warehouse_data(instance, validated_data)
        self.create_m2m_balance_init_data(instance)
        self.push_to_inventory_report(instance, prd_wh_obj)
        SubPeriods.objects.filter(period_mapped=validated_data['period_obj']).update(run_report_inventory=False)
        return instance


class BalanceInitializationCreateSerializerImportDB(BalanceInitializationCreateSerializer):
    balance_init_data = serializers.JSONField(default=dict)

    class Meta:
        model = BalanceInitialization
        fields = ('balance_init_data',)

    def validate(self, validate_data):
        tenant_current = self.context.get('tenant_current')
        company_current = self.context.get('company_current')
        if not tenant_current or not company_current:
            raise serializers.ValidationError({"error": "Tenant or Company is missing."})

        balance_init_data = validate_data.get('balance_init_data', {})
        validate_data = BalanceInitCommonFunction.validate_balance_init_data(
            balance_init_data, tenant_current, company_current
        )
        return validate_data

    def create(self, validated_data):
        instance = BalanceInitialization.objects.create(
            product=validated_data.get('product'),
            warehouse=validated_data.get('warehouse'),
            uom=validated_data.get('uom'),
            quantity=validated_data.get('quantity', 0),
            value=validated_data.get('value', 0),
            data_lot=validated_data.get('data_lot', []),
            data_sn=validated_data.get('data_sn', []),
            tenant=self.context.get('tenant_current'),
            company=self.context.get('company_current'),
            employee_created=self.context.get('employee_current'),
            employee_inherit=self.context.get('employee_current'),
        )
        prd_wh_obj = self.create_product_warehouse_data(instance, validated_data)
        self.create_m2m_balance_init_data(instance)
        self.push_to_inventory_report(instance, prd_wh_obj)
        SubPeriods.objects.filter(period_mapped=validated_data['period_obj']).update(run_report_inventory=False)
        return instance


class BalanceInitializationDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportInventoryCost
        fields = ('id',)


class BalanceInitCommonFunction:
    @staticmethod
    def cast_unit_to_inv_quantity(inventory_uom, log_quantity):
        return (log_quantity / inventory_uom.ratio) if inventory_uom else 0

    @staticmethod
    def get_product_from_balance_init_data(balance_init_data, tenant_current, company_current):
        if 'product_id' not in balance_init_data and 'product_code' not in balance_init_data:
            raise serializers.ValidationError({"error": "Balance data is missing product information."})

        prd_obj = None
        if 'product_id' in balance_init_data:
            prd_obj = Product.objects.filter(
                tenant=tenant_current, company=company_current, id=balance_init_data.get('product_id')
            ).first()
        if 'product_code' in balance_init_data:
            prd_obj = Product.objects.filter(
                tenant=tenant_current, company=company_current, code=balance_init_data.get('product_code')
            ).first()
        return prd_obj

    @staticmethod
    def get_warehouse_from_balance_init_data(balance_init_data, tenant_current, company_current):
        if 'warehouse_id' not in balance_init_data and 'warehouse_code' not in balance_init_data:
            raise serializers.ValidationError({"error": "Balance data is missing warehouse information."})

        wh_obj = None
        if 'warehouse_id' in balance_init_data:
            wh_obj = WareHouse.objects.filter(
                tenant=tenant_current, company=company_current, id=balance_init_data.get('warehouse_id')
            ).first()
        if 'product_code' in balance_init_data:
            wh_obj = WareHouse.objects.filter(
                tenant=tenant_current, company=company_current, code=balance_init_data.get('warehouse_code')
            ).first()
        return wh_obj

    @staticmethod
    def validate_balance_init_data(balance_init_data, tenant_obj, company_obj):
        prd_obj = BalanceInitCommonFunction.get_product_from_balance_init_data(
            balance_init_data, tenant_obj, company_obj
        )
        if not prd_obj:
            raise serializers.ValidationError({'prd_obj': 'Product is not found.'})

        wh_obj = BalanceInitCommonFunction.get_warehouse_from_balance_init_data(
            balance_init_data, tenant_obj, company_obj
        )
        if not wh_obj:
            raise serializers.ValidationError({'wh_obj': 'Warehouse is not found.'})

        this_period = Periods.get_current_period(tenant_obj.id, company_obj.id)
        if not this_period:
            raise serializers.ValidationError({'this_period': 'Period is not found.'})

        if not prd_obj.inventory_uom:
            raise serializers.ValidationError({'inventory_uom': 'Inventory UOM is not found.'})

        if BalanceInitialization.objects.filter(product=prd_obj, warehouse=wh_obj).exists():
            raise serializers.ValidationError(
                {"Existed": f"{prd_obj.title}'s opening balance has been created in {wh_obj.title}."}
            )

        if prd_obj.is_used_in_inventory_activities(warehouse_obj=wh_obj):
            raise serializers.ValidationError(
                {"Has trans": f'{prd_obj.title} transactions are existed in {wh_obj.title}.'}
            )

        sub_period_order = company_obj.software_start_using_time.month - this_period.space_month
        this_sub_period = this_period.sub_periods_period_mapped.filter(order=sub_period_order).first()
        if not this_sub_period:
            raise serializers.ValidationError({"this_sub_period": 'This sub period is not found.'})

        validate_data = {
            'product': prd_obj,
            'uom': prd_obj.inventory_uom,
            'warehouse': wh_obj,
            'period_obj': this_period,
            'sub_period_obj': this_sub_period,
            'quantity': float(balance_init_data.get('quantity', 0)),
            'value': float(balance_init_data.get('value', 0)),
            'data_lot': balance_init_data.get('data_lot', []),
            'data_sn': balance_init_data.get('data_sn', [])
        }
        return validate_data