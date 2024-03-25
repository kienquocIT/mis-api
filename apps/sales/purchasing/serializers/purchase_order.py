from rest_framework import serializers

from apps.core.base.models import Application
from apps.core.workflow.tasks import decorator_run_workflow
from apps.sales.purchasing.models import PurchaseOrder, PurchaseOrderProduct, PurchaseOrderRequestProduct, \
    PurchaseOrderQuotation, PurchaseOrderPaymentStage, PurchaseOrderAttachmentFile
from apps.sales.purchasing.serializers.purchase_order_sub import PurchasingCommonValidate, PurchaseOrderCommonCreate, \
    PurchaseOrderCommonGet
from apps.shared import SYSTEM_STATUS, RECEIPT_STATUS, SaleMsg, HRMsg
from apps.shared.translations.base import AttachmentMsg


class PurchaseQuotationSerializer(serializers.ModelSerializer):
    purchase_quotation = serializers.UUIDField()

    class Meta:
        model = PurchaseOrderQuotation
        fields = (
            'purchase_quotation',
            'is_use',
        )

    @classmethod
    def validate_purchase_quotation(cls, value):
        return PurchasingCommonValidate().validate_purchase_quotation(value=value)


class PurchaseOrderRequestProductSerializer(serializers.ModelSerializer):
    purchase_request_product = serializers.UUIDField(required=False, allow_null=True)
    sale_order_product = serializers.UUIDField(required=False, allow_null=True)
    uom_stock = serializers.UUIDField(required=False, allow_null=True)

    class Meta:
        model = PurchaseOrderRequestProduct
        fields = (
            'purchase_request_product',
            'sale_order_product',
            'quantity_order',
            'uom_stock',
            'is_stock',
        )

    @classmethod
    def validate_purchase_request_product(cls, value):
        return PurchasingCommonValidate().validate_purchase_request_product(value=value)

    @classmethod
    def validate_sale_order_product(cls, value):
        return PurchasingCommonValidate().validate_sale_order_product(value=value)

    @classmethod
    def validate_uom_stock(cls, value):
        return PurchasingCommonValidate().validate_unit_of_measure(value=value)


class PurchaseOrderRequestProductListSerializer(serializers.ModelSerializer):
    purchase_request_product = serializers.SerializerMethodField()
    uom_stock = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseOrderRequestProduct
        fields = (
            'id',
            'purchase_request_product',
            'purchase_order_product_id',
            'sale_order_product_id',
            'quantity_order',
            'uom_stock',
            'is_stock',
            # goods receipt information
            'gr_completed_quantity',
            'gr_remain_quantity',
        )

    @classmethod
    def get_purchase_request_product(cls, obj):
        return {
            'id': obj.purchase_request_product_id,
            'purchase_request': {
                'id': obj.purchase_request_product.purchase_request_id,
                'title': obj.purchase_request_product.purchase_request.title,
                'code': obj.purchase_request_product.purchase_request.code,
            } if obj.purchase_request_product.purchase_request else {},
            'uom': {
                'id': obj.purchase_request_product.uom_id,
                'title': obj.purchase_request_product.uom.title,
                'code': obj.purchase_request_product.uom.code,
                'ratio': obj.purchase_request_product.uom.ratio,
            } if obj.purchase_request_product.uom else {},
        } if obj.purchase_request_product else {}

    @classmethod
    def get_uom_stock(cls, obj):
        return {
            'id': obj.uom_stock_id,
            'title': obj.uom_stock.title,
            'code': obj.uom_stock.code,
            'ratio': obj.uom_stock.ratio,
        } if obj.uom_stock else {}


class PurchaseOrderProductSerializer(serializers.ModelSerializer):
    purchase_request_products_data = PurchaseOrderRequestProductSerializer(
        many=True,
        required=False
    )
    product = serializers.UUIDField()
    uom_order_request = serializers.UUIDField(required=False)
    uom_order_actual = serializers.UUIDField()
    tax = serializers.UUIDField(required=False, allow_null=True)
    product_unit_price = serializers.FloatField()
    product_quantity_order_actual = serializers.FloatField()

    class Meta:
        model = PurchaseOrderProduct
        fields = (
            'product',
            'uom_order_request',
            'uom_order_actual',
            'tax',
            'stock',
            'purchase_request_products_data',
            # product information
            'product_title',
            'product_code',
            'product_description',
            'product_quantity_order_request',
            'product_quantity_order_actual',
            'product_unit_price',
            'product_tax_title',
            'product_tax_amount',
            'product_subtotal_price',
            'product_subtotal_price_after_tax',
            'order',
        )

    @classmethod
    def validate_product(cls, value):
        return PurchasingCommonValidate().validate_product(value=value)

    @classmethod
    def validate_uom_order_request(cls, value):
        return PurchasingCommonValidate().validate_unit_of_measure(value=value)

    @classmethod
    def validate_uom_order_actual(cls, value):
        return PurchasingCommonValidate().validate_unit_of_measure(value=value)

    @classmethod
    def validate_tax(cls, value):
        return PurchasingCommonValidate().validate_tax(value=value)

    @classmethod
    def validate_product_unit_price(cls, value):
        return PurchasingCommonValidate().validate_price(value=value)

    @classmethod
    def validate_product_quantity_order_actual(cls, value):
        return PurchasingCommonValidate().validate_quantity(value=value)


class PurchaseOrderProductListSerializer(serializers.ModelSerializer):
    purchase_request_products_data = serializers.SerializerMethodField()
    product = serializers.SerializerMethodField()
    uom_order_request = serializers.SerializerMethodField()
    uom_order_actual = serializers.SerializerMethodField()
    tax = serializers.SerializerMethodField()
    goods_receipt_info = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseOrderProduct
        fields = (
            'id',
            'product',
            'uom_order_request',
            'uom_order_actual',
            'tax',
            'stock',
            'purchase_request_products_data',
            # product information
            'product_title',
            'product_code',
            'product_description',
            'product_quantity_order_request',
            'product_quantity_order_actual',
            'product_unit_price',
            'product_tax_title',
            'product_tax_amount',
            'product_subtotal_price',
            'product_subtotal_price_after_tax',
            'order',
            # goods receipt
            'goods_receipt_info'
        )

    @classmethod
    def get_purchase_request_products_data(cls, obj):
        return PurchaseOrderRequestProductListSerializer(obj.purchase_order_request_order_product.filter(
            is_stock=False,
        ), many=True).data

    @classmethod
    def get_product(cls, obj):
        return {
            'id': obj.product_id,
            'title': obj.product.title,
            'code': obj.product.code,
            'general_traceability_method': obj.product.general_traceability_method,
            'description': obj.product.description,
        } if obj.product else {}

    @classmethod
    def get_uom_order_request(cls, obj):
        return PurchaseOrderCommonGet.get_uom(uom_obj=obj.uom_order_request, uom_id=obj.uom_order_request_id)

    @classmethod
    def get_uom_order_actual(cls, obj):
        return PurchaseOrderCommonGet.get_uom(uom_obj=obj.uom_order_actual, uom_id=obj.uom_order_actual_id)

    @classmethod
    def get_tax(cls, obj):
        return {
            'id': obj.tax_id,
            'title': obj.tax.title,
            'code': obj.tax.code,
            'rate': obj.tax.rate,
        } if obj.tax else {}

    @classmethod
    def get_goods_receipt_info(cls, obj):
        gr_completed_quantity = 0
        for gr_product in obj.goods_receipt_product_po_product.all():
            if gr_product.goods_receipt.system_status in [2, 3]:
                gr_completed_quantity += gr_product.quantity_import
        return {
            'gr_completed_quantity': gr_completed_quantity,
            'gr_remain_quantity': (obj.product_quantity_order_actual - gr_completed_quantity)
        }


class PurchaseOrderProductGRListSerializer(serializers.ModelSerializer):
    purchase_request_products_data = serializers.SerializerMethodField()
    product = serializers.SerializerMethodField()
    uom_order_request = serializers.SerializerMethodField()
    uom_order_actual = serializers.SerializerMethodField()
    tax = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseOrderProduct
        fields = (
            'id',
            'product',
            'uom_order_request',
            'uom_order_actual',
            'tax',
            'stock',
            'purchase_request_products_data',
            # product information
            'product_title',
            'product_code',
            'product_description',
            'product_quantity_order_request',
            'product_quantity_order_actual',
            'product_unit_price',
            'product_tax_title',
            'product_subtotal_price',
            'product_subtotal_price_after_tax',
            'order',
            # goods receipt information
            'gr_completed_quantity',
            'gr_remain_quantity',
        )

    @classmethod
    def get_purchase_request_products_data(cls, obj):
        return PurchaseOrderRequestProductListSerializer(obj.purchase_order_request_order_product.all(), many=True).data

    @classmethod
    def get_product(cls, obj):
        return {
            'id': obj.product_id,
            'title': obj.product.title,
            'code': obj.product.code,
            'general_traceability_method': obj.product.general_traceability_method,
            'description': obj.product.description,
            'product_choice': obj.product.product_choice,
        } if obj.product else {}

    @classmethod
    def get_uom_order_request(cls, obj):
        return PurchaseOrderCommonGet.get_uom(uom_obj=obj.uom_order_request, uom_id=obj.uom_order_request_id)

    @classmethod
    def get_uom_order_actual(cls, obj):
        return PurchaseOrderCommonGet.get_uom(uom_obj=obj.uom_order_actual, uom_id=obj.uom_order_actual_id)

    @classmethod
    def get_tax(cls, obj):
        return {
            'id': obj.tax_id,
            'title': obj.tax.title,
            'code': obj.tax.code,
            'rate': obj.tax.rate,
        } if obj.tax else {}


class PurchaseOrderPaymentStageSerializer(serializers.ModelSerializer):
    tax = serializers.UUIDField(required=False, allow_null=True)
    due_date = serializers.CharField(required=False, allow_null=True)

    class Meta:
        model = PurchaseOrderPaymentStage
        fields = (
            'remark',
            'payment_ratio',
            'value_before_tax',
            'tax',
            'value_after_tax',
            'due_date',
            'order',
        )

    @classmethod
    def validate_tax(cls, value):
        return PurchasingCommonValidate().validate_tax(value=value)


# PURCHASE ORDER BEGIN
def handle_attach_file(instance, attachment_result):
    if attachment_result and isinstance(attachment_result, dict):
        relate_app = Application.objects.filter(id="81a111ef-9c32-4cbd-8601-a3cce884badb").first()
        state = PurchaseOrderAttachmentFile.resolve_change(
            result=attachment_result, doc_id=instance.id, doc_app=relate_app,
        )
        if state:
            return True
        raise serializers.ValidationError({'attachment': AttachmentMsg.ERROR_VERIFY})
    return True


def validate_attachment(instance, value):
    if instance.employee_created_id:
        state, result = PurchaseOrderAttachmentFile.valid_change(
            current_ids=value, employee_id=instance.employee_created_id, doc_id=None
        )
        if state is True:
            return result
        raise serializers.ValidationError({'attachment': AttachmentMsg.SOME_FILES_NOT_CORRECT})
    raise serializers.ValidationError({'employee_id': HRMsg.EMPLOYEE_NOT_EXIST})


class PurchaseOrderListSerializer(serializers.ModelSerializer):
    supplier = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseOrder
        fields = (
            'id',
            'title',
            'code',
            'supplier',
            'delivered_date',
            'receipt_status',
            'system_status',
        )

    @classmethod
    def get_supplier(cls, obj):
        return {
            'id': obj.supplier_id,
            'name': obj.supplier.name,
            'code': obj.supplier.code,
        } if obj.supplier else {}


class PurchaseOrderDetailSerializer(serializers.ModelSerializer):
    purchase_requests_data = serializers.SerializerMethodField()
    purchase_quotations_data = serializers.SerializerMethodField()
    purchase_request_products_data = serializers.SerializerMethodField()
    supplier = serializers.SerializerMethodField()
    contact = serializers.SerializerMethodField()
    purchase_order_products_data = serializers.SerializerMethodField()
    receipt_status = serializers.SerializerMethodField()
    attachment = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseOrder
        fields = (
            'id',
            'title',
            'code',
            'purchase_requests_data',
            'purchase_quotations_data',
            'purchase_request_products_data',
            'supplier',
            'contact',
            'delivered_date',
            'status_delivered',
            'receipt_status',
            # purchase order tabs
            'purchase_order_products_data',
            # total amount
            'total_product_pretax_amount',
            'total_product_tax',
            'total_product',
            'total_product_revenue_before_tax',
            # payment stage tab
            'purchase_order_payment_stage',
            # system
            'system_status',
            'workflow_runtime_id',
            'is_active',
            'attachment',
        )

    @classmethod
    def get_purchase_requests_data(cls, obj):
        return [{
            'id': purchase_request.id,
            'title': purchase_request.title,
            'code': purchase_request.code,
        } for purchase_request in obj.purchase_requests.all()]

    @classmethod
    def get_purchase_quotations_data(cls, obj):
        return [{
            'id': purchase_order_quotation.id,
            'purchase_quotation': {
                'id': purchase_order_quotation.purchase_quotation_id,
                'title': purchase_order_quotation.purchase_quotation.title,
                'code': purchase_order_quotation.purchase_quotation.code,
                'supplier': {
                    'id': purchase_order_quotation.purchase_quotation.supplier_mapped_id,
                    'name': purchase_order_quotation.purchase_quotation.supplier_mapped.name,
                    'code': purchase_order_quotation.purchase_quotation.supplier_mapped.code,
                    'owner': {
                        'id': purchase_order_quotation.purchase_quotation.supplier_mapped.owner_id,
                        'fullname': purchase_order_quotation.purchase_quotation.supplier_mapped.owner.fullname,
                        'email': purchase_order_quotation.purchase_quotation.supplier_mapped.owner.email,
                        'mobile': purchase_order_quotation.purchase_quotation.supplier_mapped.owner.mobile,
                        'job_title': purchase_order_quotation.purchase_quotation.supplier_mapped.owner.job_title,
                    } if purchase_order_quotation.purchase_quotation.supplier_mapped.owner else {},
                } if purchase_order_quotation.purchase_quotation.supplier_mapped else {}
            } if purchase_order_quotation.purchase_quotation else {},
            'is_use': purchase_order_quotation.is_use,
        } for purchase_order_quotation in obj.purchase_order_quotation_order.all()]

    @classmethod
    def get_purchase_request_products_data(cls, obj):
        return PurchaseOrderRequestProductListSerializer(obj.purchase_order_request_product_order.filter(
            purchase_order_product__isnull=True,
            is_stock=False,
        ), many=True).data

    @classmethod
    def get_supplier(cls, obj):
        return {
            'id': obj.supplier_id,
            'name': obj.supplier.name,
            'code': obj.supplier.code,
        } if obj.supplier else {}

    @classmethod
    def get_contact(cls, obj):
        return {
            'id': obj.contact_id,
            'fullname': obj.contact.fullname,
            'code': obj.contact.code,
        } if obj.contact else {}

    @classmethod
    def get_purchase_order_products_data(cls, obj):
        return PurchaseOrderProductListSerializer(obj.purchase_order_product_order.all(), many=True).data

    @classmethod
    def get_receipt_status(cls, obj):
        if obj.receipt_status or obj.receipt_status == 0:
            return dict(RECEIPT_STATUS).get(obj.receipt_status)
        return None

    @classmethod
    def get_attachment(cls, obj):
        return [file_obj.get_detail() for file_obj in obj.attachment_m2m.all()]


class PurchaseOrderCreateSerializer(serializers.ModelSerializer):
    title = serializers.CharField()
    purchase_requests_data = serializers.ListField(
        child=serializers.UUIDField(required=False),
        required=False
    )
    purchase_quotations_data = PurchaseQuotationSerializer(
        many=True,
        required=False
    )
    supplier = serializers.UUIDField()
    contact = serializers.UUIDField()
    # purchase order tabs
    purchase_order_products_data = PurchaseOrderProductSerializer(
        many=True,
        required=False
    )
    # payment stage tab
    purchase_order_payment_stage = PurchaseOrderPaymentStageSerializer(
        many=True,
        required=False
    )
    attachment = serializers.ListSerializer(child=serializers.UUIDField(), required=False)

    class Meta:
        model = PurchaseOrder
        fields = (
            'title',
            'purchase_requests_data',
            'purchase_quotations_data',
            'supplier',
            'contact',
            'delivered_date',
            'status_delivered',
            # purchase order tabs
            'purchase_order_products_data',
            # total amount
            'total_product_pretax_amount',
            'total_product_tax',
            'total_product',
            'total_product_revenue_before_tax',
            # payment stage tab
            'purchase_order_payment_stage',
            # system
            'system_status',
            'attachment',
        )

    @classmethod
    def validate_purchase_requests_data(cls, value):
        return PurchasingCommonValidate().validate_purchase_requests_data(value=value)

    @classmethod
    def validate_supplier(cls, value):
        return PurchasingCommonValidate().validate_supplier(value=value)

    @classmethod
    def validate_contact(cls, value):
        return PurchasingCommonValidate().validate_contact(value=value)

    @classmethod
    def validate_total_payment_term(cls, validate_data):
        if 'purchase_order_payment_stage' in validate_data:
            total = 0
            for payment_stage in validate_data['purchase_order_payment_stage']:
                total += payment_stage.get('payment_ratio', 0)
                # check required field
                due_date = payment_stage.get('due_date', '')
                if not due_date:
                    raise serializers.ValidationError({'detail': SaleMsg.DUE_DATE_REQUIRED})
            if total != 100:
                raise serializers.ValidationError({'detail': SaleMsg.TOTAL_PAYMENT})
        return True

    def validate(self, validate_data):
        self.validate_total_payment_term(validate_data=validate_data)
        return validate_data

    @decorator_run_workflow
    def create(self, validated_data):
        attachment = []
        if 'attachment' in validated_data:
            attachment = validated_data['attachment']
            del validated_data['attachment']
        purchase_order = PurchaseOrder.objects.create(**validated_data)
        PurchaseOrderCommonCreate().create_purchase_order_sub_models(
            validated_data=validated_data,
            instance=purchase_order
        )
        validated_attachment = validate_attachment(purchase_order, attachment)
        handle_attach_file(purchase_order, validated_attachment)
        return purchase_order


class PurchaseOrderUpdateSerializer(serializers.ModelSerializer):
    purchase_requests_data = serializers.ListField(
        child=serializers.UUIDField(required=False),
        required=False
    )
    purchase_quotations_data = PurchaseQuotationSerializer(
        many=True,
        required=False
    )
    supplier = serializers.UUIDField(required=False)
    contact = serializers.UUIDField(required=False)
    # purchase order tabs
    purchase_order_products_data = PurchaseOrderProductSerializer(
        many=True,
        required=False
    )
    # payment stage tab
    purchase_order_payment_stage = PurchaseOrderPaymentStageSerializer(
        many=True,
        required=False
    )

    class Meta:
        model = PurchaseOrder
        fields = (
            'title',
            'purchase_requests_data',
            'purchase_quotations_data',
            'supplier',
            'contact',
            'delivered_date',
            'status_delivered',
            # purchase order tabs
            'purchase_order_products_data',
            # total amount
            'total_product_pretax_amount',
            'total_product_tax',
            'total_product',
            'total_product_revenue_before_tax',
            # payment stage tab
            'purchase_order_payment_stage',
            # system
            'system_status',
        )

    @classmethod
    def validate_purchase_requests_data(cls, value):
        return PurchasingCommonValidate().validate_purchase_requests_data(value=value)

    @classmethod
    def validate_supplier(cls, value):
        return PurchasingCommonValidate().validate_supplier(value=value)

    @classmethod
    def validate_contact(cls, value):
        return PurchasingCommonValidate().validate_contact(value=value)

    @classmethod
    def validate_total_payment_term(cls, validate_data):
        if 'purchase_order_payment_stage' in validate_data:
            total = 0
            for payment_stage in validate_data['purchase_order_payment_stage']:
                total += payment_stage.get('payment_ratio', 0)
                # check required field
                due_date = payment_stage.get('due_date', '')
                if not due_date:
                    raise serializers.ValidationError({'detail': SaleMsg.DUE_DATE_REQUIRED})
            if total != 100:
                raise serializers.ValidationError({'detail': SaleMsg.TOTAL_PAYMENT})
        return True

    def validate(self, validate_data):
        self.validate_total_payment_term(validate_data=validate_data)
        return validate_data

    def update(self, instance, validated_data):
        # update purchase order
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        PurchaseOrderCommonCreate().create_purchase_order_sub_models(
            validated_data=validated_data,
            instance=instance,
            is_update=True,
        )
        return instance


class PurchaseOrderSaleListSerializer(serializers.ModelSerializer):
    purchase_requests_data = serializers.SerializerMethodField()
    supplier = serializers.SerializerMethodField()
    receipt_status = serializers.SerializerMethodField()
    system_status = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseOrder
        fields = (
            'id',
            'title',
            'code',
            'purchase_requests_data',
            'supplier',
            'delivered_date',
            'receipt_status',
            'system_status',
        )

    @classmethod
    def get_purchase_requests_data(cls, obj):
        return [{
            'id': purchase_request.id,
            'title': purchase_request.title,
            'code': purchase_request.code,
        } for purchase_request in obj.purchase_requests.all()]

    @classmethod
    def get_supplier(cls, obj):
        return {
            'id': obj.supplier_id,
            'name': obj.supplier.name,
            'code': obj.supplier.code,
        } if obj.supplier else {}

    @classmethod
    def get_receipt_status(cls, obj):
        if obj.receipt_status or obj.receipt_status == 0:
            return dict(RECEIPT_STATUS).get(obj.receipt_status)
        return None

    @classmethod
    def get_system_status(cls, obj):
        if obj.system_status or obj.system_status == 0:
            return dict(SYSTEM_STATUS).get(obj.system_status)
        return None
