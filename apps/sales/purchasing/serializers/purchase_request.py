from django.utils.datetime_safe import datetime
from rest_framework import serializers
from apps.core.base.models import Application
from apps.core.workflow.tasks import decorator_run_workflow
from apps.masterdata.saledata.models import Account, Contact, Product, UnitOfMeasure, Tax
from apps.sales.purchasing.models import PurchaseRequest, PurchaseRequestProduct, PurchaseRequestAttachmentFile
from apps.sales.saleorder.models import SaleOrder, SaleOrderProduct
from apps.sales.distributionplan.models import DistributionPlan
from apps.shared import (
    REQUEST_FOR, PURCHASE_STATUS, AbstractCreateSerializerModel,
    AbstractDetailSerializerModel, AbstractListSerializerModel, HRMsg
)
from apps.shared.translations.base import AttachmentMsg
from apps.shared.translations.sales import PurchaseRequestMsg


class PurchaseRequestListSerializer(AbstractListSerializerModel):
    sale_order = serializers.SerializerMethodField()
    distribution_plan = serializers.SerializerMethodField()
    supplier = serializers.SerializerMethodField()
    request_for_string = serializers.SerializerMethodField()
    purchase_status_string = serializers.SerializerMethodField()

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
            'supplier',
            'delivered_date',
            'purchase_status',
            'purchase_status_string',
        )

    @classmethod
    def get_request_for_string(cls, obj):
        return str(dict(REQUEST_FOR).get(obj.request_for))

    @classmethod
    def get_sale_order(cls, obj):
        if obj.sale_order:
            return {
                'id': obj.sale_order_id,
                'code': obj.sale_order.code,
                'title': obj.sale_order.title,
            }
        return None

    @classmethod
    def get_distribution_plan(cls, obj):
        if obj.distribution_plan:
            return {
                'id': obj.distribution_plan_id,
                'code': obj.distribution_plan.code,
                'title': obj.distribution_plan.title,
            }
        return None

    @classmethod
    def get_supplier(cls, obj):
        if obj.supplier:
            return {
                'id': obj.supplier_id,
                'title': obj.supplier.name,
            }
        return None

    @classmethod
    def get_purchase_status_string(cls, obj):
        return str(dict(PURCHASE_STATUS).get(obj.purchase_status))


class PurchaseRequestDetailSerializer(AbstractDetailSerializerModel):
    sale_order = serializers.SerializerMethodField()
    distribution_plan = serializers.SerializerMethodField()
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
            'purchase_request_product_datas',
            'pretax_amount',
            'taxes',
            'total_price',
            'attachment',
            'employee_inherit',
        )

    @classmethod
    def get_sale_order(cls, obj):
        if obj.sale_order:
            return {
                'id': obj.sale_order_id,
                'code': obj.sale_order.code,
                'title': obj.sale_order.title,
            }
        return None

    @classmethod
    def get_distribution_plan(cls, obj):
        if obj.distribution_plan:
            return {
                'id': obj.distribution_plan_id,
                'code': obj.distribution_plan.code,
                'title': obj.distribution_plan.title,
            }
        return None

    @classmethod
    def get_supplier(cls, obj):
        if obj.supplier:
            return {
                'id': obj.supplier_id,
                'name': obj.supplier.name,
                'code': obj.supplier.code,
            }
        return None

    @classmethod
    def get_contact(cls, obj):
        if obj.supplier:
            return {
                'id': obj.contact_id,
                'fullname': obj.contact.fullname,
                'job_title': obj.contact.job_title,
                'email': obj.contact.email,
                'mobile': obj.contact.mobile,
            }
        return None

    @classmethod
    def get_purchase_status(cls, obj):
        return str(dict(PURCHASE_STATUS).get(obj.purchase_status))

    @classmethod
    def get_purchase_request_product_datas(cls, obj):
        return [
            {
                "tax": {
                    "id": str(item.tax_id),
                    "code": item.tax.code,
                    "title": item.tax.title,
                    "rate": item.tax.rate
                } if item.tax else {},
                "uom": {
                    "id": str(item.uom_id),
                    "code": item.uom.code,
                    "title": item.uom.title,
                    "group_id": item.uom.group_id
                } if item.uom else {},
                "product": {
                    "id": str(item.product_id),
                    "code": item.product.code,
                    "title": item.product.title,
                    "description": item.product.description,
                    "uom_group": str(item.product.general_uom_group_id)
                } if item.product else {},
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "sub_total_price": item.sub_total_price,
                "sale_order_product": str(item.sale_order_product_id)
            } for item in obj.purchase_request.all()
        ]

    @classmethod
    def get_attachment(cls, obj):
        att_objs = PurchaseRequestAttachmentFile.objects.select_related('attachment').filter(purchase_request=obj)
        return [item.attachment.get_detail() for item in att_objs]

    @classmethod
    def get_employee_inherit(cls, obj):
        return obj.employee_inherit.get_detail_minimal() if obj.employee_inherit else {}


class PurchaseRequestProductSerializer(serializers.ModelSerializer):
    product = serializers.UUIDField()
    sale_order_product = serializers.UUIDField(allow_null=True, default=None)
    uom = serializers.UUIDField()
    tax = serializers.UUIDField(allow_null=True, default=None)

    class Meta:
        model = PurchaseRequestProduct
        fields = (
            'sale_order_product',
            'product',
            'uom',
            'quantity',
            'unit_price',
            'tax',
            'sub_total_price'
        )

    @classmethod
    def validate_sale_order_product(cls, value):
        if value:
            try:
                so_product = SaleOrderProduct.objects.get(
                    id=value
                )
                return str(so_product.id)
            except Product.DoesNotExist:
                raise serializers.ValidationError({'product': PurchaseRequestMsg.NOT_IN_SALE_ORDER})
        return None

    @classmethod
    def validate_product(cls, value):
        try:
            product = Product.objects.get_current(
                fill__tenant=True,
                fill__company=True,
                id=value
            )
            return {
                'id': str(product.id),
                'title': product.title,
                'code': product.code,
                'uom_group': str(product.general_uom_group_id),
            }
        except Product.DoesNotExist:
            raise serializers.ValidationError({'product': PurchaseRequestMsg.DOES_NOT_EXIST})

    @classmethod
    def validate_tax(cls, value):
        if value:
            try:
                tax = Tax.objects.get_current(
                    fill__tenant=True,
                    fill__company=True,
                    id=value
                )
                return {
                    'id': str(tax.id),
                    'title': tax.title,
                    'rate': tax.rate,
                }
            except Tax.DoesNotExist:
                raise serializers.ValidationError({'tax': PurchaseRequestMsg.DOES_NOT_EXIST})
        return None

    @classmethod
    def validate_uom(cls, value):
        try:
            uom = UnitOfMeasure.objects.get_current(
                fill__tenant=True,
                fill__company=True,
                id=value
            )
            return {
                'id': str(uom.id),
                'title': uom.title,
            }
        except UnitOfMeasure.DoesNotExist:
            raise serializers.ValidationError({'uom': PurchaseRequestMsg.DOES_NOT_EXIST})

    @classmethod
    def validate_unit_price(cls, value):
        if value < 0:
            raise serializers.ValidationError({'unit_price': PurchaseRequestMsg.GREATER_THAN_ZERO})
        return value

    @classmethod
    def validate_sub_total_price(cls, value):
        if value < 0:
            raise serializers.ValidationError({'sub_total_price': PurchaseRequestMsg.GREATER_THAN_ZERO})
        return value

    @classmethod
    def validate_quantity(cls, value):
        if value < 0:
            raise serializers.ValidationError({'quantity': PurchaseRequestMsg.GREATER_THAN_ZERO})
        return value

    @classmethod
    def create_product_datas(cls, purchase_request, product_datas):
        bulk_data = []
        for data in product_datas:
            pr_product = PurchaseRequestProduct(
                purchase_request=purchase_request,
                sale_order_product_id=data['sale_order_product'],
                product_id=data['product']['id'],
                uom_id=data['uom']['id'],
                tax_id=data['tax']['id'] if data.get('tax') else None,
                quantity=data['quantity'],
                remain_for_purchase_order=data['quantity'],
                unit_price=data['unit_price'],
                sub_total_price=data['sub_total_price'],
                tenant=purchase_request.tenant,
                company=purchase_request.company,
            )
            bulk_data.append(pr_product)
        return bulk_data

    @classmethod
    def delete_product_datas(cls, instance):
        objs = PurchaseRequestProduct.objects.select_related('sale_order_product').filter(purchase_request=instance)
        if objs:
            objs.delete()
        return True


class PurchaseRequestCreateSerializer(AbstractCreateSerializerModel):
    sale_order = serializers.UUIDField(required=False, allow_null=True)
    distribution_plan = serializers.UUIDField(required=False, allow_null=True)
    supplier = serializers.UUIDField(required=True)
    contact = serializers.UUIDField(required=True)
    purchase_request_product_datas = PurchaseRequestProductSerializer(many=True)
    note = serializers.CharField(allow_blank=True)
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
            'delivered_date',
            'purchase_status',
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
            return Account.objects.get_current(
                fill__tenant=True,
                fill__company=True,
                id=value
            )
        except Account.DoesNotExist:
            raise serializers.ValidationError({'supplier': PurchaseRequestMsg.DOES_NOT_EXIST})

    @classmethod
    def validate_contact(cls, value):
        try:
            return Contact.objects.get_current(
                fill__tenant=True,
                fill__company=True,
                id=value
            )
        except Contact.DoesNotExist:
            raise serializers.ValidationError({'contact': PurchaseRequestMsg.DOES_NOT_EXIST})

    @classmethod
    def validate_sale_order(cls, value):
        if value:
            try:
                return SaleOrder.objects.get_current(
                    fill__tenant=True,
                    fill__company=True,
                    id=value
                )
            except SaleOrder.DoesNotExist:
                raise serializers.ValidationError({'sale_order': PurchaseRequestMsg.DOES_NOT_EXIST})
        return None

    @classmethod
    def validate_distribution_plan(cls, value):
        if value:
            try:
                distribution_plan_obj = DistributionPlan.objects.get_current(
                    fill__tenant=True,
                    fill__company=True,
                    id=value
                )
                if distribution_plan_obj.end_date < datetime.now().date():
                    raise serializers.ValidationError({'distribution_plan': PurchaseRequestMsg.EXPIRED_DB})
                return distribution_plan_obj
            except DistributionPlan.DoesNotExist:
                raise serializers.ValidationError({'distribution_plan': PurchaseRequestMsg.DOES_NOT_EXIST})
        return None

    @classmethod
    def validate_pretax_amount(cls, value):
        if value < 0:
            raise serializers.ValidationError({'pretax_amount': PurchaseRequestMsg.GREATER_THAN_ZERO})
        return value

    @classmethod
    def validate_taxes(cls, value):
        if value < 0:
            raise serializers.ValidationError({'pretax_amount': PurchaseRequestMsg.GREATER_THAN_ZERO})
        return value

    @classmethod
    def validate_total_price(cls, value):
        if value < 0:
            raise serializers.ValidationError({'pretax_amount': PurchaseRequestMsg.GREATER_THAN_ZERO})
        return value

    def validate(self, validate_data):
        context_user = self.context.get('user', None)
        if 'attachment' in validate_data:
            if context_user and hasattr(context_user, 'employee_current_id'):
                state, result = PurchaseRequestAttachmentFile.valid_change(
                    current_ids=validate_data.get('attachment', []),
                    employee_id=context_user.employee_current_id,
                    doc_id=None
                )
                if state is True:
                    validate_data['attachment'] = result
                    return validate_data
                raise serializers.ValidationError({'attachment': AttachmentMsg.SOME_FILES_NOT_CORRECT})
            raise serializers.ValidationError({'employee_id': HRMsg.EMPLOYEE_NOT_EXIST})
        return validate_data

    @decorator_run_workflow
    def create(self, validated_data):
        attachment = validated_data.pop('attachment', [])
        purchase_request_product_datas = validated_data.pop('purchase_request_product_datas', [])

        purchase_request = PurchaseRequest.objects.create(**validated_data)
        bulk_data = PurchaseRequestProductSerializer.create_product_datas(
            purchase_request,
            purchase_request_product_datas
        )
        PurchaseRequestProduct.objects.bulk_create(bulk_data)

        PurchaseRequestCommonFunction.handle_attach_file(purchase_request, attachment)
        return purchase_request


class PurchaseRequestUpdateSerializer(AbstractCreateSerializerModel):
    title = serializers.CharField(required=False)
    sale_order = serializers.UUIDField(required=False, allow_null=True)
    distribution_plan = serializers.UUIDField(required=False, allow_null=True)
    request_for = serializers.IntegerField(required=False)
    supplier = serializers.UUIDField(required=False)
    contact = serializers.UUIDField(required=False)
    delivered_date = serializers.DateTimeField(required=False)
    purchase_status = serializers.IntegerField(required=False)
    purchase_request_product_datas = PurchaseRequestProductSerializer(many=True, required=False)
    note = serializers.CharField(allow_blank=True, required=False)
    pretax_amount = serializers.FloatField(required=False)
    taxes = serializers.FloatField(required=False)
    total_price = serializers.FloatField(required=False)
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
            'delivered_date',
            'purchase_status',
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
            return Account.objects.get_current(
                fill__tenant=True,
                fill__company=True,
                id=value
            )
        except Account.DoesNotExist:
            raise serializers.ValidationError({'supplier': PurchaseRequestMsg.DOES_NOT_EXIST})

    @classmethod
    def validate_contact(cls, value):
        try:
            return Contact.objects.get_current(
                fill__tenant=True,
                fill__company=True,
                id=value
            )
        except Contact.DoesNotExist:
            raise serializers.ValidationError({'contact': PurchaseRequestMsg.DOES_NOT_EXIST})

    @classmethod
    def validate_sale_order(cls, value):
        if value:
            try:
                return SaleOrder.objects.get_current(
                    fill__tenant=True,
                    fill__company=True,
                    id=value
                )
            except SaleOrder.DoesNotExist:
                raise serializers.ValidationError({'sale_order': PurchaseRequestMsg.DOES_NOT_EXIST})
        return None

    @classmethod
    def validate_distribution_plan(cls, value):
        if value:
            try:
                distribution_plan_obj = DistributionPlan.objects.get_current(
                    fill__tenant=True,
                    fill__company=True,
                    id=value
                )
                if distribution_plan_obj.end_date > datetime.now().date():
                    raise serializers.ValidationError({'distribution_plan': PurchaseRequestMsg.EXPIRED_DB})
                return distribution_plan_obj
            except DistributionPlan.DoesNotExist:
                raise serializers.ValidationError({'distribution_plan': PurchaseRequestMsg.DOES_NOT_EXIST})
        return None

    @classmethod
    def validate_pretax_amount(cls, value):
        if value < 0:
            raise serializers.ValidationError({'pretax_amount': PurchaseRequestMsg.GREATER_THAN_ZERO})
        return value

    @classmethod
    def validate_taxes(cls, value):
        if value < 0:
            raise serializers.ValidationError({'pretax_amount': PurchaseRequestMsg.GREATER_THAN_ZERO})
        return value

    @classmethod
    def validate_total_price(cls, value):
        if value < 0:
            raise serializers.ValidationError({'pretax_amount': PurchaseRequestMsg.GREATER_THAN_ZERO})
        return value

    def validate(self, validate_data):
        context_user = self.context.get('user', None)
        if 'attachment' in validate_data:
            if context_user and hasattr(context_user, 'employee_current_id'):
                state, result = PurchaseRequestAttachmentFile.valid_change(
                    current_ids=validate_data.get('attachment', []),
                    employee_id=context_user.employee_current_id,
                    doc_id=self.instance.id
                )
                if state is True:
                    validate_data['attachment'] = result
                    return validate_data
                raise serializers.ValidationError({'attachment': AttachmentMsg.SOME_FILES_NOT_CORRECT})
            raise serializers.ValidationError({'employee_id': HRMsg.EMPLOYEE_NOT_EXIST})
        return validate_data

    @decorator_run_workflow
    def update(self, instance, validated_data):
        attachment = validated_data.pop('attachment', [])
        purchase_request_product_datas = validated_data.pop('purchase_request_product_datas', [])

        PurchaseRequestProductSerializer.delete_product_datas(instance)
        bulk_data = PurchaseRequestProductSerializer.create_product_datas(
            instance,
            purchase_request_product_datas
        )
        PurchaseRequestProduct.objects.bulk_create(bulk_data)

        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()

        PurchaseRequestCommonFunction.handle_attach_file(instance, attachment)
        return instance


class PurchaseRequestCommonFunction:
    @classmethod
    def handle_attach_file(cls, instance, attachment_result):
        if attachment_result and isinstance(attachment_result, dict):
            relate_app = Application.objects.filter(id="fbff9b3ff7c9414f995996d3ec2fb8bf").first()
            if relate_app:
                state = PurchaseRequestAttachmentFile.resolve_change(
                    result=attachment_result, doc_id=instance.id, doc_app=relate_app,
                )
                if state:
                    return True
            raise serializers.ValidationError({'attachment': AttachmentMsg.ERROR_VERIFY})
        return True


# related serializers
class PurchaseRequestListForPQRSerializer(serializers.ModelSerializer):
    product_list = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseRequest
        fields = (
            'id',
            'code',
            'title',
            'product_list'
        )

    @classmethod
    def get_product_list(cls, obj):
        product_list = []
        for item in obj.purchase_request.all().select_related('product', 'uom', 'tax'):
            product_list.append(
                {
                    'id': item.product_id,
                    'title': item.product.title,
                    'description': item.product.description,
                    'uom': {'id': item.uom_id, 'title': item.uom.title, 'ratio': item.uom.ratio},
                    'uom_group': {
                        'id': item.uom.group_id, 'code': item.uom.group.code, 'title': item.uom.group.title
                    } if item.uom.group else {},
                    'quantity': item.quantity,
                    'purchase_request_id': item.purchase_request_id,
                    'purchase_request_code': item.purchase_request.code,
                    'product_unit_price': item.unit_price,
                    'product_subtotal_price': item.sub_total_price,
                    'tax': {
                        'id': item.tax_id, 'title': item.tax.title, 'code': item.tax.code, 'value': item.tax.rate
                    } if item.tax else {},
                }
            )
        return product_list


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
