from django.utils.datetime_safe import datetime
from rest_framework import serializers
from apps.core.base.models import Application
from apps.core.workflow.tasks import decorator_run_workflow
from apps.masterdata.saledata.models import Account, Contact, Product, UnitOfMeasure, Tax
from apps.sales.purchasing.models import PurchaseRequest, PurchaseRequestProduct, PurchaseRequestAttachmentFile
from apps.sales.saleorder.models import SaleOrder, SaleOrderProduct
from apps.sales.distributionplan.models import DistributionPlan
from apps.sales.serviceorder.models import ServiceOrder, ServiceOrderServiceDetail
from apps.shared import (
    REQUEST_FOR, PURCHASE_STATUS, AbstractCreateSerializerModel,
    AbstractDetailSerializerModel, AbstractListSerializerModel, SerializerCommonHandle, SerializerCommonValidate
)
from apps.shared.translations.sales import PurchaseRequestMsg


# sub
class PurchaseRequestProductSerializer(serializers.ModelSerializer):
    sale_order_product = serializers.UUIDField(required=False, allow_null=True)
    service_order_product = serializers.UUIDField(required=False, allow_null=True)
    product = serializers.UUIDField()
    uom = serializers.UUIDField()
    tax = serializers.UUIDField(required=False, allow_null=True)

    class Meta:
        model = PurchaseRequestProduct
        fields = (
            'sale_order_product',
            'service_order_product',
            'product',
            'uom',
            'tax',
            'quantity',
            'unit_price',
            'sub_total_price'
        )

    @classmethod
    def validate_sale_order_product(cls, value):
        if value:
            try:
                return SaleOrderProduct.objects.get(id=value)
            except SaleOrderProduct.DoesNotExist:
                raise serializers.ValidationError({'product': PurchaseRequestMsg.SALE_ORDER_PRODUCT_NOT_EXIST})
        return None

    @classmethod
    def validate_service_order_product(cls, value):
        if value:
            try:
                return ServiceOrderServiceDetail.objects.get(id=value)
            except ServiceOrderServiceDetail.DoesNotExist:
                raise serializers.ValidationError(
                    {'service_order_product': PurchaseRequestMsg.SERVICE_ORDER_PRODUCT_NOT_EXIST}
                )
        return None

    @classmethod
    def validate_product(cls, value):
        try:
            return Product.objects.get(id=value)
        except Product.DoesNotExist:
            raise serializers.ValidationError({'product': PurchaseRequestMsg.DOES_NOT_EXIST})

    @classmethod
    def validate_tax(cls, value):
        if value:
            try:
                return Tax.objects.get(id=value)
            except Tax.DoesNotExist:
                raise serializers.ValidationError({'tax': PurchaseRequestMsg.DOES_NOT_EXIST})
        return None

    @classmethod
    def validate_uom(cls, value):
        try:
            return UnitOfMeasure.objects.get(id=value)
        except UnitOfMeasure.DoesNotExist:
            raise serializers.ValidationError({'uom': PurchaseRequestMsg.DOES_NOT_EXIST})

    def validate(self, validate_data):
        if validate_data.get('unit_price', 0) < 0:
            raise serializers.ValidationError({'unit_price': PurchaseRequestMsg.GREATER_THAN_ZERO})

        if validate_data.get('sub_total_price', 0) < 0:
            raise serializers.ValidationError({'sub_total_price': PurchaseRequestMsg.GREATER_THAN_ZERO})

        if validate_data.get('quantity', 0) < 0:
            raise serializers.ValidationError({'quantity': PurchaseRequestMsg.GREATER_THAN_ZERO})

        if 'product' in validate_data:
            product_obj = validate_data.get('product')
            validate_data['product_data'] = {
                'id': str(product_obj.id),
                'code': product_obj.code,
                'title': product_obj.title,
                'description': product_obj.description,
            } if product_obj else {}

        if 'uom' in validate_data:
            uom_obj = validate_data.get('uom')
            validate_data['uom_data'] = {
                'id': str(uom_obj.id),
                'code': uom_obj.code,
                'title': uom_obj.title,
                'group_id': str(uom_obj.group_id)
            } if uom_obj else {}

        if 'tax' in validate_data:
            tax_obj = validate_data.get('tax')
            validate_data['tax_data'] = {
                'id': str(tax_obj.id),
                'code': tax_obj.code,
                'title': tax_obj.title,
                'rate': tax_obj.rate,
            } if tax_obj else {}

        return validate_data


# main
class PurchaseRequestListSerializer(AbstractListSerializerModel):
    sale_order = serializers.SerializerMethodField()
    distribution_plan = serializers.SerializerMethodField()
    service_order = serializers.SerializerMethodField()
    supplier = serializers.SerializerMethodField()
    request_for_string = serializers.SerializerMethodField()
    purchase_status_string = serializers.SerializerMethodField()
    employee_created = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseRequest
        fields = (
            'id',
            'code',
            'title',
            'request_for',
            'request_for_string',
            'sale_order',
            'distribution_plan',
            'service_order',
            'supplier',
            'delivered_date',
            'purchase_status',
            'purchase_status_string',
            'employee_created',
            'date_created'
        )

    @classmethod
    def get_request_for_string(cls, obj):
        return str(dict(REQUEST_FOR).get(obj.request_for))

    @classmethod
    def get_sale_order(cls, obj):
        return obj.sale_order_data

    @classmethod
    def get_distribution_plan(cls, obj):
        return obj.distribution_plan_data

    @classmethod
    def get_service_order(cls, obj):
        return obj.service_order_data

    @classmethod
    def get_supplier(cls, obj):
        return obj.supplier_data

    @classmethod
    def get_purchase_status_string(cls, obj):
        return str(dict(PURCHASE_STATUS).get(obj.purchase_status))

    @classmethod
    def get_employee_created(cls, obj):
        return obj.employee_created.get_detail_with_group() if obj.employee_created else {}


class PurchaseRequestCreateSerializer(AbstractCreateSerializerModel):
    title = serializers.CharField(max_length=150)
    sale_order = serializers.UUIDField(required=False, allow_null=True)
    distribution_plan = serializers.UUIDField(required=False, allow_null=True)
    service_order = serializers.UUIDField(required=False, allow_null=True)
    supplier = serializers.UUIDField(required=True)
    contact = serializers.UUIDField(required=True)
    purchase_request_product_datas = PurchaseRequestProductSerializer(many=True)
    note = serializers.CharField(allow_blank=True, allow_null=True)
    attachment = serializers.ListSerializer(child=serializers.CharField(), required=False)

    class Meta:
        model = PurchaseRequest
        fields = (
            'title',
            'supplier',
            'contact',
            'request_for',
            'sale_order',
            'distribution_plan',
            'service_order',
            'delivered_date',
            'note',
            'purchase_request_product_datas',
            'pretax_amount',
            'taxes',
            'total_price',
            'attachment'
        )

    @classmethod
    def validate_supplier(cls, value):
        try:
            return Account.objects.get_on_company(id=value, is_supplier_account=True)
        except Account.DoesNotExist:
            raise serializers.ValidationError({'supplier': PurchaseRequestMsg.DOES_NOT_EXIST})

    @classmethod
    def validate_contact(cls, value):
        try:
            return Contact.objects.get_on_company(id=value)
        except Contact.DoesNotExist:
            raise serializers.ValidationError({'contact': PurchaseRequestMsg.DOES_NOT_EXIST})

    @classmethod
    def validate_sale_order(cls, value):
        if value:
            try:
                return SaleOrder.objects.get_on_company(id=value)
            except SaleOrder.DoesNotExist:
                raise serializers.ValidationError({'sale_order': PurchaseRequestMsg.DOES_NOT_EXIST})
        return None

    @classmethod
    def validate_distribution_plan(cls, value):
        if value:
            try:
                distribution_plan_obj = DistributionPlan.objects.get_on_company(id=value)
                if distribution_plan_obj.end_date < datetime.now().date():
                    raise serializers.ValidationError({'distribution_plan': PurchaseRequestMsg.EXPIRED_DB})
                return distribution_plan_obj
            except DistributionPlan.DoesNotExist:
                raise serializers.ValidationError({'distribution_plan': PurchaseRequestMsg.DOES_NOT_EXIST})
        return None

    @classmethod
    def validate_service_order(cls, value):
        if value:
            try:
                return ServiceOrder.objects.get_on_company(id=value)
            except ServiceOrder.DoesNotExist:
                raise serializers.ValidationError({'service_order': PurchaseRequestMsg.DOES_NOT_EXIST})
        return None

    def validate_attachment(self, value):
        user = self.context.get('user', None)
        return SerializerCommonValidate.validate_attachment(
            user=user, model_cls=PurchaseRequestAttachmentFile, value=value,
        )

    def validate(self, validate_data):
        if validate_data.get('pretax_amount', 0) < 0:
            raise serializers.ValidationError({'pretax_amount': PurchaseRequestMsg.GREATER_THAN_ZERO})

        if validate_data.get('taxes', 0) < 0:
            raise serializers.ValidationError({'taxes': PurchaseRequestMsg.GREATER_THAN_ZERO})

        if validate_data.get('total_price', 0) < 0:
            raise serializers.ValidationError({'total_price': PurchaseRequestMsg.GREATER_THAN_ZERO})

        if 'supplier' in validate_data:
            supplier_obj = validate_data.get('supplier')
            validate_data['supplier_data'] = {
                'id': str(supplier_obj.id),
                'name': supplier_obj.name,
                'code': supplier_obj.code,
                'tax_code': supplier_obj.tax_code,
            } if supplier_obj else {}

        if 'contact' in validate_data:
            contact_obj = validate_data.get('contact')
            validate_data['contact_data'] = {
                'id': str(contact_obj.id),
                'code': contact_obj.code,
                'fullname': contact_obj.fullname,
            } if contact_obj else {}

        if 'sale_order' in validate_data:
            sale_order_obj = validate_data.get('sale_order')
            validate_data['sale_order_data'] = {
                'id': str(sale_order_obj.id),
                'code': sale_order_obj.code,
                'title': sale_order_obj.title,
            } if sale_order_obj else {}

        if 'distribution_plan' in validate_data:
            distribution_plan_obj = validate_data.get('distribution_plan')
            validate_data['distribution_plan_data'] = {
                'id': str(distribution_plan_obj.id),
                'code': distribution_plan_obj.code,
                'title': distribution_plan_obj.title,
            } if distribution_plan_obj else {}

        if 'service_order' in validate_data:
            service_order_obj = validate_data.get('service_order')
            validate_data['service_order_data'] = {
                'id': str(service_order_obj.id),
                'code': service_order_obj.code,
                'title': service_order_obj.title,
            } if service_order_obj else {}

        return validate_data

    @decorator_run_workflow
    def create(self, validated_data):
        attachment_list = validated_data.pop('attachment', [])
        data_item_list = validated_data.pop('purchase_request_product_datas', [])

        purchase_request_obj = PurchaseRequest.objects.create(**validated_data)

        PurchaseRequestCommonFunction.create_items_mapped(purchase_request_obj, data_item_list)
        PurchaseRequestCommonFunction.create_files_mapped(purchase_request_obj, attachment_list)

        return purchase_request_obj


class PurchaseRequestDetailSerializer(AbstractDetailSerializerModel):
    sale_order = serializers.SerializerMethodField()
    distribution_plan = serializers.SerializerMethodField()
    service_order = serializers.SerializerMethodField()
    supplier = serializers.SerializerMethodField()
    purchase_status = serializers.SerializerMethodField()
    contact = serializers.SerializerMethodField()
    purchase_request_product_datas = serializers.SerializerMethodField()
    attachment = serializers.SerializerMethodField()
    employee_inherit = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseRequest
        fields = (
            'id',
            'title',
            'code',
            'request_for',
            'supplier',
            'contact',
            'delivered_date',
            'purchase_status',
            'note',
            'sale_order',
            'distribution_plan',
            'service_order',
            'purchase_request_product_datas',
            'pretax_amount',
            'taxes',
            'total_price',
            'attachment',
            'employee_inherit',
        )

    @classmethod
    def get_sale_order(cls, obj):
        return obj.sale_order_data

    @classmethod
    def get_distribution_plan(cls, obj):
        return obj.distribution_plan_data

    @classmethod
    def get_service_order(cls, obj):
        return obj.service_order_data

    @classmethod
    def get_supplier(cls, obj):
        return obj.supplier_data

    @classmethod
    def get_contact(cls, obj):
        return obj.contact_data

    @classmethod
    def get_purchase_status(cls, obj):
        return str(dict(PURCHASE_STATUS).get(obj.purchase_status))

    @classmethod
    def get_purchase_request_product_datas(cls, obj):
        return [{
            "id": str(item.id),
            "sale_order_product_id": str(item.sale_order_product_id),
            "service_order_product_id": str(item.service_order_product_id),
            "product_data": item.product_data,
            "uom_data": item.uom_data,
            "tax_data": item.tax_data,
            "quantity": item.quantity,
            "unit_price": item.unit_price,
            "sub_total_price": item.sub_total_price
        } for item in obj.purchase_request.all()]

    @classmethod
    def get_attachment(cls, obj):
        att_objs = PurchaseRequestAttachmentFile.objects.select_related('attachment').filter(purchase_request=obj)
        return [item.attachment.get_detail() for item in att_objs]

    @classmethod
    def get_employee_inherit(cls, obj):
        return obj.employee_inherit.get_detail_with_group() if obj.employee_inherit else {}


class PurchaseRequestUpdateSerializer(AbstractCreateSerializerModel):
    title = serializers.CharField(max_length=150)
    sale_order = serializers.UUIDField(required=False, allow_null=True)
    distribution_plan = serializers.UUIDField(required=False, allow_null=True)
    service_order = serializers.UUIDField(required=False, allow_null=True)
    supplier = serializers.UUIDField(required=True)
    contact = serializers.UUIDField(required=True)
    purchase_request_product_datas = PurchaseRequestProductSerializer(many=True)
    note = serializers.CharField(allow_blank=True, allow_null=True)
    attachment = serializers.ListSerializer(child=serializers.CharField(), required=False)

    class Meta:
        model = PurchaseRequest
        fields = (
            'title',
            'supplier',
            'contact',
            'request_for',
            'sale_order',
            'distribution_plan',
            'service_order',
            'delivered_date',
            'note',
            'purchase_request_product_datas',
            'pretax_amount',
            'taxes',
            'total_price',
            'attachment'
        )

    @classmethod
    def validate_supplier(cls, value):
        return PurchaseRequestCreateSerializer.validate_supplier(value)

    @classmethod
    def validate_contact(cls, value):
        return PurchaseRequestCreateSerializer.validate_contact(value)

    @classmethod
    def validate_sale_order(cls, value):
        return PurchaseRequestCreateSerializer.validate_sale_order(value)

    @classmethod
    def validate_distribution_plan(cls, value):
        return PurchaseRequestCreateSerializer.validate_distribution_plan(value)

    @classmethod
    def validate_service_order(cls, value):
        return PurchaseRequestCreateSerializer.validate_service_order(value)

    def validate_attachment(self, value):
        user = self.context.get('user', None)
        return SerializerCommonValidate.validate_attachment(
            user=user, model_cls=PurchaseRequestAttachmentFile, value=value, doc_id=self.instance.id
        )

    def validate(self, validate_data):
        return PurchaseRequestCreateSerializer().validate(validate_data)

    @decorator_run_workflow
    def update(self, instance, validated_data):
        attachment_list = validated_data.pop('attachment', [])
        data_item_list = validated_data.pop('purchase_request_product_datas', [])

        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()

        PurchaseRequestCommonFunction.create_items_mapped(instance, data_item_list)
        PurchaseRequestCommonFunction.create_files_mapped(instance, attachment_list)

        return instance


class PurchaseRequestCommonFunction:
    @classmethod
    def create_items_mapped(cls, purchase_request_obj, data_item_list):
        bulk_data = []
        for item in data_item_list:
            bulk_data.append(
                PurchaseRequestProduct(
                    purchase_request=purchase_request_obj,
                    tenant=purchase_request_obj.tenant,
                    company=purchase_request_obj.company,
                    remain_for_purchase_order=item.get('quantity', 0),
                    **item
                )
            )
        PurchaseRequestProduct.objects.filter(purchase_request=purchase_request_obj).delete()
        PurchaseRequestProduct.objects.bulk_create(bulk_data)
        return True

    @staticmethod
    def create_files_mapped(pr_obj, attachment_list):
        SerializerCommonHandle.handle_attach_file(
            relate_app=Application.objects.filter(id=PurchaseRequest.get_app_id()).first(),
            model_cls=PurchaseRequestAttachmentFile,
            instance=pr_obj,
            attachment_result=attachment_list,
        )
        return True


# related serializers
class SaleOrderListForPRSerializer(serializers.ModelSerializer):
    is_create_purchase_request = serializers.SerializerMethodField()
    employee_inherit = serializers.SerializerMethodField()

    class Meta:
        model = SaleOrder
        fields = (
            'id',
            'code',
            'title',
            'employee_inherit',
            'customer_data',
            'is_create_purchase_request',
        )

    @classmethod
    def get_is_create_purchase_request(cls, obj):
        so_product = obj.sale_order_product_sale_order.all()
        return any(item.remain_for_purchase_request > 0 and item.product_id is not None for item in so_product)

    @classmethod
    def get_employee_inherit(cls, obj):
        return obj.employee_inherit.get_detail_with_group() if obj.employee_inherit else {}


class SaleOrderProductListForPRSerializer(serializers.ModelSerializer):
    product_data = serializers.SerializerMethodField()

    class Meta:
        model = SaleOrder
        fields = (
            'id',
            'product_data',
        )

    @classmethod
    def get_product_data(cls, obj):
        return [{
            'id': str(item.id),
            'product_quantity': item.product_quantity,
            'remain_for_purchase_request': item.remain_for_purchase_request,
            'product_data': item.product_data,
            'uom_data': item.uom_data,
            'tax_data': item.tax_data,
        } for item in obj.sale_order_product_sale_order.filter(
            product__isnull=False
        ) if 2 in item.product.product_choice and item.remain_for_purchase_request > 0]


class DistributionPlanListForPRSerializer(AbstractListSerializerModel):
    is_expired = serializers.SerializerMethodField()
    employee_inherit = serializers.SerializerMethodField()

    class Meta:
        model = DistributionPlan
        fields = (
            'id',
            'code',
            'title',
            'start_date',
            'end_date',
            'is_expired',
            'employee_inherit'
        )

    @classmethod
    def get_is_expired(cls, obj):
        return obj.end_date < datetime.now().date()

    @classmethod
    def get_employee_inherit(cls, obj):
        return obj.employee_inherit.get_detail_with_group() if obj.employee_inherit else {}


class DistributionPlanProductListForPRSerializer(AbstractDetailSerializerModel):
    product_data = serializers.SerializerMethodField()
    uom_data = serializers.SerializerMethodField()

    class Meta:
        model = DistributionPlan
        fields = (
            'id',
            'product_data',
            'uom_data',
            'start_date',
            'end_date',
            'no_of_month',
            'expected_number',
            'purchase_request_number'
        )

    @classmethod
    def get_product_data(cls, obj):
        return {
            'id': str(obj.product_id),
            'code': obj.product.code,
            'title': obj.product.title,
            'description': obj.product.description
        } if obj.product and 2 in obj.product.product_choice else {}

    @classmethod
    def get_uom_data(cls, obj):
        return {
            'id': str(obj.product.general_uom_group.uom_reference_id),
            'code': obj.product.general_uom_group.uom_reference.code,
            'title': obj.product.general_uom_group.uom_reference.title,
            'group_id': str(obj.product.general_uom_group_id),
        } if obj.product.general_uom_group.uom_reference else {} if obj.product.general_uom_group else {}


class ServiceOrderListForPRSerializer(AbstractListSerializerModel):
    employee_inherit = serializers.SerializerMethodField()

    class Meta:
        model = ServiceOrder
        fields = (
            'id',
            'title',
            'code',
            'customer_data',
            'employee_inherit',
        )

    @classmethod
    def get_employee_inherit(cls, obj):
        return obj.employee_inherit.get_detail_with_group() if obj.employee_inherit else {}


class ServiceOrderProductListForPRSerializer(AbstractListSerializerModel):
    product_data = serializers.SerializerMethodField()

    class Meta:
        model = ServiceOrder
        fields = (
            'id',
            'product_data'
        )

    @classmethod
    def get_product_data(cls, obj):
        return [{
            'id': str(item.id),
            'product_quantity': item.quantity,
            'remain_for_purchase_request': item.remain_for_purchase_request,
            'product_data': item.product_data,
            'uom_data': item.uom_data,
            'tax_data': item.tax_data,
        } for item in obj.service_details.all() if
            2 in item.product.product_choice and item.remain_for_purchase_request > 0]


class PurchaseRequestProductListSerializer(serializers.ModelSerializer):
    purchase_request = serializers.SerializerMethodField()
    product = serializers.SerializerMethodField()
    uom = serializers.SerializerMethodField()
    tax = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseRequestProduct
        fields = (
            'id',
            'purchase_request',
            'sale_order_product_id',
            'product',
            'uom',
            'tax',
            'quantity',
            'remain_for_purchase_order',
            'unit_price',
        )

    @classmethod
    def get_purchase_request(cls, obj):
        return {
            'id': obj.purchase_request_id,
            'title': obj.purchase_request.title,
            'code': obj.purchase_request.code,
        } if obj.purchase_request else {}

    @classmethod
    def get_product(cls, obj):
        return {
            'id': obj.product_id,
            'code': obj.product.code,
            'title': obj.product.title,
            'general_information': {
                'product_type': [{
                    'id': general_product_type.id,
                    'title': general_product_type.title,
                    'code': general_product_type.code
                } for general_product_type in obj.product.general_product_types_mapped.all()],
                'product_category': {
                    'id': obj.product.general_product_category_id,
                    'title': obj.product.general_product_category.title,
                    'code': obj.product.general_product_category.code
                } if obj.product.general_product_category else {},
                'uom_group': {
                    'id': obj.product.general_uom_group_id,
                    'title': obj.product.general_uom_group.title,
                    'code': obj.product.general_uom_group.code
                } if obj.product.general_uom_group else {},
            },
            'sale_information': {
                'default_uom': {
                    'id': obj.product.sale_default_uom_id,
                    'title': obj.product.sale_default_uom.title,
                    'code': obj.product.sale_default_uom.code,
                    'ratio': obj.product.sale_default_uom.ratio,
                    'rounding': obj.product.sale_default_uom.rounding,
                    'is_referenced_unit': obj.product.sale_default_uom.is_referenced_unit,
                } if obj.product.sale_default_uom else {},
                'tax_code': {
                    'id': obj.product.sale_tax_id,
                    'title': obj.product.sale_tax.title,
                    'code': obj.product.sale_tax.code,
                    'rate': obj.product.sale_tax.rate
                } if obj.product.sale_tax else {},
                'currency_using': {
                    'id': obj.product.sale_currency_using_id,
                    'title': obj.product.sale_currency_using.title,
                    'code': obj.product.sale_currency_using.code,
                } if obj.product.sale_currency_using else {},
                'length': obj.product.length,
                'width': obj.product.width,
                'height': obj.product.height,
            },
            'purchase_information': {
                'uom': {
                    'id': obj.product.purchase_default_uom_id,
                    'title': obj.product.purchase_default_uom.title,
                    'code': obj.product.purchase_default_uom.code,
                    'ratio': obj.product.purchase_default_uom.ratio,
                    'rounding': obj.product.purchase_default_uom.rounding,
                    'is_referenced_unit': obj.product.purchase_default_uom.is_referenced_unit,
                } if obj.product.purchase_default_uom else {},
                'tax': {
                    'id': obj.product.purchase_tax_id,
                    'title': obj.product.purchase_tax.title,
                    'code': obj.product.purchase_tax.code,
                    'rate': obj.product.purchase_tax.rate
                } if obj.product.purchase_tax else {},
            },
            'description': obj.product.description,
            'product_choice': obj.product.product_choice,
            'sale_cost': None,
        }

    @classmethod
    def get_uom(cls, obj):
        return {
            'id': obj.uom_id,
            'title': obj.uom.title,
            'code': obj.uom.code,
            'uom_group': {
                'id': obj.uom.group_id,
                'title': obj.uom.group.title,
                'code': obj.uom.group.code,
                'uom_reference': {
                    'id': obj.uom.group.uom_reference_id,
                    'title': obj.uom.group.uom_reference.title,
                    'code': obj.uom.group.uom_reference.code,
                    'ratio': obj.uom.group.uom_reference.ratio,
                    'rounding': obj.uom.group.uom_reference.rounding,
                } if obj.uom.group.uom_reference else {},
            } if obj.uom.group else {},
            'ratio': obj.uom.ratio,
            'rounding': obj.uom.rounding,
            'is_referenced_unit': obj.uom.is_referenced_unit,
        } if obj.uom else {}

    @classmethod
    def get_tax(cls, obj):
        return {
            'id': obj.tax_id,
            'title': obj.tax.title,
            'code': obj.tax.code,
            'rate': obj.tax.rate,
        } if obj.tax else {}


class PurchaseRequestSaleListSerializer(AbstractListSerializerModel):
    sale_order = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseRequest
        fields = (
            'id',
            'code',
            'title',
            'request_for',
            'sale_order',
        )

    @classmethod
    def get_sale_order(cls, obj):
        return {
            'id': obj.sale_order_id,
            'title': obj.sale_order.title,
            'code': obj.sale_order.code,
            'is_deal_close': obj.sale_order.opportunity.is_deal_close if obj.sale_order.opportunity else False,
        } if obj.sale_order else {}
