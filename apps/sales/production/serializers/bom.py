from rest_framework import serializers
from apps.core.workflow.tasks import decorator_run_workflow
from apps.masterdata.saledata.models import Product, Expense, UnitOfMeasure
from apps.sales.production.models import BOM, BOMProcess, BOMSummaryProcess, BOMMaterialComponent, BOMTool
from apps.shared import AbstractDetailSerializerModel, AbstractCreateSerializerModel, AbstractListSerializerModel


class LaborListForBOMSerializer(serializers.ModelSerializer):
    uom = serializers.SerializerMethodField()
    price_list = serializers.SerializerMethodField()

    class Meta:
        model = Expense
        fields = (
            'id',
            'code',
            'title',
            'uom',
            'uom_group',
            'price_list',
        )

    @classmethod
    def get_uom(cls, obj):
        return {
            'id': str(obj.uom_id),
            'code': obj.uom.code,
            'title': obj.uom.title,
            'ratio': obj.uom.ratio
        } if obj.uom else {}

    @classmethod
    def get_price_list(cls, obj):
        price_list = []
        for item in obj.expense.all():
            price_list.append({
                'price': {
                    'id': str(item.price_id),
                    'code': item.price.code,
                    'title': item.price.title,
                } if item.price else {},
                'price_value': item.price_value,
                'uom': {
                    'id': str(item.uom_id),
                    'code': item.uom.code,
                    'title': item.uom.title
                } if item.uom else {}
            })
        return price_list


class BOMProductMaterialListSerializer(serializers.ModelSerializer):
    sale_default_uom = serializers.SerializerMethodField()
    price_list = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            'id',
            'code',
            'title',
            'sale_default_uom',
            'general_uom_group',
            'price_list'
        )

    @classmethod
    def get_sale_default_uom(cls, obj):
        return {
            'id': str(obj.sale_default_uom_id),
            'code': obj.sale_default_uom.code,
            'title': obj.sale_default_uom.title
        } if obj.sale_default_uom else {}

    @classmethod
    def get_price_list(cls, obj):
        price_list = []
        for item in obj.product_price_product.all():
            price_list.append({
                'price': {
                    'id': str(item.price_list_id),
                    'code': item.price_list.code,
                    'title': item.price_list.title,
                } if item.price_list else {},
                'price_value': item.price,
                'uom': {
                    'id': str(item.uom_using_id),
                    'code': item.uom_using.code,
                    'title': item.uom_using.title
                } if item.uom_using else {}
            })
        return price_list


class BOMProductToolListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
            'id',
            'code',
            'title',
            'general_uom_group'
        )


# BEGIN
class BOMListSerializer(AbstractListSerializerModel):
    product = serializers.SerializerMethodField()

    class Meta:
        model = BOM
        fields = (
            'id',
            'code',
            'bom_type',
            'product',
            'sum_price',
            'sum_time'
        )

    @classmethod
    def get_product(cls, obj):
        return {
            'id': str(obj.product_id),
            'code': obj.product.code,
            'title': obj.product.title
        } if obj.product else {}


class BOMCreateSerializer(AbstractCreateSerializerModel):
    bom_type = serializers.IntegerField()
    product = serializers.UUIDField()
    sum_price = serializers.FloatField()
    sum_time = serializers.FloatField()
    bom_process_data = serializers.ListField()
    bom_summary_process_data = serializers.ListField()
    bom_material_component_data = serializers.ListField()
    bom_tool_data = serializers.ListField()

    class Meta:
        model = BOM
        fields = (
            'bom_type',
            'product',
            'sum_price',
            'sum_time',
            'bom_process_data',
            'bom_summary_process_data',
            'bom_material_component_data',
            'bom_tool_data',
        )

    @classmethod
    def validate_bom_type(cls, value):
        if value in [0, 1, 2, 3]:
            return value
        raise serializers.ValidationError({'bom_type': "Bom type is not valid"})

    @classmethod
    def validate_product(cls, value):
        try:
            return Product.objects.get(id=value)
        except Product.DoesNotExist:
            raise serializers.ValidationError({'product': "Product is not exist"})

    @classmethod
    def validate_sum_price(cls, value):
        if value and value > 0:
            return value
        raise serializers.ValidationError({'sum_price': "Sum price is not valid"})

    @classmethod
    def validate_sum_time(cls, value):
        if value and value > 0:
            return value
        raise serializers.ValidationError({'sum_time': "Sum time is not valid"})

    @classmethod
    def validate_bom_process_data(cls, bom_process_data):
        try:
            for item in bom_process_data:
                if all([
                    item.get('task_name'),
                    float(item.get('quantity', 0)) > 0,
                    float(item.get('unit_price', 0)) > 0
                ]):
                    item['labor'] = Expense.objects.get(id=item.get('labor'))
                    item['uom'] = UnitOfMeasure.objects.get(id=item.get('uom'))
                    item['subtotal_price'] = float(item['quantity']) * float(item['unit_price'])
                else:
                    raise serializers.ValidationError({'bom_process_data': "Process data is missing field"})
            return bom_process_data
        except Product.DoesNotExist:
            raise serializers.ValidationError({'bom_process_data': "Process data is not valid"})

    @classmethod
    def validate_bom_summary_process_data(cls, bom_summary_process_data):
        try:
            for item in bom_summary_process_data:
                if all([
                    float(item.get('quantity', 0)) > 0,
                    float(item.get('unit_price', 0)) > 0
                ]):
                    item['labor'] = Expense.objects.get(id=item.get('labor'))
                    item['uom'] = UnitOfMeasure.objects.get(id=item.get('uom'))
                    item['subtotal_price'] = float(item['quantity']) * float(item['unit_price'])
                else:
                    raise serializers.ValidationError({'bom_process_data': "Summary process data is missing field"})
            return bom_summary_process_data
        except Product.DoesNotExist:
            raise serializers.ValidationError({'bom_process_data': "Summary process data is not valid"})

    @classmethod
    def validate_bom_material_component_data(cls, bom_material_component_data):
        try:
            for item in bom_material_component_data:
                if all([
                    float(item.get('quantity', 0)) > 0,
                    float(item.get('unit_price', 0)) > 0,
                    item.get('bom_process_order')
                ]):
                    item['material'] = Product.objects.get(id=item.get('material')) if item.get('material') else None
                    item['uom'] = UnitOfMeasure.objects.get(id=item.get('uom'))
                    item['subtotal_price'] = float(item['quantity']) * float(item['unit_price'])
                else:
                    raise serializers.ValidationError({'bom_process_data': "Material/component data is missing field"})
            return bom_material_component_data
        except Product.DoesNotExist:
            raise serializers.ValidationError({'bom_process_data': "Material/component data is not valid"})

    @classmethod
    def validate_bom_tool_data(cls, bom_tool_data):
        try:
            for item in bom_tool_data:
                if all([float(item.get('quantity', 0)) > 0, item.get('bom_process_order')]):
                    item['tool'] = Product.objects.get(id=item.get('tool'))
                    item['uom'] = UnitOfMeasure.objects.get(id=item.get('uom'))
                else:
                    raise serializers.ValidationError({'bom_tool_data': "Tool data is missing field"})
            return bom_tool_data
        except Product.DoesNotExist:
            raise serializers.ValidationError({'bom_tool_data': "Tool data is not valid"})

    @decorator_run_workflow
    def create(self, validated_data):
        bom_process_data = validated_data.get('bom_process_data')
        bom_summary_process_data = validated_data.get('bom_summary_process_data')
        bom_material_component_data = validated_data.get('bom_material_component_data')
        bom_tool_data = validated_data.get('bom_tool_data')
        validated_data.pop('bom_process_data', [])
        validated_data.pop('bom_summary_process_data', [])
        validated_data.pop('bom_material_component_data', [])
        validated_data.pop('bom_tool_data', [])

        instance = BOM.objects.create(**validated_data)
        BOMCommonFunction.create_bom_process_data(bom_process_data, instance)
        BOMCommonFunction.create_bom_summary_process_data(bom_summary_process_data, instance)
        BOMCommonFunction.create_bom_material_component_data(bom_material_component_data, instance)
        BOMCommonFunction.create_bom_tool_data(bom_tool_data, instance)
        return instance


class BOMDetailSerializer(AbstractDetailSerializerModel):
    product = serializers.SerializerMethodField()
    bom_process_data = serializers.SerializerMethodField()
    bom_summary_process_data = serializers.SerializerMethodField()
    bom_material_component_data = serializers.SerializerMethodField()
    bom_tool_data = serializers.SerializerMethodField()

    class Meta:
        model = BOM
        fields = (
            'id',
            'code',
            'bom_type',
            'product',
            'sum_price',
            'sum_time',
            'bom_process_data',
            'bom_summary_process_data',
            'bom_material_component_data',
            'bom_tool_data'
        )

    @classmethod
    def get_product(cls, obj):
        return {
            'id': str(obj.product_id),
            'code': obj.product.code,
            'title': obj.product.title
        } if obj.product else {}

    @classmethod
    def get_bom_process_data(cls, obj):
        bom_process_data = []
        for process_item in obj.bom_process_bom.all():
            bom_process_data.append({
                'order': process_item.order,
                'task_name': process_item.task_name,
                'labor': {
                    'id': str(process_item.labor_id),
                    'code': process_item.labor.code,
                    'title': process_item.labor.title,
                    'price_list': [{
                        'price': {
                            'id': str(item.price_id),
                            'code': item.price.code,
                            'title': item.price.title,
                        } if item.price else {},
                        'price_value': item.price_value,
                        'uom': {
                            'id': str(item.uom_id),
                            'code': item.uom.code,
                            'title': item.uom.title
                        } if item.uom else {}
                    } for item in process_item.labor.expense.all()]
                } if process_item.labor else {},
                'quantity': process_item.quantity,
                'uom': {
                    'id': str(process_item.uom_id),
                    'code': process_item.uom.code,
                    'title': process_item.uom.title,
                    'ratio': process_item.uom.ratio,
                    'group_id': str(process_item.uom.group_id)
                } if process_item.uom else {},
                'unit_price': process_item.unit_price,
                'subtotal_price': process_item.subtotal_price,
                'note': process_item.note,
            })
        return bom_process_data

    @classmethod
    def get_bom_summary_process_data(cls, obj):
        bom_summary_process_data = []
        for summary_process_item in obj.bom_summary_process_bom.all():
            bom_summary_process_data.append({
                'order': summary_process_item.order,
                'labor': {
                    'id': str(summary_process_item.labor_id),
                    'code': summary_process_item.labor.code,
                    'title': summary_process_item.labor.title,
                } if summary_process_item.labor else {},
                'quantity': summary_process_item.quantity,
                'uom': {
                    'id': str(summary_process_item.uom_id),
                    'code': summary_process_item.uom.code,
                    'title': summary_process_item.uom.title,
                    'ratio': summary_process_item.uom.ratio,
                    'group_id': str(summary_process_item.uom.group_id)
                } if summary_process_item.uom else {},
                'unit_price': summary_process_item.unit_price,
                'subtotal_price': summary_process_item.subtotal_price,
            })
        return bom_summary_process_data

    @classmethod
    def get_bom_material_component_data(cls, obj):
        bom_material_component_data = []
        for material_component_item in obj.bom_material_component_bom.all():
            bom_material_component_data.append({
                'order': material_component_item.order,
                'bom_process_order': material_component_item.bom_process_order,
                'material': {
                    'id': str(material_component_item.material_id),
                    'code': material_component_item.material.code,
                    'title': material_component_item.material.title,
                    'price_list': [{
                        'price': {
                            'id': str(item.price_list_id),
                            'code': item.price_list.code,
                            'title': item.price_list.title,
                        } if item.price_list else {},
                        'price_value': item.price,
                        'uom': {
                            'id': str(item.uom_using_id),
                            'code': item.uom_using.code,
                            'title': item.uom_using.title
                        } if item.uom_using else {}
                    } for item in material_component_item.material.product_price_product.all()]
                } if material_component_item.material else {},
                'quantity': material_component_item.quantity,
                'uom': {
                    'id': str(material_component_item.uom_id),
                    'code': material_component_item.uom.code,
                    'title': material_component_item.uom.title,
                    'ratio': material_component_item.uom.ratio,
                    'group_id': str(material_component_item.uom.group_id)
                } if material_component_item.uom else {},
                'unit_price': material_component_item.unit_price,
                'subtotal_price': material_component_item.subtotal_price,
                'disassemble': material_component_item.disassemble,
                'note': material_component_item.note
            })
        return bom_material_component_data

    @classmethod
    def get_bom_tool_data(cls, obj):
        bom_tool_data = []
        for tool_item in obj.bom_tool_bom.all():
            bom_tool_data.append({
                'order': tool_item.order,
                'bom_process_order': tool_item.bom_process_order,
                'tool': {
                    'id': str(tool_item.tool_id),
                    'code': tool_item.tool.code,
                    'title': tool_item.tool.title
                } if tool_item.tool else {},
                'quantity': tool_item.quantity,
                'uom': {
                    'id': str(tool_item.uom_id),
                    'code': tool_item.uom.code,
                    'title': tool_item.uom.title,
                    'ratio': tool_item.uom.ratio,
                    'group_id': str(tool_item.uom.group_id)
                } if tool_item.uom else {},
                'note': tool_item.note
            })
        return bom_tool_data


class BOMUpdateSerializer(AbstractCreateSerializerModel):

    class Meta:
        model = BOM
        fields = '__all__'

    @decorator_run_workflow
    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance


class BOMCommonFunction:
    @classmethod
    def create_bom_process_data(cls, bom_process_data, bom_obj):
        bulk_info = []
        for item in bom_process_data:
            bulk_info.append(BOMProcess(bom=bom_obj, **item))
        BOMProcess.objects.filter(bom=bom_obj).delete()
        BOMProcess.objects.bulk_create(bulk_info)
        print('bom_process_data --- ok')
        return True

    @classmethod
    def create_bom_summary_process_data(cls, bom_summary_process_data, bom_obj):
        bulk_info = []
        for item in bom_summary_process_data:
            bulk_info.append(BOMSummaryProcess(bom=bom_obj, **item))
        BOMSummaryProcess.objects.filter(bom=bom_obj).delete()
        BOMSummaryProcess.objects.bulk_create(bulk_info)
        print('bom_summary_process_data --- ok')
        return True

    @classmethod
    def create_bom_material_component_data(cls, bom_material_component_data, bom_obj):
        bulk_info = []
        for item in bom_material_component_data:
            bom_process_obj = bom_obj.bom_process_bom.filter(order=item.get('bom_process_order')).first()
            if bom_process_obj:
                bulk_info.append(BOMMaterialComponent(bom=bom_obj, bom_process=bom_process_obj, **item))
        BOMMaterialComponent.objects.filter(bom=bom_obj).delete()
        BOMMaterialComponent.objects.bulk_create(bulk_info)
        print('bom_material_component_data --- ok')
        return True

    @classmethod
    def create_bom_tool_data(cls, bom_tool_data, bom_obj):
        bulk_info = []
        for item in bom_tool_data:
            bom_process_obj = bom_obj.bom_process_bom.filter(order=item.get('bom_process_order')).first()
            if bom_process_obj:
                bulk_info.append(BOMTool(bom=bom_obj, bom_process=bom_process_obj, **item))
        BOMTool.objects.filter(bom=bom_obj).delete()
        BOMTool.objects.bulk_create(bulk_info)
        print('bom_tool_data --- ok')
        return True
