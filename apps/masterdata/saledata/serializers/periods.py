from datetime import datetime

from rest_framework import serializers
from apps.masterdata.saledata.models.periods import (
    Periods
)
from apps.sales.report.models import ReportInventoryProductWarehouse, ReportInventory


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
        period = Periods(**validated_data)
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


def update_opening_balance_after():
    for item in ReportInventoryProductWarehouse.objects.filter(for_balance=True):
        for child in ReportInventoryProductWarehouse.objects.filter(product=item.product, warehouse=item.warehouse):
            if child.period_mapped.fiscal_year == item.period_mapped.fiscal_year:
                if child.sub_period_order > item.sub_period_order:
                    child.opening_balance_quantity = item.opening_balance_quantity
                    child.opening_balance_cost = item.opening_balance_cost
                    child.opening_balance_value = item.opening_balance_value
                    child.save(update_fields=[
                        'opening_balance_quantity', 'opening_balance_cost', 'opening_balance_value'
                    ])
            elif child.period_mapped.fiscal_year > item.period_mapped.fiscal_year:
                child.opening_balance_quantity = item.opening_balance_quantity
                child.opening_balance_cost = item.opening_balance_cost
                child.opening_balance_value = item.opening_balance_value
                child.save(update_fields=[
                    'opening_balance_quantity', 'opening_balance_cost', 'opening_balance_value'
                ])
    return True


def check_wrong_cost(period_mapped, product_id, warehouse_id, software_using_time):
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


def update_balance_data(balance_data, instance):
    software_using_time = instance.company.software_start_using_time
    bulk_info_1 = []
    bulk_info_2 = []
    for item in balance_data:
        if item.get('product_id') and item.get('warehouse_id'):
            prd_wh_obj = ReportInventoryProductWarehouse.objects.filter(
                product_id=item.get('product_id'),
                warehouse_id=item.get('warehouse_id'),
                period_mapped=instance,
                sub_period_order=software_using_time.month - instance.space_month
            ).first()
            if prd_wh_obj:
                prd_wh_obj.opening_balance_quantity = float(item.get('quantity'))
                prd_wh_obj.opening_balance_value = float(item.get('value'))
                prd_wh_obj.opening_balance_cost = float(item.get('value')) / float(item.get('quantity'))
                if prd_wh_obj.ending_balance_quantity == 0:
                    prd_wh_obj.ending_balance_quantity = float(item.get('quantity'))
                    prd_wh_obj.ending_balance_value = float(item.get('value'))
                    prd_wh_obj.ending_balance_cost = float(item.get('value')) / float(item.get('quantity'))
                prd_wh_obj.wrong_cost = check_wrong_cost(
                    instance,
                    item.get('product_id'),
                    item.get('warehouse_id'),
                    software_using_time
                )
                prd_wh_obj.for_balance = True
                prd_wh_obj.save(update_fields=[
                    'opening_balance_quantity',
                    'opening_balance_value',
                    'opening_balance_cost',
                    'ending_balance_quantity',
                    'ending_balance_value',
                    'ending_balance_cost',
                    'wrong_cost',
                    'for_balance'
                ])
            else:
                bulk_info_1.append(
                    ReportInventoryProductWarehouse(
                        product_id=item.get('product_id'),
                        warehouse_id=item.get('warehouse_id'),
                        period_mapped=instance,
                        sub_period_order=software_using_time.month - instance.space_month,
                        opening_balance_quantity=float(item.get('quantity')),
                        opening_balance_value=float(item.get('value')),
                        opening_balance_cost=float(item.get('value')) / float(item.get('quantity')),
                        ending_balance_quantity=float(item.get('quantity')),
                        ending_balance_value=float(item.get('value')),
                        ending_balance_cost=float(item.get('value')) / float(item.get('quantity')),
                        for_balance=True
                    )
                )
                bulk_info_2.append(
                    ReportInventory(
                        tenant_id=instance.tenant_id,
                        company_id=instance.company_id,
                        employee_inherit=instance.employee_created,
                        employee_created=instance.employee_created,
                        product_id=item.get('product_id'),
                        period_mapped=instance,
                        sub_period_order=software_using_time.month - instance.space_month,
                    )
                )
    ReportInventoryProductWarehouse.objects.bulk_create(bulk_info_1)
    ReportInventory.objects.bulk_create(bulk_info_2)
    # update_opening_balance_after()
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
