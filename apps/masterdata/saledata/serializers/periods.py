from datetime import datetime
from django.db import transaction
from rest_framework import serializers
from apps.masterdata.saledata.models import (
    ProductWareHouse, Product, WareHouse, ProductWareHouseSerial, ProductWareHouseLot
)
from apps.masterdata.saledata.models.periods import Periods, SubPeriods
from apps.sales.report.models import (
    ReportInventoryCost, ReportStockLog, ReportInventoryCostByWarehouse
)


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
            'locked': sub.locked
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
            software_start_using_time_format = datetime.strptime(software_start_using_time, '%m-%Y')
            if not period.company.software_start_using_time:
                period.company.software_start_using_time = software_start_using_time_format
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
            software_start_using_time_format = datetime.strptime(software_start_using_time, '%m-%Y')
            if (not instance.company.software_start_using_time or
                    software_start_using_time_format == instance.company.software_start_using_time):
                instance.company.software_start_using_time = software_start_using_time_format
                instance.company.save(update_fields=['software_start_using_time'])
            else:
                raise serializers.ValidationError({"Exist": 'You have set up software using time already'})

        if all(key in self.initial_data for key in ['clear_balance_data', 'product_id', 'warehouse_id']):
            if ReportStockLog.objects.filter(
                    tenant=instance.tenant,
                    company=instance.company,
                    product_id=self.initial_data.get('product_id'),
                    warehouse_id=self.initial_data.get('warehouse_id')
            ).exists():
                raise serializers.ValidationError(
                    {"Has trans": 'The transactions of this product are existed in this warehouse.'}
                )

            try:
                with transaction.atomic():
                    PeriodInventoryFunction.clear_balance_data(
                        instance,
                        self.initial_data.get('product_id'),
                        self.initial_data.get('warehouse_id')
                    )
                    SubPeriods.objects.filter(period_mapped=instance).update(run_report_inventory=False)
                return instance
            except Exception as err:
                return err
        return instance


class PeriodInventoryFunction:
    @classmethod
    def clear_balance_data(cls, instance, product_id, warehouse_id):
        prd_obj = Product.objects.filter(id=product_id).first()
        wh_obj = WareHouse.objects.filter(id=warehouse_id).first()
        company_config = instance.company.company_config
        if prd_obj and wh_obj:
            prd_obj.stock_amount = 0
            prd_obj.available_amount = 0
            prd_obj.save(update_fields=['stock_amount', 'available_amount'])

            ReportInventoryCost.objects.filter(
                tenant=instance.tenant,
                company=instance.company,
                product=prd_obj,
                warehouse=wh_obj if not company_config.cost_per_project else None
            ).delete()
            ReportInventoryCostByWarehouse.objects.filter(
                report_inventory_cost__product=prd_obj,
                report_inventory_cost__warehouse=wh_obj if not company_config.cost_per_project else None
            ).delete()
            ProductWareHouse.objects.filter(
                tenant=instance.tenant,
                company=instance.company,
                product=prd_obj,
                warehouse=wh_obj
            ).delete()
            ProductWareHouseSerial.objects.filter(
                tenant=instance.tenant,
                company=instance.company,
                product_warehouse__product=prd_obj,
                product_warehouse__warehouse=wh_obj
            ).delete()
            ProductWareHouseLot.objects.filter(
                tenant=instance.tenant,
                company=instance.company,
                product_warehouse__product=prd_obj,
                product_warehouse__warehouse=wh_obj
            ).delete()
            return True
        raise serializers.ValidationError({"Not exist": 'Product | Warehouse does not exist.'})
