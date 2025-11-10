from django.db import transaction
from django.db.transaction import atomic
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from apps.accounting.accountingsettings.models import AccountDimensionMap, ChartOfAccounts, Dimension

__all__ = [
    'AccountDimensionMapListSerializer',
]

class AccountDimensionMapListSerializer(serializers.ModelSerializer):

    class Meta:
        model = AccountDimensionMap
        fields = (
            'id',
            'account_id',
            'dimension_id'
        )


class DimensionListSerializer(serializers.ModelSerializer):
    dimension_id = serializers.UUIDField(error_messages={
        'required': _('Dimension ID is required'),
    })

    class Meta:
        model = AccountDimensionMap
        fields = (
            'dimension_id',
            'status'
        )

    @classmethod
    def validate_dimension_id(cls, value):
        ...
        # try:
            # return DimensionDefinition.objects.get_on(id=value)

class DimensionListForAccountCreateSerializer(serializers.ModelSerializer):
    dimension_data = DimensionListSerializer(many=True)

    class Meta:
        model = ChartOfAccounts
        fields = (
            'dimension_data'
        )

    @transaction.atomic
    def update(self, instance, validated_data):
        dimension_data = validated_data.pop('dimension_data', None)
        update_dimension_list(instance, dimension_data)
        return instance

def update_dimension_list(chart_of_account, dimension_data):
    if not dimension_data:
        return

    # Step 1: Collect all current mappings for this account
    existing_mappings = {}
    for item in AccountDimensionMap.objects.filter_on_company(account=chart_of_account):
        existing_mappings[item.dimension_id] = item

    bulk_create_data = []
    dimensions_to_keep = []
    for dim in dimension_data:
        dim_id = dim.get("id", None)
        status = dim.get("status", 0)

        if not dim_id:
            continue

        dimensions_to_keep.append(dim_id)

        # Update existing mapping
        if dim_id in existing_mappings:
            mapping = existing_mappings[dim_id]
            if mapping.status != status:
                mapping.status = status
                mapping.save(update_fields=["status", "date_modified"])
        else:
            # New mapping to create
            bulk_create_data.append(
                AccountDimensionMap(
                    account=chart_of_account,
                    dimension_id=dim_id,
                    status=status,
                )
            )

    # Step 3: Bulk create new mappings
    if bulk_create_data:
        AccountDimensionMap.objects.bulk_create(bulk_create_data)

    # Step 4: Delete mappings that are no longer in the request
    AccountDimensionMap.objects.filter(
        account=chart_of_account
    ).exclude(dimension_id__in=dimensions_to_keep).delete()
