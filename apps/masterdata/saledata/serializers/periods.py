from datetime import datetime

from rest_framework import serializers

from apps.masterdata.saledata.models import (
    ProductWareHouse, Product, WareHouse, ProductWareHouseSerial, ProductWareHouseLot
)
from apps.masterdata.saledata.models.periods import Periods
from apps.sales.report.models import ReportInventoryProductWarehouse, ReportInventory, ReportInventorySub


# Product Type
class PeriodsListSerializer(serializers.ModelSerializer):  # noqa
    software_start_using_time = serializers.SerializerMethodField()

    class Meta:
        model = Periods
        fields = (
            'id',
            'code',
            'title',
            'fiscal_year',
            'space_month',
            'start_date',
            'software_start_using_time'
        )

    @classmethod
    def get_software_start_using_time(cls, obj):
        software_start_using_time = obj.company.software_start_using_time
        if software_start_using_time:
            if software_start_using_time.year == obj.fiscal_year:
                return f'{str(software_start_using_time.month).zfill(2)}/{str(software_start_using_time.year)}'
            return False
        return False


class PeriodsCreateSerializer(serializers.ModelSerializer):
    fiscal_year = serializers.IntegerField(allow_null=False)

    class Meta:
        model = Periods
        fields = ('code', 'title', 'fiscal_year', 'start_date')

    @classmethod
    def validate_fiscal_year(cls, value):
        if value < datetime.now().year:
            raise serializers.ValidationError({"Fiscal year": 'Passed fiscal year'})
        if Periods.objects.filter_current(
            fill__tenant=True,
            fill__company=True,
            fiscal_year=value
        ).exists():
            raise serializers.ValidationError({"Period": 'This fiscal year has created already'})
        return value

    def validate(self, validate_data):
        validate_data['space_month'] = validate_data['start_date'].month - 1
        return validate_data

    def create(self, validated_data):
        period = Periods.objects.create(**validated_data)
        software_start_using_time = self.initial_data.get('software_start_using_time')
        if software_start_using_time:
            period.company.software_start_using_time = datetime.strptime(software_start_using_time, '%m/%Y')
            period.company.save(update_fields=['software_start_using_time'])
        return period


class PeriodsDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Periods
        fields = (
            'id',
            'code',
            'title',
            'fiscal_year',
            'space_month',
            'start_date'
        )


def check_wrong_cost(period_mapped, product_id, warehouse_id, software_using_time):
    """
    B1: Check các hđ nhập xuất trong cùng kì
    B2: Check các hđ nhập xuất trong kì sau đó
    Nếu cộng lại > 0 => sai cost
    """
    same_period = ReportInventoryProductWarehouse.objects.filter(
        product_id=product_id,
        warehouse_id=warehouse_id,
        period_mapped=period_mapped,
        sub_period_order__gte=software_using_time.month - period_mapped.space_month
    )
    later_period = ReportInventoryProductWarehouse.objects.filter(
        product_id=product_id,
        warehouse_id=warehouse_id,
        period_mapped__fiscal_year__gt=period_mapped.fiscal_year,
    )
    if same_period.count() + later_period.count() > 0:
        return True
    return False


def create_data_warehouse_product(item, instance, prd_obj, wh_obj):
    """
    Nếu Số lượng = len(data_sn):
        Kiểm tra thử Product P đã có trong Warehouse W chưa ?
        Nếu chưa:
            Tạo ProductWareHouse mới
            Tạo các record ProductWareHouseSerial mới
        Else: raise lỗi
    Else: raise lỗi
    """
    bulk_info_prd_wh = []
    bulk_info_sn = []
    bulk_info_lot = []
    if len(item.get('data_sn', [])) > 0:
        if float(item.get('quantity')) == len(item.get('data_sn', [])):
            check_prd_wh = ProductWareHouse.objects.filter(
                tenant_id=instance.tenant_id,
                company_id=instance.company_id,
                product=prd_obj,
                warehouse=wh_obj
            )
            if not check_prd_wh.exists():
                bulk_info_prd_wh.append(
                    ProductWareHouse(
                        tenant_id=instance.tenant_id,
                        company_id=instance.company_id,
                        product=prd_obj,
                        warehouse=wh_obj,
                        uom=prd_obj.inventory_uom,
                        unit_price=float(item.get('value')) / float(item.get('quantity')),
                        tax=prd_obj.purchase_tax,
                        stock_amount=float(item.get('quantity')),
                        receipt_amount=float(item.get('quantity')),
                        sold_amount=0,
                        picked_ready=0,
                        used_amount=0,
                        # backup data
                        product_data={"id": str(prd_obj.id), "code": prd_obj.code, "title": prd_obj.title},
                        warehouse_data={"id": str(wh_obj.id), "code": wh_obj.code, "title": wh_obj.title},
                        uom_data={
                            "id": str(prd_obj.inventory_uom_id),
                            "code": prd_obj.inventory_uom.code,
                            "title": prd_obj.inventory_uom.title
                        },
                        tax_data={
                            "id": str(prd_obj.purchase_tax_id),
                            "code": prd_obj.purchase_tax.code,
                            "rate": prd_obj.purchase_tax.rate,
                            "title": prd_obj.purchase_tax.title
                        }
                    )
                )
                for serial in item.get('data_sn', []):
                    bulk_info_sn.append(
                        ProductWareHouseSerial(
                            tenant_id=instance.tenant_id,
                            company_id=instance.company_id,
                            product_warehouse=bulk_info_prd_wh[-1],
                            **serial
                        )
                    )
                return bulk_info_prd_wh, bulk_info_sn, []
            raise serializers.ValidationError({"Existed": 'This Product-Warehouse already exists.'})
        raise serializers.ValidationError({"Invalid": 'Quantity is != num serial data.'})
    if len(item.get('data_lot', [])) > 0:
        if float(item.get('quantity')) == sum(float(lot.get('quantity_import', 0)) for lot in item.get('data_lot', [])):
            check_prd_wh = ProductWareHouse.objects.filter(
                tenant_id=instance.tenant_id,
                company_id=instance.company_id,
                product=prd_obj,
                warehouse=wh_obj
            )
            if not check_prd_wh.exists():
                bulk_info_prd_wh.append(
                    ProductWareHouse(
                        tenant_id=instance.tenant_id,
                        company_id=instance.company_id,
                        product=prd_obj,
                        warehouse=wh_obj,
                        uom=prd_obj.inventory_uom,
                        unit_price=float(item.get('value')) / float(item.get('quantity')),
                        tax=prd_obj.purchase_tax,
                        stock_amount=float(item.get('quantity')),
                        receipt_amount=float(item.get('quantity')),
                        sold_amount=0,
                        picked_ready=0,
                        used_amount=0,
                        # backup data
                        product_data={"id": str(prd_obj.id), "code": prd_obj.code, "title": prd_obj.title},
                        warehouse_data={"id": str(wh_obj.id), "code": wh_obj.code, "title": wh_obj.title},
                        uom_data={
                            "id": str(prd_obj.inventory_uom_id),
                            "code": prd_obj.inventory_uom.code,
                            "title": prd_obj.inventory_uom.title
                        },
                        tax_data={
                            "id": str(prd_obj.purchase_tax_id),
                            "code": prd_obj.purchase_tax.code,
                            "rate": prd_obj.purchase_tax.rate,
                            "title": prd_obj.purchase_tax.title
                        }
                    )
                )
                for lot in item.get('data_lot', []):
                    bulk_info_lot.append(
                        ProductWareHouseLot(
                            tenant_id=instance.tenant_id,
                            company_id=instance.company_id,
                            product_warehouse=bulk_info_prd_wh[-1],
                            **lot
                        )
                    )
                return bulk_info_prd_wh, [], bulk_info_lot
            raise serializers.ValidationError({"Existed": 'This Product-Warehouse already exists.'})
        raise serializers.ValidationError({"Invalid": 'Quantity is != num lot data.'})


def update_balance_data(balance_data, instance):
    """
    Lấy thời gian sử dụng phần mềm
    Lặp từng row trong balance table:
        Nếu có product_id + warehouse_id:
            Lấy product_obj, warehouse_obj (check valid - else: raise lỗi)
            Kiểm tra thử có hđ nhập-xuất nào chưa ?
            Nếu có: raise lỗi
            Else:
                Lấy record ReportInventoryProductWarehouse (theo period và sub)
                Nếu có: raise lỗi
                Else:
                    Cập nhập 'stock_amount' và 'available_amount' cho Product (cộng lên)
                    Tạo ReportInventoryProductWarehouse mới (lưu opening_balance_quantity-value-cost)
                    Tạo ReportInventory mới (lưu prd-wh theo period và sub)
                    Tạo các item Serial|Lot để quản lí kho (nếu quản lí bằng Serial|Lot)
        Else: raise lỗi
    """
    sub_period_order_value = instance.company.software_start_using_time.month - instance.space_month
    bulk_info_rp_prd_wh = []
    bulk_info_inventory = []
    bulk_info_prd_wh = []
    bulk_info_sn = []
    bulk_info_lot = []
    for item in balance_data:
        if item.get('product_id') and item.get('warehouse_id'):
            prd_obj = Product.objects.filter(id=item.get('product_id')).first()
            wh_obj = WareHouse.objects.filter(id=item.get('warehouse_id')).first()

            if prd_obj and wh_obj:
                if ReportInventorySub.objects.filter(product=prd_obj, warehouse=wh_obj).exists():
                    raise serializers.ValidationError(
                        {"Has trans": f'{prd_obj.title} transactions are existed in {wh_obj.title}.'}
                    )

                if ReportInventoryProductWarehouse.objects.filter(
                    product=prd_obj,
                    warehouse=wh_obj,
                    period_mapped=instance,
                    sub_period_order=sub_period_order_value
                ).first():
                    raise serializers.ValidationError(
                        {"Existed": f"{prd_obj.title}'s opening balance has been created in {wh_obj.title}."}
                    )

                prd_obj.stock_amount += float(item.get('quantity'))
                prd_obj.available_amount += float(item.get('quantity'))
                prd_obj.save(update_fields=['stock_amount', 'available_amount'])
                bulk_info_rp_prd_wh.append(
                    ReportInventoryProductWarehouse(
                        product=prd_obj,
                        warehouse=wh_obj,
                        period_mapped=instance,
                        sub_period_order=sub_period_order_value,
                        opening_balance_quantity=float(item.get('quantity')),
                        opening_balance_value=float(item.get('value')),
                        opening_balance_cost=float(item.get('value')) / float(item.get('quantity')),
                        ending_balance_quantity=float(item.get('quantity')),
                        ending_balance_value=float(item.get('value')),
                        ending_balance_cost=float(item.get('value')) / float(item.get('quantity')),
                        for_balance=True
                    )
                )

                if not ReportInventory.objects.filter(
                        tenant_id=instance.tenant_id,
                        company_id=instance.company_id,
                        product=prd_obj,
                        period_mapped=instance,
                        sub_period_order=sub_period_order_value,
                ).exists():
                    bulk_info_inventory.append(
                        ReportInventory(
                            tenant_id=instance.tenant_id,
                            company_id=instance.company_id,
                            employee_inherit=instance.employee_created,
                            employee_created=instance.employee_created,
                            product=prd_obj,
                            period_mapped=instance,
                            sub_period_order=sub_period_order_value,
                        )
                    )

                bulk_info_prd_wh_item, bulk_info_sn_item, bulk_info_lot_item = create_data_warehouse_product(
                    item, instance, prd_obj, wh_obj
                )
                bulk_info_prd_wh += bulk_info_prd_wh_item
                bulk_info_sn += bulk_info_sn_item
                bulk_info_lot += bulk_info_lot_item
            else:
                raise serializers.ValidationError({"Not exist": 'Product | Warehouse is not exist.'})
        ReportInventoryProductWarehouse.objects.bulk_create(bulk_info_rp_prd_wh)
        ReportInventory.objects.bulk_create(bulk_info_inventory)
        ProductWareHouse.objects.bulk_create(bulk_info_prd_wh)
        ProductWareHouseSerial.objects.bulk_create(bulk_info_sn)
    return True


class PeriodsUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Periods
        fields = ('code', 'title')

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()

        software_start_using_time = self.initial_data.get('software_start_using_time')
        if software_start_using_time:
            instance.company.software_start_using_time = datetime.strptime(software_start_using_time, '%m/%Y')
            instance.company.save(update_fields=['software_start_using_time'])

        if 'balance_data' in self.initial_data:
            update_balance_data(self.initial_data.get('balance_data', []), instance)

        return instance
