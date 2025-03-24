from rest_framework import serializers

from apps.core.hr.models import Group
from apps.masterdata.saledata.models import FixedAssetClassification, ToolClassification
from apps.sales.leaseorder.models import LeaseOrderAppConfig, LeaseOrderConfigAssetGroupUsing, \
    LeaseOrderConfigToolGroupUsing
from apps.shared import HRMsg, BaseMsg


class LeaseOrderConfigDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = LeaseOrderAppConfig
        fields = (
            'asset_type_data',
            'asset_group_manage_data',
            'asset_group_using_data',
            'tool_type_data',
            'tool_group_manage_data',
            'tool_group_using_data',
        )


class LeaseOrderConfigUpdateSerializer(serializers.ModelSerializer):
    asset_type_id = serializers.UUIDField()
    asset_group_manage_id = serializers.UUIDField()
    tool_type_id = serializers.UUIDField()
    tool_group_manage_id = serializers.UUIDField()

    class Meta:
        model = LeaseOrderAppConfig
        fields = (
            'asset_type_id',
            'asset_type_data',
            'asset_group_manage_id',
            'asset_group_manage_data',
            'asset_group_using_data',
            'tool_type_id',
            'tool_type_data',
            'tool_group_manage_id',
            'tool_group_manage_data',
            'tool_group_using_data',
        )

    @classmethod
    def validate_asset_type_id(cls, value):
        try:
            return str(FixedAssetClassification.objects.get_on_company(id=value).id)
        except FixedAssetClassification.DoesNotExist:
            raise serializers.ValidationError({'asset_type': BaseMsg.NOT_EXIST})

    @classmethod
    def validate_asset_group_manage_id(cls, value):
        try:
            return str(Group.objects.get_on_company(id=value).id)
        except Group.DoesNotExist:
            raise serializers.ValidationError({'asset_group_manage': BaseMsg.NOT_EXIST})

    @classmethod
    def validate_tool_type_id(cls, value):
        try:
            return str(ToolClassification.objects.get_on_company(id=value).id)
        except ToolClassification.DoesNotExist:
            raise serializers.ValidationError({'tool_type': BaseMsg.NOT_EXIST})

    @classmethod
    def validate_tool_group_manage_id(cls, value):
        try:
            return str(Group.objects.get_on_company(id=value).id)
        except Group.DoesNotExist:
            raise serializers.ValidationError({'tool_group_manage': BaseMsg.NOT_EXIST})

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        instance.lo_config_asset_group_using_lo_config.all().delete()
        LeaseOrderConfigAssetGroupUsing.objects.bulk_create([
            LeaseOrderConfigAssetGroupUsing(
                lease_order_config=instance,
                group_using_id=asset_gs_data.get('id', None)
            ) for asset_gs_data in instance.asset_group_using_data
        ])
        instance.lo_config_tool_group_using_lo_config.all().delete()
        LeaseOrderConfigToolGroupUsing.objects.bulk_create([
            LeaseOrderConfigToolGroupUsing(
                lease_order_config=instance,
                group_using_id=tool_gs_data.get('id', None)
            ) for tool_gs_data in instance.tool_group_using_data
        ])
        return instance
