from rest_framework import serializers
from apps.core.workflow.tasks import decorator_run_workflow
from apps.masterdata.saledata.models import Product, Expense, UnitOfMeasure
from apps.sales.opportunity.models import Opportunity
from apps.sales.production.models import (
    BOM, BOMProcess, BOMSummaryProcess, BOMMaterialComponent, BOMTool, BOMReplacementMaterialComponent
)
from apps.shared import AbstractDetailSerializerModel, AbstractCreateSerializerModel, AbstractListSerializerModel


class ProductListForBOMSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
            'id',
            'code',
            'title'
        )


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
    bom_id = serializers.SerializerMethodField()
    is_opp_bom = serializers.SerializerMethodField()
    inventory_uom = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            'id',
            'code',
            'title',
            'has_bom',
            'bom_id',
            'is_opp_bom',
            'inventory_uom',
            'general_uom_group',
            'standard_price'
        )

    @classmethod
    def get_bom_id(cls, obj):
        bom = obj.bom_product.first()
        return str(bom.id) if bom else None

    @classmethod
    def get_is_opp_bom(cls, obj):
        bom = obj.bom_product.first()
        if bom:
            return bool(bom.opportunity)
        return False

    @classmethod
    def get_inventory_uom(cls, obj):
        return {
            'id': str(obj.inventory_uom_id),
            'code': obj.inventory_uom.code,
            'title': obj.inventory_uom.title
        } if obj.inventory_uom else {}


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
    opportunity = serializers.SerializerMethodField()
    employee_created = serializers.SerializerMethodField()
    employee_inherit = serializers.SerializerMethodField()

    class Meta:
        model = BOM
        fields = (
            'id',
            'code',
            'title',
            'bom_type',
            'for_outsourcing',
            'product',
            'opportunity',
            'employee_created',
            'employee_inherit',
            'date_created',
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

    @classmethod
    def get_opportunity(cls, obj):
        return {
            'id': str(obj.opportunity_id),
            'code': obj.opportunity.code,
            'title': obj.opportunity.title
        } if obj.opportunity else {}

    @classmethod
    def get_employee_created(cls, obj):
        return {
            'id': obj.employee_created_id,
            'code': obj.employee_created.code,
            'full_name': obj.employee_created.get_full_name(2),
            'group': {
                'id': obj.employee_created.group_id,
                'title': obj.employee_created.group.title,
                'code': obj.employee_created.group.code
            } if obj.employee_created.group else {}
        } if obj.employee_created else {}

    @classmethod
    def get_employee_inherit(cls, obj):
        return {
            'id': obj.employee_inherit_id,
            'code': obj.employee_inherit.code,
            'full_name': obj.employee_inherit.get_full_name(2),
            'group': {
                'id': obj.employee_inherit.group_id,
                'title': obj.employee_inherit.group.title,
                'code': obj.employee_inherit.group.code
            } if obj.employee_inherit.group else {}
        } if obj.employee_inherit else {}


class BOMCreateSerializer(AbstractCreateSerializerModel):
    bom_type = serializers.IntegerField()
    opportunity_id = serializers.UUIDField(required=False, allow_null=True)
    product_id = serializers.UUIDField()
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
            'for_outsourcing',
            'opportunity_id',
            'product_id',
            'sum_price',
            'sum_time',
            'bom_process_data',
            'bom_summary_process_data',
            'bom_material_component_data',
            'bom_tool_data',
        )

    def validate(self, validate_data):
        BOMCommonFunction.validate_bom_type(validate_data)
        BOMCommonFunction.validate_opportunity_id(validate_data)
        BOMCommonFunction.validate_product_id(validate_data)
        BOMCommonFunction.validate_sum_price(validate_data)
        BOMCommonFunction.validate_sum_time(validate_data)
        BOMCommonFunction.validate_bom_process_data(validate_data)
        BOMCommonFunction.validate_bom_summary_process_data(validate_data)
        BOMCommonFunction.validate_bom_material_component_data(validate_data)
        BOMCommonFunction.validate_bom_tool_data(validate_data)

        if validate_data['bom_type'] == 4 and not validate_data.get('opportunity_id'):
            raise serializers.ValidationError({'opportunity_id': "Opportunity is required"})

        print('*validate done')
        return validate_data

    @decorator_run_workflow
    def create(self, validated_data):
        bom_process_data = validated_data.pop('bom_process_data', [])
        bom_summary_process_data = validated_data.pop('bom_summary_process_data', [])
        bom_material_component_data = validated_data.pop('bom_material_component_data', [])
        bom_tool_data = validated_data.pop('bom_tool_data', [])

        instance = BOM.objects.create(**validated_data)
        BOMCommonFunction.create_bom_process_data(bom_process_data, instance)
        BOMCommonFunction.create_bom_summary_process_data(bom_summary_process_data, instance)
        BOMCommonFunction.create_bom_material_component_data(bom_material_component_data, instance)
        BOMCommonFunction.create_bom_tool_data(bom_tool_data, instance)
        return instance


class BOMDetailSerializer(AbstractDetailSerializerModel):
    product = serializers.SerializerMethodField()
    opportunity = serializers.SerializerMethodField()
    bom_process_data = serializers.SerializerMethodField()
    bom_summary_process_data = serializers.SerializerMethodField()
    bom_material_component_data = serializers.SerializerMethodField()
    bom_tool_data = serializers.SerializerMethodField()
    employee_inherit = serializers.SerializerMethodField()

    class Meta:
        model = BOM
        fields = (
            'id',
            'code',
            'bom_type',
            'for_outsourcing',
            'product',
            'opportunity',
            'sum_price',
            'sum_time',
            'bom_process_data',
            'bom_summary_process_data',
            'bom_material_component_data',
            'bom_tool_data',
            'employee_inherit',
        )

    @classmethod
    def get_product(cls, obj):
        return obj.product_data

    @classmethod
    def get_opportunity(cls, obj):
        return obj.opp_data

    @classmethod
    def get_bom_process_data(cls, obj):
        bom_process_data = []
        for item in obj.bom_process_bom.all():
            bom_process_data.append({
                'order': item.order,
                'task_name': item.task_name,
                'labor': {
                    'id': str(item.labor_id),
                    'code': item.labor.code,
                    'title': item.labor.title,
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
                    } for item in item.labor.expense.all()],
                    'expense_item': {
                        'id': str(item.labor.expense_item.id),
                        'title': item.labor.expense_item.title,
                        'code': item.labor.expense_item.code
                    }
                } if item.labor else {},
                'quantity': item.quantity,
                'uom': item.uom_data,
                'unit_price': item.unit_price,
                'subtotal_price': item.subtotal_price,
                'note': item.note,
            })
        return bom_process_data

    @classmethod
    def get_bom_summary_process_data(cls, obj):
        bom_summary_process_data = []
        for item in obj.bom_summary_process_bom.all():
            bom_summary_process_data.append({
                'order': item.order,
                'labor': item.labor_data,
                'quantity': item.quantity,
                'uom': item.uom_data,
                'unit_price': item.unit_price,
                'subtotal_price': item.subtotal_price,
            })
        return bom_summary_process_data

    @classmethod
    def get_bom_material_component_data(cls, obj):
        bom_material_component_data = []
        if not obj.for_outsourcing:
            for item in obj.bom_material_component_bom.filter(for_outsourcing=False):
                bom_material_component_data.append({
                    'order': item.order,
                    'bom_process_order': item.bom_process_order,
                    'material': item.material_data,
                    'quantity': item.quantity,
                    'standard_price': item.standard_price,
                    'subtotal_price': item.subtotal_price,
                    'uom': item.uom_data,
                    'disassemble': item.disassemble,
                    'note': item.note,
                    'replacement_data': item.replacement_data
                })
        else:
            for item in obj.bom_material_component_bom.filter(for_outsourcing=True):
                bom_material_component_data.append({
                    'order': item.order,
                    'material': item.material_data,
                    'quantity': item.quantity,
                    'standard_price': item.standard_price,
                    'subtotal_price': item.subtotal_price,
                    'uom': item.uom_data,
                    'disassemble': item.disassemble,
                    'note': item.note,
                    'replacement_data': item.replacement_data
                })
        return bom_material_component_data

    @classmethod
    def get_bom_tool_data(cls, obj):
        bom_tool_data = []
        for item in obj.bom_tool_bom.all():
            bom_tool_data.append({
                'order': item.order,
                'bom_process_order': item.bom_process_order,
                'tool': item.tool_data,
                'quantity': item.quantity,
                'uom': item.uom_data,
                'note': item.note
            })
        return bom_tool_data

    @classmethod
    def get_employee_inherit(cls, obj):
        return obj.employee_inherit.get_detail_minimal() if obj.employee_inherit else {}


class BOMUpdateSerializer(AbstractCreateSerializerModel):
    bom_type = serializers.IntegerField()
    opportunity_id = serializers.UUIDField(required=False, allow_null=True)
    product_id = serializers.UUIDField()
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
            'for_outsourcing',
            'opportunity_id',
            'product_id',
            'sum_price',
            'sum_time',
            'bom_process_data',
            'bom_summary_process_data',
            'bom_material_component_data',
            'bom_tool_data',
        )

    def validate(self, validate_data):
        BOMCommonFunction.validate_bom_type(validate_data)
        BOMCommonFunction.validate_opportunity_id(validate_data)
        BOMCommonFunction.validate_product_id(validate_data)
        BOMCommonFunction.validate_sum_price(validate_data)
        BOMCommonFunction.validate_sum_time(validate_data)
        BOMCommonFunction.validate_bom_process_data(validate_data)
        BOMCommonFunction.validate_bom_summary_process_data(validate_data)
        BOMCommonFunction.validate_bom_material_component_data(validate_data)
        BOMCommonFunction.validate_bom_tool_data(validate_data)
        print('*validate done')
        return validate_data

    @decorator_run_workflow
    def update(self, instance, validated_data):
        bom_process_data = validated_data.pop('bom_process_data', [])
        bom_summary_process_data = validated_data.pop('bom_summary_process_data', [])
        bom_material_component_data = validated_data.pop('bom_material_component_data', [])
        bom_tool_data = validated_data.pop('bom_tool_data', [])

        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()

        BOMCommonFunction.create_bom_process_data(bom_process_data, instance)
        BOMCommonFunction.create_bom_summary_process_data(bom_summary_process_data, instance)
        BOMCommonFunction.create_bom_material_component_data(bom_material_component_data, instance)
        BOMCommonFunction.create_bom_tool_data(bom_tool_data, instance)
        return instance


class BOMCommonFunction:
    @classmethod
    def validate_bom_type(cls, validate_data):
        bom_type = validate_data.get('bom_type')
        if bom_type in [0, 1, 2, 3, 4]:
            validate_data['bom_type'] = bom_type
            print('1. validate_bom_type --- ok')
            return True
        raise serializers.ValidationError({'bom_type': "Bom type is not valid"})

    @classmethod
    def validate_opportunity_id(cls, validate_data):
        if validate_data.get('opportunity_id'):
            try:
                opportunity_obj = Opportunity.objects.get(id=validate_data.get('opportunity_id'))
                validate_data['opportunity_id'] = str(opportunity_obj.id)
                validate_data['employee_inherit'] = opportunity_obj.employee_inherit
                validate_data['opp_data'] = {
                    'id': str(opportunity_obj.id),
                    'code': opportunity_obj.code,
                    'title': opportunity_obj.title,
                    'sale_person': {
                        'id': str(opportunity_obj.employee_inherit_id),
                        'code': opportunity_obj.employee_inherit.code,
                        'full_name': opportunity_obj.employee_inherit.get_full_name(2),
                    } if opportunity_obj.employee_inherit else {}
                } if opportunity_obj else {}
            except Opportunity.DoesNotExist:
                raise serializers.ValidationError({'opportunity_id': "Opportunity does not exist"})
        print('2. validate_opportunity_id --- ok')
        return True

    @classmethod
    def validate_product_id(cls, validate_data):
        try:
            product_obj = Product.objects.get(id=validate_data.get('product_id'))
            if product_obj.has_bom:
                raise serializers.ValidationError({'product': "This product is mapped with BOM"})
            validate_data['product_id'] = str(product_obj.id)
            validate_data['title'] = f"BOM - {product_obj.title}"
            validate_data['product_data'] = {
                'id': str(product_obj.id),
                'code': product_obj.code,
                'title': product_obj.title
            } if product_obj else {}
            print('3. validate_product --- ok')
            return True
        except Product.DoesNotExist:
            raise serializers.ValidationError({'product': "Product does not exist"})

    @classmethod
    def validate_sum_price(cls, validate_data):
        sum_price = validate_data.get('sum_price', 0)
        if sum_price >= 0:
            validate_data['sum_price'] = sum_price
            print('4. validate_sum_price --- ok')
            return True
        raise serializers.ValidationError({'sum_price': "Sum price is not valid"})

    @classmethod
    def validate_sum_time(cls, validate_data):
        sum_time = validate_data.get('sum_time')
        if sum_time >= 0:
            validate_data['sum_time'] = sum_time
            print('5. validate_sum_time --- ok')
            return True
        raise serializers.ValidationError({'sum_time': "Sum time is not valid"})

    @classmethod
    def validate_bom_process_data(cls, validate_data):
        if not validate_data.get('for_outsourcing'):
            bom_process_data = validate_data.get('bom_process_data')
            try:
                for item in bom_process_data:
                    if all([
                        item.get('task_name'),
                        float(item.get('quantity', 0)) > 0,
                        float(item.get('unit_price', 0)) > 0
                    ]):
                        uom_obj = UnitOfMeasure.objects.get(id=item.get('uom_id'))
                        item['labor_id'] = str(Expense.objects.get(id=item.get('labor_id')).id)
                        item['uom_id'] = str(uom_obj.id)
                        item['uom_data'] = {
                            'id': str(uom_obj.id),
                            'code': uom_obj.code,
                            'title': uom_obj.title,
                            'ratio': uom_obj.ratio,
                            'group_id': str(uom_obj.group_id)
                        } if uom_obj else {}
                        item['subtotal_price'] = float(item['quantity']) * float(item['unit_price'])
                    else:
                        raise serializers.ValidationError({'bom_process_data': "Process data is missing field"})
                validate_data['bom_process_data'] = bom_process_data
            except Exception as err:
                print(err)
                raise serializers.ValidationError({'bom_process_data': "Process data is not valid."})
        print('6. validate_bom_process_data --- ok')
        return True

    @classmethod
    def validate_bom_summary_process_data(cls, validate_data):
        if not validate_data.get('for_outsourcing'):
            bom_summary_process_data = validate_data.get('bom_summary_process_data')
            try:
                for item in bom_summary_process_data:
                    if all([float(item.get('quantity', 0)) > 0, float(item.get('unit_price', 0)) > 0]):
                        labor_obj = Expense.objects.get(id=item.get('labor_id'))
                        uom_obj = UnitOfMeasure.objects.get(id=item.get('uom_id'))
                        item['labor_id'] = str(labor_obj.id)
                        item['labor_data'] = {
                            'id': str(labor_obj.id),
                            'code': labor_obj.code,
                            'title': labor_obj.title,
                        } if labor_obj else {}
                        item['uom_id'] = str(uom_obj.id)
                        item['uom_data'] = {
                            'id': str(uom_obj.id),
                            'code': uom_obj.code,
                            'title': uom_obj.title,
                            'ratio': uom_obj.ratio,
                            'group_id': str(uom_obj.group_id)
                        } if uom_obj else {}
                        item['subtotal_price'] = float(item['quantity']) * float(item['unit_price'])
                    else:
                        raise serializers.ValidationError({'bom_process_data': "Summary process data is missing field"})
                validate_data['bom_summary_process_data'] = bom_summary_process_data
            except Exception as err:
                print(err)
                raise serializers.ValidationError({'bom_process_data': "Summary process data is not valid"})
        print('7. validate_bom_summary_process_data --- ok')
        return True

    @classmethod
    def validate_bom_replacement_data(cls, material_item):
        for replacement_item in material_item.get('replacement_data', []):
            if float(replacement_item.get('quantity', 0)) > 0:
                material_obj = Product.objects.get(id=replacement_item.get('material_id'))
                uom_obj = UnitOfMeasure.objects.get(id=replacement_item.get('uom_id'))
                replacement_item['material_id'] = str(material_obj.id)
                replacement_item['uom_id'] = str(uom_obj.id)
                replacement_item['material_data'] = {
                    'id': str(material_obj.id),
                    'code': material_obj.code,
                    'title': material_obj.title
                } if material_obj else {}
                replacement_item['uom_data'] = {
                    'id': str(uom_obj.id),
                    'code': uom_obj.code,
                    'title': uom_obj.title,
                    'group_id': str(uom_obj.group_id),
                } if uom_obj else {}
            else:
                raise serializers.ValidationError({'quantity': "Replacement material quantity must be > 0"})
        return True

    @classmethod
    def validate_bom_material_component_data(cls, validate_data):
        bom_material_component_data = validate_data.get('bom_material_component_data')
        try:
            for material_item in bom_material_component_data:
                if all([
                    not validate_data.get('for_outsourcing'),
                    validate_data.get('bom_type') != 2,
                    not material_item.get('bom_process_order')
                ]):
                    raise serializers.ValidationError({'bom_process_order': "Process order is required."})
                if float(material_item.get('quantity', 0)) > 0:
                    material_obj = Product.objects.get(id=material_item.get('material_id'))
                    uom_obj = UnitOfMeasure.objects.get(id=material_item.get('uom_id'))
                    material_item['material_id'] = str(material_obj.id)
                    material_item['material_data'] = {
                        'id': str(material_obj.id),
                        'code': material_obj.code,
                        'title': material_obj.title
                    } if material_obj else {}
                    material_item['uom_id'] = str(uom_obj.id)
                    material_item['uom_data'] = {
                        'id': str(uom_obj.id),
                        'code': uom_obj.code,
                        'title': uom_obj.title,
                        'ratio': uom_obj.ratio,
                        'group_id': str(uom_obj.group_id)
                    } if uom_obj else {}
                    cls.validate_bom_replacement_data(material_item)
                else:
                    raise serializers.ValidationError({'quantity': "Material quantity must be > 0"})

            validate_data['bom_material_component_data'] = bom_material_component_data
        except Exception as err:
            print(err)
            raise serializers.ValidationError({'bom_process_data': "Material/component data is not valid"})
        print('8. validate_bom_material_component_data --- ok')
        return True

    @classmethod
    def validate_bom_tool_data(cls, validate_data):
        if not validate_data.get('for_outsourcing'):
            bom_tool_data = validate_data.get('bom_tool_data')
            try:
                for item in bom_tool_data:
                    if all([float(item.get('quantity', 0)) > 0, item.get('bom_process_order')]):
                        tool_obj = Product.objects.get(id=item.get('tool_id'))
                        uom_obj = UnitOfMeasure.objects.get(id=item.get('uom_id'))
                        item['tool_id'] = str(tool_obj.id)
                        item['tool_data'] = {
                            'id': str(tool_obj.id),
                            'code': tool_obj.code,
                            'title': tool_obj.title
                        } if tool_obj else {}
                        item['uom_id'] = str(uom_obj.id)
                        item['uom_data'] = {
                            'id': str(uom_obj.id),
                            'code': uom_obj.code,
                            'title': uom_obj.title,
                            'ratio': uom_obj.ratio,
                            'group_id': str(uom_obj.group_id)
                        } if uom_obj else {}
                    else:
                        raise serializers.ValidationError({'bom_tool_data': "Tool data is missing field"})
                validate_data['bom_tool_data'] = bom_tool_data
            except Exception as err:
                print(err)
                raise serializers.ValidationError({'bom_tool_data': "Tool data is not valid"})
        print('9. validate_bom_tool_data --- ok')
        return True

    @classmethod
    def create_bom_process_data(cls, bom_process_data, bom_obj):
        bulk_info = []
        for item in bom_process_data:
            bulk_info.append(BOMProcess(bom=bom_obj, **item))
        BOMProcess.objects.filter(bom=bom_obj).delete()
        BOMProcess.objects.bulk_create(bulk_info)
        print('10. create_bom_process_data --- ok')
        return True

    @classmethod
    def create_bom_summary_process_data(cls, bom_summary_process_data, bom_obj):
        bulk_info = []
        for item in bom_summary_process_data:
            bulk_info.append(BOMSummaryProcess(bom=bom_obj, **item))
        BOMSummaryProcess.objects.filter(bom=bom_obj).delete()
        BOMSummaryProcess.objects.bulk_create(bulk_info)
        print('11. create_bom_summary_process_data --- ok')
        return True

    @classmethod
    def create_bom_material_component_data(cls, bom_material_component_data, bom_obj):
        if not bom_obj.for_outsourcing:
            bulk_info = []
            for item in bom_material_component_data:
                bom_process_obj = bom_obj.bom_process_bom.filter(
                    order=item.get('bom_process_order')
                ).first() if bom_obj.bom_type != 2 else None
                bulk_info.append(BOMMaterialComponent(bom=bom_obj, bom_process=bom_process_obj, **item))
            BOMMaterialComponent.objects.filter(bom=bom_obj).delete()
            bom_material_component_records = BOMMaterialComponent.objects.bulk_create(bulk_info)
        else:
            bulk_info = []
            for item in bom_material_component_data:
                bulk_info.append(BOMMaterialComponent(bom=bom_obj, for_outsourcing=True, **item))
            BOMMaterialComponent.objects.filter(bom=bom_obj).delete()
            bom_material_component_records = BOMMaterialComponent.objects.bulk_create(bulk_info)
        print('12. create_bom_material_component_data --- ok')
        cls.create_bom_replacement_material_component_data(bom_obj, bom_material_component_records)
        return True

    @classmethod
    def create_bom_replacement_material_component_data(cls, bom_obj, bom_material_component_records):
        bulk_info = []
        for item in bom_material_component_records:
            for replacement_data in item.replacement_data:
                bulk_info.append(
                    BOMReplacementMaterialComponent(bom=bom_obj, replace_for_id=item.id, **replacement_data)
                )
        BOMReplacementMaterialComponent.objects.filter(bom=bom_obj).delete()
        BOMReplacementMaterialComponent.objects.bulk_create(bulk_info)
        print('13. create_bom_replacement_material_component_data --- ok')
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
        print('14. create_bom_tool_data --- ok')
        return True


# BOM use for production order/ work order
class BOMOrderListSerializer(AbstractDetailSerializerModel):
    bom_task = serializers.SerializerMethodField()
    bom_material = serializers.SerializerMethodField()
    bom_tool = serializers.SerializerMethodField()

    class Meta:
        model = BOM
        fields = (
            'id',
            'code',
            'bom_type',
            'for_outsourcing',
            'sum_price',
            'sum_time',
            'bom_task',
            'bom_material',
            'bom_tool',
            'sum_price',
        )

    @classmethod
    def get_bom_task(cls, obj):
        return [
            {
                'id': bom_task.id,
                'order': bom_task.order,
                'task_title': bom_task.task_name,
                'quantity_bom': bom_task.quantity,
                'uom_id': str(bom_task.uom_id),
                'uom_data': {
                    'id': str(bom_task.uom_id),
                    'code': bom_task.uom.code,
                    'title': bom_task.uom.title,
                    'ratio': bom_task.uom.ratio,
                    'group_id': str(bom_task.uom.group_id)
                } if bom_task.uom else {},
            } for bom_task in obj.bom_process_bom.all()
        ]

    @classmethod
    def get_bom_material(cls, obj):
        return [
            {
                'order': bom_material.order,
                'bom_task': {
                    'id': bom_material.bom_process_id, 'order': bom_material.bom_process.order
                } if bom_material.bom_process else {},
                'product_data': {
                    'id': str(bom_material.material_id),
                    'code': bom_material.material.code,
                    'title': bom_material.material.title,
                } if bom_material.material else {},
                'quantity_bom': bom_material.quantity,
                'uom_data': {
                    'id': str(bom_material.uom_id),
                    'code': bom_material.uom.code,
                    'title': bom_material.uom.title,
                    'ratio': bom_material.uom.ratio,
                    'group_id': str(bom_material.uom.group_id)
                } if bom_material.uom else {},
                'is_disassembly': bom_material.disassemble,
            } for bom_material in obj.bom_material_component_bom.all()
        ]

    @classmethod
    def get_bom_tool(cls, obj):
        return [
            {
                'order': bom_tool.order,
                'bom_task': {'id': bom_tool.bom_process_id, 'order': bom_tool.bom_process.order},
                'product_data': {
                    'id': str(bom_tool.tool_id),
                    'code': bom_tool.tool.code,
                    'title': bom_tool.tool.title
                } if bom_tool.tool else {},
                'quantity_bom': bom_tool.quantity,
                'uom': {
                    'id': str(bom_tool.uom_id),
                    'code': bom_tool.uom.code,
                    'title': bom_tool.uom.title,
                    'ratio': bom_tool.uom.ratio,
                    'group_id': str(bom_tool.uom.group_id)
                } if bom_tool.uom else {},
            } for bom_tool in obj.bom_tool_bom.all()
        ]
