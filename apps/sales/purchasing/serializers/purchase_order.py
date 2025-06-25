from rest_framework import serializers

from apps.core.base.models import Application
from apps.core.workflow.tasks import decorator_run_workflow
from apps.sales.purchasing.models import PurchaseOrder, PurchaseOrderProduct, PurchaseOrderRequestProduct, \
    PurchaseOrderQuotation, PurchaseOrderPaymentStage, PurchaseOrderAttachmentFile, PurchaseOrderInvoice
from apps.sales.purchasing.serializers.purchase_order_sub import PurchasingCommonValidate, PurchaseOrderCommonCreate, \
    PurchaseOrderCommonGet
from apps.sales.quotation.models import QuotationAppConfig
from apps.shared import SYSTEM_STATUS, RECEIPT_STATUS, SaleMsg, AbstractCreateSerializerModel, \
    AbstractListSerializerModel, AbstractDetailSerializerModel, SerializerCommonValidate, SerializerCommonHandle


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
            # goods receipt information
            'gr_remain_quantity',
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
    product = serializers.UUIDField(required=False, allow_null=True)
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
            # goods receipt information
            'gr_remain_quantity',
            # shipping
            'is_shipping',
            'shipping_title',
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
            'is_shipping',
            'shipping_title',
            'gr_remain_quantity',
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


class PORequestProductGRListSerializer(serializers.ModelSerializer):
    purchase_order_request_product_id = serializers.SerializerMethodField()
    purchase_request_data = serializers.SerializerMethodField()
    uom_id = serializers.SerializerMethodField()
    uom_data = serializers.SerializerMethodField()
    gr_completed_quantity = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseOrderRequestProduct
        fields = (
            'purchase_order_request_product_id',
            'purchase_request_product_id',
            'purchase_request_data',
            'purchase_order_product_id',
            'sale_order_product_id',
            'quantity_order',
            'uom_id',
            'uom_data',
            'is_stock',
            # goods receipt information
            'gr_completed_quantity',
            'gr_remain_quantity',
        )

    @classmethod
    def get_purchase_order_request_product_id(cls, obj):
        return obj.id

    @classmethod
    def get_purchase_request_data(cls, obj):
        if obj.purchase_request_product:
            return {
                'id': obj.purchase_request_product.purchase_request_id,
                'title': obj.purchase_request_product.purchase_request.title,
                'code': obj.purchase_request_product.purchase_request.code,
            } if obj.purchase_request_product.purchase_request else {}
        return {}

    @classmethod
    def get_uom_id(cls, obj):
        if obj.is_stock is True and obj.uom_stock:
            return str(obj.uom_stock_id)
        if obj.purchase_request_product:
            return str(obj.purchase_request_product.uom_id) if obj.purchase_request_product.uom else None
        return None

    @classmethod
    def get_uom_data(cls, obj):
        if obj.is_stock is True and obj.uom_stock:
            return {
                'id': obj.uom_stock_id,
                'title': obj.uom_stock.title,
                'code': obj.uom_stock.code,
                'ratio': obj.uom_stock.ratio,
            }
        if obj.purchase_request_product:
            return {
                'id': obj.purchase_request_product.uom_id,
                'title': obj.purchase_request_product.uom.title,
                'code': obj.purchase_request_product.uom.code,
                'ratio': obj.purchase_request_product.uom.ratio,
            } if obj.purchase_request_product.uom else {}
        return {}

    @classmethod
    def get_gr_completed_quantity(cls, obj):
        return obj.quantity_order - obj.gr_remain_quantity


class POProductGRListSerializer(serializers.ModelSerializer):
    purchase_order_product_id = serializers.SerializerMethodField()
    pr_products_data = serializers.SerializerMethodField()
    product_data = serializers.SerializerMethodField()
    uom_request_data = serializers.SerializerMethodField()
    uom_data = serializers.SerializerMethodField()
    tax_data = serializers.SerializerMethodField()
    gr_completed_quantity = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseOrderProduct
        fields = (
            'purchase_order_product_id',
            'product_data',
            'uom_request_data',
            'uom_data',
            'tax_data',
            'stock',
            'pr_products_data',
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
    def get_purchase_order_product_id(cls, obj):
        return obj.id

    @classmethod
    def get_pr_products_data(cls, obj):
        return PORequestProductGRListSerializer(obj.filtered_po_pr_product, many=True).data

    @classmethod
    def get_product_data(cls, obj):
        return {
            'id': obj.product_id,
            'title': obj.product.title,
            'code': obj.product.code,
            'general_traceability_method': obj.product.general_traceability_method,
            'description': obj.product.description,
            'product_choice': obj.product.product_choice,
        } if obj.product else {}

    @classmethod
    def get_uom_request_data(cls, obj):
        return PurchaseOrderCommonGet.get_uom(uom_obj=obj.uom_order_request, uom_id=obj.uom_order_request_id)

    @classmethod
    def get_uom_data(cls, obj):
        return PurchaseOrderCommonGet.get_uom(uom_obj=obj.uom_order_actual, uom_id=obj.uom_order_actual_id)

    @classmethod
    def get_tax_data(cls, obj):
        return {
            'id': obj.tax_id,
            'title': obj.tax.title,
            'code': obj.tax.code,
            'rate': obj.tax.rate,
        } if obj.tax else {}

    @classmethod
    def get_gr_completed_quantity(cls, obj):
        return obj.product_quantity_order_actual - obj.gr_remain_quantity


class PurchaseOrderPaymentStageSerializer(serializers.ModelSerializer):
    date = serializers.CharField(required=False, allow_null=True)
    due_date = serializers.CharField(required=False, allow_null=True)
    tax_id = serializers.UUIDField(required=False, allow_null=True)

    class Meta:
        model = PurchaseOrderPaymentStage
        fields = (
            'remark',
            'date',
            'due_date',
            'ratio',
            'invoice',
            'invoice_data',
            'value_before_tax',
            'value_reconcile',
            'reconcile_data',
            'tax_id',
            'tax_data',
            'value_tax',
            'value_total',
            'is_ap_invoice',
            'order',
        )

    @classmethod
    def validate_tax_id(cls, value):
        return PurchasingCommonValidate().validate_tax_id(value=value)


class PurchaseOrderInvoiceSerializer(serializers.ModelSerializer):
    date = serializers.CharField(required=False, allow_null=True)
    tax_id = serializers.UUIDField(required=False, allow_null=True)

    class Meta:
        model = PurchaseOrderInvoice
        fields = (
            'remark',
            'date',
            'ratio',
            'tax_id',
            'tax_data',
            'total',
            'balance',
            'order',
        )

    @classmethod
    def validate_tax_id(cls, value):
        return PurchasingCommonValidate().validate_tax_id(value=value)


# BEGIN PURCHASE ORDER
class PurchaseOrderListSerializer(AbstractListSerializerModel):
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


class PurchaseOrderMinimalListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrder
        fields = (
            'id',
            'title',
            'code',
            'date_created',
        )


class PurchaseOrderDetailSerializer(AbstractDetailSerializerModel):
    purchase_requests_data = serializers.SerializerMethodField()
    purchase_quotations_data = serializers.SerializerMethodField()
    purchase_request_products_data = serializers.SerializerMethodField()
    purchase_order_products_data = serializers.SerializerMethodField()
    receipt_status = serializers.SerializerMethodField()
    attachment = serializers.SerializerMethodField()
    employee_inherit = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseOrder
        fields = (
            'id',
            'title',
            'code',
            'purchase_requests_data',
            'purchase_quotations_data',
            'purchase_request_products_data',
            'supplier_data',
            'contact_data',
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
            'purchase_order_invoice',
            # system
            'system_status',
            'workflow_runtime_id',
            'is_active',
            'attachment',
            'employee_inherit',
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

    @classmethod
    def get_employee_inherit(cls, obj):
        return obj.employee_inherit.get_detail_minimal() if obj.employee_inherit else {}


class PurchaseOrderCreateSerializer(AbstractCreateSerializerModel):
    title = serializers.CharField(max_length=100)
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
    purchase_order_invoice = PurchaseOrderInvoiceSerializer(
        many=True,
        required=False
    )
    attachment = serializers.ListSerializer(child=serializers.CharField(), required=False)

    class Meta:
        model = PurchaseOrder
        fields = (
            'title',
            'purchase_requests_data',
            'purchase_quotations_data',
            'supplier',
            'supplier_data',
            'contact',
            'contact_data',
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
            'purchase_order_invoice',
            # attachment
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
        if 'purchase_order_payment_stage' in validate_data and 'total_product' in validate_data:
            if len(validate_data['purchase_order_payment_stage']) > 0:
                total_payment = 0
                for payment_stage in validate_data['purchase_order_payment_stage']:
                    total_payment += payment_stage.get('value_total', 0)
                    # check required field
                    date = payment_stage.get('date', '')
                    due_date = payment_stage.get('due_date', '')
                    if not date:
                        raise serializers.ValidationError({'detail': SaleMsg.PAYMENT_DATE_REQUIRED})
                    if not due_date:
                        raise serializers.ValidationError({'detail': SaleMsg.PAYMENT_DUE_DATE_REQUIRED})
                # if total_payment != validate_data.get('total_product', 0):
                #     raise serializers.ValidationError({'detail': SaleMsg.TOTAL_PAYMENT})
            else:
                # check required by config
                so_config = QuotationAppConfig.objects.filter_on_company().first()
                if so_config:
                    if so_config.is_require_payment is True:
                        raise serializers.ValidationError({'detail': SaleMsg.PAYMENT_REQUIRED_BY_CONFIG})
        return True

    def validate_attachment(self, value):
        user = self.context.get('user', None)
        return SerializerCommonValidate.validate_attachment(
            user=user, model_cls=PurchaseOrderAttachmentFile, value=value
        )

    def validate(self, validate_data):
        self.validate_total_payment_term(validate_data=validate_data)
        return validate_data

    @decorator_run_workflow
    def create(self, validated_data):
        attachment = validated_data.pop('attachment', [])
        purchase_order = PurchaseOrder.objects.create(**validated_data)
        PurchaseOrderCommonCreate().create_purchase_order_sub_models(
            validated_data=validated_data,
            instance=purchase_order
        )
        SerializerCommonHandle.handle_attach_file(
            relate_app=Application.objects.filter(id="81a111ef-9c32-4cbd-8601-a3cce884badb").first(),
            model_cls=PurchaseOrderAttachmentFile,
            instance=purchase_order,
            attachment_result=attachment,
        )
        return purchase_order


class PurchaseOrderUpdateSerializer(AbstractCreateSerializerModel):
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
    purchase_order_invoice = PurchaseOrderInvoiceSerializer(
        many=True,
        required=False
    )
    attachment = serializers.ListSerializer(child=serializers.CharField(), required=False)

    class Meta:
        model = PurchaseOrder
        fields = (
            'title',
            'purchase_requests_data',
            'purchase_quotations_data',
            'supplier',
            'supplier_data',
            'contact',
            'contact_data',
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
            'purchase_order_invoice',
            # attachment
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
        if 'purchase_order_payment_stage' in validate_data and 'total_product' in validate_data:
            if len(validate_data['purchase_order_payment_stage']) > 0:
                total_payment = 0
                for payment_stage in validate_data['purchase_order_payment_stage']:
                    total_payment += payment_stage.get('value_total', 0)
                    # check required field
                    date = payment_stage.get('date', '')
                    due_date = payment_stage.get('due_date', '')
                    if not date:
                        raise serializers.ValidationError({'detail': SaleMsg.PAYMENT_DATE_REQUIRED})
                    if not due_date:
                        raise serializers.ValidationError({'detail': SaleMsg.PAYMENT_DUE_DATE_REQUIRED})
                # if total_payment != validate_data.get('total_product', 0):
                #     raise serializers.ValidationError({'detail': SaleMsg.TOTAL_PAYMENT})
            else:
                # check required by config
                so_config = QuotationAppConfig.objects.filter_on_company().first()
                if so_config:
                    if so_config.is_require_payment is True:
                        raise serializers.ValidationError({'detail': SaleMsg.PAYMENT_REQUIRED_BY_CONFIG})
        return True

    def validate_attachment(self, value):
        user = self.context.get('user', None)
        return SerializerCommonValidate.validate_attachment(
            user=user, model_cls=PurchaseOrderAttachmentFile, value=value, doc_id=self.instance.id
        )

    def validate(self, validate_data):
        self.validate_total_payment_term(validate_data=validate_data)
        return validate_data

    @decorator_run_workflow
    def update(self, instance, validated_data):
        attachment = validated_data.pop('attachment', [])
        # update purchase order
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        PurchaseOrderCommonCreate().create_purchase_order_sub_models(
            validated_data=validated_data,
            instance=instance,
            is_update=True,
        )
        SerializerCommonHandle.handle_attach_file(
            relate_app=Application.objects.filter(id="81a111ef-9c32-4cbd-8601-a3cce884badb").first(),
            model_cls=PurchaseOrderAttachmentFile,
            instance=instance,
            attachment_result=attachment,
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
