import logging
from django.db import transaction
from rest_framework import serializers

from apps.core.workflow.tasks import decorator_run_workflow
from apps.sales.asset.models import InstrumentToolWriteOff, InstrumentTool, InstrumentToolWriteOffQuantity
from apps.shared import BaseMsg, FixedAssetMsg, AbstractCreateSerializerModel, AbstractDetailSerializerModel, \
    AbstractListSerializerModel

logger = logging.getLogger(__name__)

__all__= [
    'InstrumentToolWriteOffListSerializer',
    'InstrumentToolWriteOffCreateSerializer',
    'InstrumentToolWriteOffUpdateSerializer',
    'InstrumentToolWriteOffDetailSerializer'
]


class InstrumentToolWriteOffListSerializer(AbstractListSerializerModel):
    type = serializers.SerializerMethodField()

    class Meta:
        model = InstrumentToolWriteOff
        fields = (
            'id',
            'code',
            'title',
            'document_date',
            'posting_date',
            'type'
        )

    @classmethod
    def get_type(cls, obj):
        return obj.get_type_display()


class InstrumentToolListCreateSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(required=False)
    write_off_quantity = serializers.IntegerField()

    class Meta:
        model = InstrumentTool
        fields = ('id','asset_code','write_off_quantity')

    @classmethod
    def validate_id(cls, value):
        if value:
            try:
                return InstrumentTool.objects.get(id=value).id
            except InstrumentTool.DoesNotExist():
                raise serializers.ValidationError({'tool_list': FixedAssetMsg.TOOL_NOT_FOUND})
        raise serializers.ValidationError({'id': BaseMsg.REQUIRED})

    def validate(self, validate_data): # pylint: disable=C0103
        tool_id = validate_data.get('id', None)
        write_off_quantity = validate_data.get('write_off_quantity', 0)
        it = InstrumentTool.objects.filter(id=tool_id).first()

        if it:
            total_write_off_quantity = 0
            it_write_off_list = it.write_off_quantities.all()
            for it_write_off in it_write_off_list:
                total_write_off_quantity += it_write_off.write_off_quantity

            using_quantity = it.quantity - total_write_off_quantity
            if using_quantity < write_off_quantity:
                raise serializers.ValidationError({'write_off_quantity': FixedAssetMsg.WRITEOFF_QUANTITY_INVALID})
        return validate_data


class InstrumentToolWriteOffCreateSerializer(AbstractCreateSerializerModel):
    tool_list = InstrumentToolListCreateSerializer(many=True)

    class Meta:
        model = InstrumentToolWriteOff
        fields = (
            'title',
            'note',
            'posting_date',
            'document_date',
            'type',
            'tool_list'
        )

    @decorator_run_workflow
    def create(self, validated_data):  # pylint: disable=C0103
        tool_list = validated_data.pop('tool_list')
        try:
            with transaction.atomic():
                instrument_tool_write_off = InstrumentToolWriteOff.objects.create(**validated_data)

                for tool in tool_list:
                    it = InstrumentTool.objects.filter(id=tool.get('id', None)).first()
                    if it:
                        write_off_quantity = tool.get('write_off_quantity', 0)

                        InstrumentToolWriteOffQuantity.objects.create(
                            instrument_tool=it,
                            instrument_tool_write_off = instrument_tool_write_off,
                            write_off_quantity=write_off_quantity
                        )

        except Exception as err:
            logger.error(msg=f'Create instrument tool write off errors: {str(err)}')
            raise serializers.ValidationError({'instrument tool write off': FixedAssetMsg.ERROR_CREATE})

        return instrument_tool_write_off


class InstrumentToolListUpdateSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(required=False)
    write_off_quantity = serializers.IntegerField()

    class Meta:
        model = InstrumentTool
        fields = ('id','asset_code', 'write_off_quantity')

    @classmethod
    def validate_id(cls, value):
        if value:
            try:
                return InstrumentTool.objects.get(id=value).id
            except InstrumentTool.DoesNotExist():
                raise serializers.ValidationError({'tool_list': FixedAssetMsg.TOOL_NOT_FOUND})
        raise serializers.ValidationError({'id': BaseMsg.REQUIRED})

    def validate(self, validate_data): # pylint: disable=C0103
        tool_id = validate_data.get('id', None)
        write_off_quantity = validate_data.get('write_off_quantity', 0)
        it = InstrumentTool.objects.filter(id=tool_id).first()
        instrument_tool_write_off_id = self.context.get('instrument_tool_write_off_id', None)

        if it:
            total_write_off_quantity = 0
            it_write_off_list = it.write_off_quantities.exclude(
                instrument_tool_write_off_id = instrument_tool_write_off_id
            )

            for it_write_off in it_write_off_list:
                total_write_off_quantity += it_write_off.write_off_quantity

            using_quantity = it.quantity - total_write_off_quantity
            if using_quantity < write_off_quantity:
                raise serializers.ValidationError({'write_off_quantity': FixedAssetMsg.WRITEOFF_QUANTITY_INVALID})

        return validate_data


class InstrumentToolWriteOffUpdateSerializer(AbstractCreateSerializerModel):
    tool_list = InstrumentToolListUpdateSerializer(many=True)

    class Meta:
        model = InstrumentToolWriteOff
        fields = (
            'title',
            'note',
            'posting_date',
            'document_date',
            'type',
            'tool_list'
        )

    @decorator_run_workflow
    def update(self, instrument_tool_write_off, validated_data): # pylint: disable=C0103
        tool_list = validated_data.pop('tool_list')

        try:
            with transaction.atomic():
                for key, value in validated_data.items():
                    setattr(instrument_tool_write_off, key, value)
                instrument_tool_write_off.save()

                instrument_tool_write_off.quantities.all().delete()

                for tool in tool_list:
                    it = InstrumentTool.objects.filter(id=tool.get('id', None)).first()
                    if it:
                        write_off_quantity = tool.get('write_off_quantity', 0)

                        InstrumentToolWriteOffQuantity.objects.create(
                            instrument_tool=it,
                            instrument_tool_write_off = instrument_tool_write_off,
                            write_off_quantity=write_off_quantity
                        )

        except Exception as err:
            logger.error(msg=f'Update instrument tool write off errors: {str(err)}')
            raise serializers.ValidationError({'instrument tool write off': FixedAssetMsg.ERROR_CREATE})

        return instrument_tool_write_off


class InstrumentToolWriteOffDetailSerializer(AbstractDetailSerializerModel):
    tool_list = serializers.SerializerMethodField()

    class Meta:
        model = InstrumentToolWriteOff
        fields = (
            'id',
            'note',
            'title',
            'posting_date',
            'document_date',
            'type',
            'tool_list'
        )

    @classmethod
    def get_tool_list(cls, obj): # pylint: disable=C0103
        data = []
        for it_write_off_quantity in obj.quantities.all():
            total_quantity = it_write_off_quantity.instrument_tool.quantity
            using_quantity = total_quantity
            it_writeoff_list = InstrumentToolWriteOffQuantity.objects.filter(
                instrument_tool = it_write_off_quantity.instrument_tool
            )
            for it in it_writeoff_list:
                using_quantity = using_quantity - it.write_off_quantity
            data.append({
                'id': it_write_off_quantity.instrument_tool_id,
                'title': it_write_off_quantity.instrument_tool.title,
                'asset_code': it_write_off_quantity.instrument_tool.asset_code,
                'using_quantity': using_quantity,
                'write_off_quantity': it_write_off_quantity.write_off_quantity,
                'net_book_value': 0,
            })
        return data
