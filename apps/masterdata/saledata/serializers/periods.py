from datetime import datetime
from rest_framework import serializers
from apps.masterdata.saledata.models import (
    ProductWareHouse, Product, WareHouse, ProductWareHouseSerial, ProductWareHouseLot
)
from apps.masterdata.saledata.models.periods import Periods, SubPeriods
from apps.sales.report.models import ReportInventoryProductWarehouse, ReportInventory, ReportInventorySub


# Product Type
class PeriodsListSerializer(serializers.ModelSerializer):  # noqa
    software_start_using_time = serializers.SerializerMethodField()
    state = serializers.SerializerMethodField()
    subs = serializers.SerializerMethodField()

    class Meta:
        model = Periods
        fields = (
            'id',
            'code',
            'title',
            'fiscal_year',
            'space_month',
            'start_date',
            'software_start_using_time',
            'state',
            'subs'
        )

    @classmethod
    def get_software_start_using_time(cls, obj):
        software_start_using_time = obj.company.software_start_using_time
        if software_start_using_time:
            if software_start_using_time.year == obj.fiscal_year:
                return f'{str(software_start_using_time.month).zfill(2)}/{str(software_start_using_time.year)}'
            return False
        return False

    @classmethod
    def get_state(cls, obj):
        if obj.fiscal_year == datetime.now().year:
            return 0
        return 1

    @classmethod
    def get_subs(cls, obj):
        return [{
            'id': sub.id,
            'order': sub.order,
            'code': sub.code,
            'name': sub.name,
            'start_date': sub.start_date,
            'end_date': sub.end_date,
            'state': sub.state
        } for sub in obj.sub_periods_period_mapped.all()]


class PeriodsCreateSerializer(serializers.ModelSerializer):
    fiscal_year = serializers.IntegerField(allow_null=False)

    class Meta:
        model = Periods
        fields = ('code', 'title', 'fiscal_year', 'start_date', 'sub_periods_type')

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
            if not period.company.software_start_using_time:
                period.company.software_start_using_time = datetime.strptime(software_start_using_time, '%m/%Y')
                period.company.save(update_fields=['software_start_using_time'])
            else:
                raise serializers.ValidationError({"Exist": 'You have set up software using time already'})

        sub_period_data = self.initial_data.get('sub_period_data')
        bulk_info = []
        for item in sub_period_data:
            bulk_info.append(SubPeriods(period_mapped=period, **item))
        SubPeriods.objects.bulk_create(bulk_info)
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
            'start_date',
            'sub_periods_type'
        )


def for_serial(item, instance, prd_obj, wh_obj):
    bulk_info_prd_wh = []
    bulk_info_sn = []
    if float(item.get('quantity')) == len(item.get('data_sn', [])):
        if not ProductWareHouse.objects.filter(
                tenant_id=instance.tenant_id,
                company_id=instance.company_id,
                product=prd_obj,
                warehouse=wh_obj
        ).exists():
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


def for_lot(item, instance, prd_obj, wh_obj):
    bulk_info_prd_wh = []
    bulk_info_lot = []
    if float(item.get('quantity')) == sum(float(lot.get('quantity_import', 0)) for lot in item.get('data_lot', [])):
        if not ProductWareHouse.objects.filter(
                tenant_id=instance.tenant_id,
                company_id=instance.company_id,
                product=prd_obj,
                warehouse=wh_obj
        ).exists():
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


def for_none(item, instance, prd_obj, wh_obj):
    bulk_info_prd_wh = []
    if not ProductWareHouse.objects.filter(
            tenant_id=instance.tenant_id,
            company_id=instance.company_id,
            product=prd_obj,
            warehouse=wh_obj
    ).exists():
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
        return bulk_info_prd_wh, [], []
    raise serializers.ValidationError({"Existed": 'This Product-Warehouse already exists.'})


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

                # Nếu Số lượng = len(data_sn):
                #     Kiểm tra thử Product P đã có trong Warehouse W chưa ?
                #     Nếu chưa:
                #         Tạo ProductWareHouse mới
                #         Tạo các record ProductWareHouseSerial mới
                #     Else: raise lỗi
                # Else: raise lỗi
                if len(item.get('data_sn', [])) > 0:
                    sub_prd_wh, sub_sn, sub_lot = for_serial(item, instance, prd_obj, wh_obj)
                elif len(item.get('data_lot', [])) > 0:
                    sub_prd_wh, sub_sn, sub_lot = for_lot(item, instance, prd_obj, wh_obj)
                elif len(item.get('data_lot', [])) == 0 and len(item.get('data_sn', [])) == 0:
                    sub_prd_wh, sub_sn, sub_lot = for_none(item, instance, prd_obj, wh_obj)
                else:
                    sub_prd_wh, sub_sn, sub_lot = [], [], []

                bulk_info_prd_wh += sub_prd_wh
                bulk_info_sn += sub_sn
                bulk_info_lot += sub_lot
            else:
                raise serializers.ValidationError({"Not exist": 'Product | Warehouse is not exist.'})
        ReportInventoryProductWarehouse.objects.bulk_create(bulk_info_rp_prd_wh)
        ReportInventory.objects.bulk_create(bulk_info_inventory)
        ProductWareHouse.objects.bulk_create(bulk_info_prd_wh)
        ProductWareHouseSerial.objects.bulk_create(bulk_info_sn)
        ProductWareHouseLot.objects.bulk_create(bulk_info_lot)
    return True


class PeriodsUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Periods
        fields = ('code', 'title')

    @classmethod
    def get_previous_sub_period(cls, period_mapped, sub):
        return SubPeriods.objects.filter(
            period_mapped=period_mapped, order=sub.order - 1
        ).first() if sub.order > 1 else SubPeriods.objects.filter(
            period_mapped__fiscal_year=period_mapped.fiscal_year - 1
        ).order_by('order').last()

    @classmethod
    def get_all_sub_periods(cls, sub):
        all_sub_periods = []
        tenant_id = sub.period_mapped.tenant_id
        company_id = sub.period_mapped.company_id

        all_sub_periods += sub.period_mapped.sub_periods_period_mapped.filter(order__gt=sub.order)
        all_sub_periods += SubPeriods.objects.filter(
            period_mapped__fiscal_year__in=range(sub.period_mapped.fiscal_year + 1, datetime.now().year)
        )
        current_period = Periods.objects.filter(
            tenant_id=tenant_id, company_id=company_id, fiscal_year=datetime.now().year
        ).first()
        if current_period:
            all_sub_periods += current_period.sub_periods_period_mapped.filter(
                order__lte=datetime.now().month - current_period.space_month
            )
        return all_sub_periods

    @classmethod
    def auto_update_cost_for_subs_after(cls, sub):
        for sub_item in cls.get_all_sub_periods(sub):
            previous_sub = cls.get_previous_sub_period(sub_item.period_mapped, sub_item)
            if previous_sub:
                for item in sub_item.report_inventory_product_warehouse_sub_period.all():
                    previous_sub_value = previous_sub.report_inventory_product_warehouse_sub_period.filter(
                        product=item.product,
                        warehouse=item.warehouse
                    ).first()
                    if previous_sub_value:
                        item.opening_balance_quantity = previous_sub_value.ending_balance_quantity
                        item.opening_balance_cost = previous_sub_value.ending_balance_cost
                        item.opening_balance_value = previous_sub_value.ending_balance_value
                        item.save(
                            update_fields=['opening_balance_quantity', 'opening_balance_cost', 'opening_balance_value']
                        )

                        all_trans = ReportInventorySub.objects.filter(
                            report_inventory__sub_period=sub_item,
                            product=item.product,
                            warehouse=item.warehouse
                        ).order_by('system_date')

                        for index in range(len(all_trans)):
                            if index == 0:
                                if all_trans[index].stock_type == 1:
                                    new_quantity = item.opening_balance_quantity + all_trans[index].quantity
                                    sum_value = item.opening_balance_value + all_trans[index].value
                                    new_cost = sum_value / new_quantity
                                    new_value = sum_value
                                else:
                                    new_quantity = item.opening_balance_quantity - all_trans[index].quantity
                                    new_cost = item.opening_balance_cost
                                    new_value = new_cost * new_quantity
                            else:
                                if all_trans[index].stock_type == 1:
                                    new_quantity = all_trans[index-1].current_quantity + all_trans[index].quantity
                                    sum_value = all_trans[index-1].current_value + all_trans[index].value
                                    new_cost = sum_value / new_quantity
                                    new_value = sum_value
                                else:
                                    new_quantity = all_trans[index-1].current_quantity - all_trans[index].quantity
                                    new_cost = all_trans[index-1].current_cost
                                    new_value = new_cost * new_quantity
                            all_trans[index].current_quantity = new_quantity
                            all_trans[index].current_cost = new_cost
                            all_trans[index].current_value = new_value
                            all_trans[index].save(
                                update_fields=['current_quantity', 'current_cost', 'current_value']
                            )
                        item.ending_balance_quantity = all_trans.last().current_quantity
                        item.ending_balance_cost = all_trans.last().current_cost
                        item.ending_balance_value = all_trans.last().current_value
                        item.save(
                            update_fields=['ending_balance_quantity', 'ending_balance_cost', 'ending_balance_value']
                        )
        return True

    @classmethod
    def check_has_trans(cls, sub):
        if ReportInventorySub.objects.filter(report_inventory__sub_period=sub).count() > 0:
            return True
        return False

    @classmethod
    def get_next_sub_and_push_opening(cls, sub, item):
        this_period = sub.period_mapped
        last_sub_order_this_period = this_period.sub_periods_period_mapped.count()
        if sub.order == last_sub_order_this_period:
            next_period = Periods.objects.filter(fiscal_year=this_period.fiscal_year + 1).first()
            if next_period:
                next_sub = this_period.sub_periods_period_mappep.first()
                if next_sub:
                    next_sub.opening_balance_quantity = item.ending_balance_quantity
                    next_sub.opening_balance_cost = item.opening_balance_cost
                    next_sub.opening_balance_value = item.ending_balance_value
                    next_sub.wrong_cost = cls.check_has_trans(next_sub)
                    next_sub.save(
                        update_fields=[
                            'opening_balance_quantity',
                            'opening_balance_cost',
                            'opening_balance_value',
                            'wrong_cost'
                        ]
                    )
                    return next_sub
            raise serializers.ValidationError(
                {"Error": "Can't push this sub-period ending as next sub-period opening. Please create next period."}
            )
        else:
            next_sub = this_period.sub_periods_period_mapped.filter(order=sub.order + 1).first()
            if next_sub:
                next_sub.opening_balance_quantity = item.ending_balance_quantity
                next_sub.opening_balance_cost = item.opening_balance_cost
                next_sub.opening_balance_value = item.ending_balance_value
                next_sub.wrong_cost = cls.check_has_trans(next_sub)
                next_sub.save(
                    update_fields=[
                        'opening_balance_quantity',
                        'opening_balance_cost',
                        'opening_balance_value'
                        'wrong_cost'
                    ]
                )
                return next_sub
            raise serializers.ValidationError(
                {"Error": "Can't push this sub-period ending as next sub-period opening. Please create next period."}
            )

    @classmethod
    def for_sub_state_is_close(cls, sub):
        current_period = Periods.objects.filter(fiscal_year=datetime.now().year).first()
        period_mapped = sub.period_mapped
        # step 1: get all product-warehouse has transaction in this period-sub
        # step 2: close the sub-period of each prd-wh (has trans)
        existed_prd = []
        existed_wh = []
        for item in sub.report_inventory_product_warehouse_sub_period.all():
            product_obj = item.product
            warehouse_obj = item.warehouse
            existed_prd.append(str(product_obj.id))
            existed_wh.append(str(warehouse_obj.id))
            last_trans = ReportInventorySub.objects.filter(
                product=product_obj,
                warehouse=warehouse_obj,
                report_inventory__sub_period=sub
            ).order_by('-system_date').first()
            if last_trans:
                item.ending_balance_quantity = last_trans.current_quantity
                item.ending_balance_cost = last_trans.current_cost
                item.ending_balance_value = last_trans.current_value
            else:
                item.ending_balance_quantity = item.opening_balance_quantity
                item.ending_balance_cost = item.opening_balance_cost
                item.ending_balance_value = item.opening_balance_value
            item.save(update_fields=['ending_balance_quantity', 'ending_balance_cost', 'ending_balance_value'])
            # step 2.a: push this sub ending as next sub opening
            if current_period:
                if str(period_mapped.id) == str(current_period.id):
                    cls.get_next_sub_and_push_opening(sub, item)
                else:
                    cls.auto_update_cost_for_subs_after(sub)
            else:
                raise serializers.ValidationError({"Error": "Current period is not exist."})

        # step 3: get product of previous sub-period that don't have trans in this sub-period (update open = end)
        previous_sub = cls.get_previous_sub_period(period_mapped, sub)
        if previous_sub:
            bulk_info = []
            for item in previous_sub.report_inventory_product_warehouse_sub_period.all():
                product_id = item.product_id
                warehouse_id = item.warehouse_id
                if str(product_id) not in existed_prd and str(warehouse_id) not in existed_wh:
                    bulk_info.append(
                        ReportInventoryProductWarehouse.objects.create(
                            product_id=product_id,
                            warehouse_id=warehouse_id,
                            period_mapped=period_mapped,
                            sub_period_order=sub.order,
                            sub_period=sub,
                            opening_balance_quantity=item.ending_balance_quantity,
                            opening_balance_cost=item.ending_balance_cost,
                            opening_balance_value=item.ending_balance_value,
                            ending_balance_quantity=item.ending_balance_quantity,
                            ending_balance_cost=item.ending_balance_cost,
                            ending_balance_value=item.ending_balance_value,
                            for_balance=False,
                            wrong_cost=False,
                            is_close=True
                        )
                    )
            ReportInventoryProductWarehouse.objects.bulk_create(bulk_info)
        return True

    @classmethod
    def for_sub_state_is_open(cls, sub):
        for item in sub.report_inventory_product_warehouse_sub_period.all():
            item.ending_balance_quantity = 0
            item.ending_balance_cost = 0
            item.ending_balance_value = 0
            item.save(update_fields=['ending_balance_quantity', 'ending_balance_cost', 'ending_balance_value'])
        return True

    @classmethod
    def check_past_sub(cls, sub):
        this_year = datetime.now().year
        this_month = datetime.now().month
        is_past_year = this_year > sub.period_mapped.fiscal_year
        is_this_year = this_year == sub.period_mapped.fiscal_year
        is_past_sub = this_month - sub.period_mapped.space_month > sub.order
        if is_past_year or (is_this_year and is_past_sub):
            return True
        return False

    @classmethod
    def recalculate_cost_value(cls, sub):
        if sub.state == '1':
            if cls.check_past_sub(sub):
                cls.for_sub_state_is_close(sub)
            else:
                raise serializers.ValidationError({"Error": 'Can not Close this Sub. Only Close sub(s) in the past.'})
        if sub.state == '0':
            cls.for_sub_state_is_open(sub)
        return True

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()

        software_start_using_time = self.initial_data.get('software_start_using_time')
        if software_start_using_time:
            if not instance.company.software_start_using_time:
                instance.company.software_start_using_time = datetime.strptime(software_start_using_time, '%m/%Y')
                instance.company.save(update_fields=['software_start_using_time'])
            else:
                raise serializers.ValidationError({"Exist": 'You have set up software using time already'})

        if 'balance_data' in self.initial_data:
            update_balance_data(self.initial_data.get('balance_data', []), instance)

        if 'sub_id' in self.initial_data and 'state' in self.initial_data:
            sub_id = self.initial_data.get('sub_id')
            new_state = self.initial_data.get('state', 0)
            sub = SubPeriods.objects.filter(id=sub_id).first()
            if sub:
                sub.state = new_state
                sub.save(update_fields=['state'])
                self.recalculate_cost_value(sub)

        return instance
