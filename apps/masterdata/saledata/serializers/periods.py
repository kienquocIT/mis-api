from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from django.db import transaction
from rest_framework import serializers
from apps.masterdata.saledata.models import (
    ProductWareHouse, Product, WareHouse, ProductWareHouseSerial, ProductWareHouseLot
)
from apps.masterdata.saledata.models.periods import Periods, SubPeriods
from apps.sales.report.models import (
    ReportInventoryCost, ReportStockLog, ReportInventoryCostByWarehouse, BalanceInitialization
)


# Product Type
class PeriodsListSerializer(serializers.ModelSerializer):  # noqa
    software_start_using_time = serializers.SerializerMethodField()
    subs = serializers.SerializerMethodField()
    current_sub = serializers.SerializerMethodField()

    class Meta:
        model = Periods
        fields = (
            'id',
            'code',
            'title',
            'fiscal_year',
            'space_month',
            'start_date',
            'end_date',
            'software_start_using_time',
            'subs',
            'current_sub'
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
    def get_subs(cls, obj):
        return [{
            'id': sub.id,
            'order': sub.order,
            'code': sub.code,
            'name': sub.name,
            'start_date': sub.start_date,
            'end_date': sub.end_date,
            'run_report_inventory': sub.run_report_inventory,
            'locked': sub.locked
        } for sub in obj.sub_periods_period_mapped.all()]

    @classmethod
    def get_current_sub(cls, obj):
        if obj.start_date <= datetime.now().date():
            current_sub = obj.get_current_sub_period(obj)
            return {
                'id': current_sub.id,
                'order': current_sub.order,
                'current_month': (
                        current_sub.order + obj.space_month - 12
                ) if (
                        current_sub.order + obj.space_month > 12
                ) else (
                        current_sub.order + obj.space_month
                ),
                'start_date': str(current_sub.start_date) if current_sub else None,
                'end_date': str(current_sub.end_date) if current_sub else None
            } if current_sub else {}
        return {}


class PeriodsCreateSerializer(serializers.ModelSerializer):
    fiscal_year = serializers.IntegerField(allow_null=False)

    class Meta:
        model = Periods
        fields = ('code', 'title', 'fiscal_year', 'start_date', 'sub_periods_type')

    @classmethod
    def validate_fiscal_year(cls, value):
        if Periods.objects.filter_current(
            fill__tenant=True,
            fill__company=True,
            fiscal_year=value
        ).exists():
            raise serializers.ValidationError({"Period": 'This fiscal year has created already'})
        return value

    def validate(self, validate_data):
        validate_data['space_month'] = validate_data['start_date'].month - 1
        validate_data['end_date'] = validate_data['start_date'] + relativedelta(months=12) - relativedelta(days=1)
        # validate start date
        for existed_period in Periods.objects.filter(company=self.context.get('company_current')):
            if validate_data['start_date'] <= existed_period.end_date:
                raise serializers.ValidationError({"start_date": 'Time overlap with previous period'})
        # validate end date
        if validate_data['end_date'] < datetime.now().date():
            raise serializers.ValidationError({"end_date": 'Passed period'})
        # check space between 2 periods
        latest_period = Periods.objects.filter(
            company=self.context.get('company_current')
        ).order_by('-fiscal_year').first()
        if latest_period:
            gap = validate_data['start_date'] - latest_period.end_date
            if gap > timedelta(days=1):
                raise serializers.ValidationError(
                    {"start_date": f'Cannot create a new period with a gap of {str(gap).split(",", maxsplit=1)[0]} '
                                   f'from the previous period'}
                )

        software_start_using_time = self.initial_data.get('software_start_using_time')
        if self.context.get('company_current'):
            if self.context.get('company_current').software_start_using_time and software_start_using_time:
                raise serializers.ValidationError(
                    {"software_start_using_time": 'You have set up software using time already'}
                )
        else:
            raise serializers.ValidationError({"company_current": 'Company does not exist'})
        return validate_data

    def create(self, validated_data):
        period = Periods.objects.create(**validated_data)

        sub_period_data = self.initial_data.get('sub_period_data')
        bulk_info = []
        for item in sub_period_data:
            bulk_info.append(SubPeriods(period_mapped=period, **item))
        SubPeriods.objects.bulk_create(bulk_info)

        software_start_using_time = self.initial_data.get('software_start_using_time')
        if software_start_using_time:
            software_start_using_time_format = datetime.strptime(software_start_using_time, '%m-%Y')
            self.context.get('company_current').software_start_using_time = software_start_using_time_format
            self.context.get('company_current').save(update_fields=['software_start_using_time'])
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

    def validate(self, validate_data):
        software_start_using_time = self.initial_data.get('software_start_using_time')
        if self.context.get('company_current'):
            if self.context.get('company_current').software_start_using_time and software_start_using_time:
                raise serializers.ValidationError(
                    {"software_start_using_time": 'You have set up software using time already'}
                )
        else:
            raise serializers.ValidationError({"company_current": 'Company does not exist'})
        return validate_data

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()

        software_start_using_time = self.initial_data.get('software_start_using_time')
        if software_start_using_time:
            software_start_using_time_format = datetime.strptime(software_start_using_time, '%m-%Y')
            self.context.get('company_current').software_start_using_time = software_start_using_time_format
            self.context.get('company_current').save(update_fields=['software_start_using_time'])

        if all(key in self.initial_data for key in ['clear_balance_data', 'product_id', 'warehouse_id']):
            if ReportStockLog.objects.filter(
                    tenant=instance.tenant,
                    company=instance.company,
                    product_id=self.initial_data.get('product_id'),
                    warehouse_id=self.initial_data.get('warehouse_id')
            ).exclude(trans_title='Balance init input').exists():
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

            ReportStockLog.objects.filter(
                tenant=instance.tenant,
                company=instance.company,
                product=prd_obj,
                warehouse=wh_obj
            ).delete()
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
            BalanceInitialization.objects.filter(
                tenant=instance.tenant,
                company=instance.company,
                product=prd_obj,
                warehouse=wh_obj
            ).delete()
            return True
        raise serializers.ValidationError({"Not exist": 'Product | Warehouse does not exist.'})
