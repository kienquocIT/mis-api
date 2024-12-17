import logging
from django.db import transaction
from rest_framework import serializers

from apps.core.hr.models import Employee
from apps.core.workflow.tasks import decorator_run_workflow
from apps.core.process.utils import ProcessRuntimeControl
from apps.masterdata.saledata.models import ProductCategory, Account, DocumentType
from apps.sales.consulting.models import Consulting, ConsultingDocument, ConsultingProductCategory, ConsultingAttachment
from apps.sales.consulting.serializers.consulting_sub import ConsultingCommonCreate
from apps.sales.opportunity.models import Opportunity
from apps.shared import AbstractListSerializerModel, AbstractCreateSerializerModel, BaseMsg, HRMsg, \
    AbstractDetailSerializerModel
from apps.shared.translations.base import AttachmentMsg

logger = logging.getLogger(__name__)

class ConsultingDocumentCreateSerializer(serializers.ModelSerializer):
    document_type = serializers.UUIDField(required=False, allow_null=True)

    class Meta:
        model = ConsultingDocument
        fields = (
            'title',
            'remark',
            'document_type',
            'attachment_data',
            'order',
        )

    @classmethod
    def validate_document_type(cls, value):
        if value:
            try:
                document_type = DocumentType.objects.get(id=value)
                return document_type
            except DocumentType.DoesNotExist:
                raise serializers.ValidationError({'document_type': BaseMsg.NOT_EXIST})
        return None

    def validate(self, validate_data):
        attachment_data = validate_data.get('attachment_data')
        if not attachment_data:
            raise serializers.ValidationError({'attachment_data': 'attachemnt required'})
        return validate_data


class ProductCategoriesCreateSerializer(serializers.ModelSerializer):
    value = serializers.FloatField()
    product_category = serializers.UUIDField()

    class Meta:
        model = ConsultingProductCategory
        fields = (
            'order',
            'value',
            'product_category',
        )

    @classmethod
    def validate_value(cls, value):
        if value:
            if value < 0:
                raise serializers.ValidationError({'value': 'Value must be a positive number'})
            return value
        raise serializers.ValidationError({'value': BaseMsg.REQUIRED})

    @classmethod
    def validate_product_category(cls, value):
        if value:
            try:
                return ProductCategory.objects.filter(id=value).first()
            except ProductCategory.DoesNotExist:
                raise serializers.ValidationError({'product_category': 'Product Category does not exist'})
        raise serializers.ValidationError({'product_category': BaseMsg.REQUIRED})

class ConsultingListSerializer(AbstractListSerializerModel):
    customer = serializers.SerializerMethodField()
    employee_inherit = serializers.SerializerMethodField()

    class Meta:
        model = Consulting
        fields = (
            'id',
            'title',
            'code',
            'customer',
            'employee_inherit',
            'due_date',
            'value'
        )

    @classmethod
    def get_customer(cls, obj):
        return {
            'id': obj.customer_id,
            'title': obj.customer.name,
            'code': obj.customer.code,
        } if obj.customer else {}

    @classmethod
    def get_employee_inherit(cls, obj):
        return {
            'id': obj.employee_inherit_id,
            'full_name': obj.employee_inherit.get_full_name(2),
            'code': obj.employee_inherit.code,
        } if obj.employee_inherit else {}


class ConsultingCreateSerializer(AbstractCreateSerializerModel):
    title = serializers.CharField(max_length=100)
    attachment = serializers.ListSerializer(child=serializers.CharField(), required=False)
    document_data = ConsultingDocumentCreateSerializer(many=True, required=False)
    due_date = serializers.DateField(required=True)
    value = serializers.FloatField()
    customer = serializers.UUIDField(required=False, allow_null=True)
    product_categories = ProductCategoriesCreateSerializer(many=True, required=False)
    opportunity = serializers.UUIDField(allow_null=True, required=False)
    employee_inherit = serializers.UUIDField()
    process = serializers.UUIDField(allow_null=True, default=None, required=False)
    process_stage_app = serializers.UUIDField(allow_null=True, default=None, required=False)

    class Meta:
        model = Consulting
        fields =(
            'opportunity',
            'employee_inherit',
            'title',
            'attachment',
            'document_data',
            'due_date',
            'value',
            'abstract_content',
            'customer',
            'product_categories',
            'process',
            'process_stage_app',
        )

    @classmethod
    def validate_process(cls, attrs):
        return ProcessRuntimeControl.get_process_obj(process_id=attrs) if attrs else None

    @classmethod
    def validate_process_stage_app(cls, attrs):
        return ProcessRuntimeControl.get_process_stage_app(
            stage_app_id=attrs, app_id=Consulting.get_app_id()
        ) if attrs else None

    def validate_value(self, value):
        total_value = 0
        if value:
            for item in self.initial_data.get('product_categories', []):
                total_value += int(item.get('value'))
            if not total_value == value:
                raise serializers.ValidationError(
                    {'value': 'Estimated value must be equal to the sum of product category value'})
            return value
        raise serializers.ValidationError({'value': BaseMsg.REQUIRED})

    @classmethod
    def validate_opportunity(cls, value):
        if value:
            try:
                return Opportunity.objects.get_current(fill__tenant=True, fill__company=True, id=value)
            except Opportunity.DoesNotExist:
                raise serializers.ValidationError({'opportunity': BaseMsg.NOT_EXIST})
        return value

    @classmethod
    def validate_employee_inherit(cls, value):
        if value:
            try:
                return Employee.objects.get_current(fill__tenant=True, fill__company=True, id=value)
            except Employee.DoesNotExist:
                raise serializers.ValidationError({'employee_inherit': BaseMsg.NOT_EXIST})
        return value

    def validate_attachment(self, value):
        user = self.context.get('user', None)
        if user and hasattr(user, 'employee_current_id'):
            state, result = ConsultingAttachment.valid_change(
                current_ids=value, employee_id=user.employee_current_id, doc_id=None
            )
            if state is True:
                return result
            raise serializers.ValidationError({'attachment': AttachmentMsg.SOME_FILES_NOT_CORRECT})
        raise serializers.ValidationError({'employee_id': HRMsg.EMPLOYEE_NOT_EXIST})

    def validate_customer(self, value):
        opportunity = self.initial_data.get('opportunity', None)
        if opportunity is None:
            if value:
                try:
                    return Account.objects.filter(id=value).first()
                except Account.DoesNotExist:
                    raise serializers.ValidationError({'customer': 'Customer does not exist'})
            raise serializers.ValidationError({'customer': BaseMsg.REQUIRED})
        return value

    def validate(self, validate_data):
        if validate_data.get('opportunity'):
            validate_data['customer'] = validate_data.get('opportunity').customer

        employee_obj = validate_data.get('employee_inherit', None)
        if not employee_obj:
            raise serializers.ValidationError({
                'detail': 'Need employee information to check permission to create progress ticket'
            })

        process_obj = validate_data.get('process', None)
        process_stage_app_obj = validate_data.get('process_stage_app', None)
        opportunity_id = validate_data.get('opportunity_id', None)
        if process_obj:
            ProcessRuntimeControl(process_obj=process_obj).validate_process(
                process_stage_app_obj=process_stage_app_obj,
                employee_id=employee_obj.id,
                opp_id=opportunity_id,
            )

        return validate_data

    @decorator_run_workflow
    def create(self, validated_data):
        attachment = validated_data.pop('attachment', [])
        product_categories = validated_data.pop('product_categories', [])
        document_data = validated_data.pop('document_data', [])
        create_data = {
            'attachment': attachment,
            'product_categories': product_categories,
            'document_data': document_data,
        }
        try:
            with transaction.atomic():
                consulting = Consulting.objects.create(**validated_data)
                if consulting.process:
                    ProcessRuntimeControl(process_obj=consulting.process).register_doc(
                        process_stage_app_obj=consulting.process_stage_app,
                        app_id=consulting.get_app_id(),
                        doc_id=consulting.id,
                        doc_title=consulting.title,
                        employee_created_id=consulting.employee_created_id,
                        date_created=consulting.date_created,
                    )

                ConsultingCommonCreate.create_sub_models(instance=consulting, create_data=create_data)
        except Exception as err:
            logger.error(msg=f'Create consulting errors: {str(err)}')
            raise serializers.ValidationError({'consulting': 'Error creating Consulting'})

        return consulting


class ConsultingDetailSerializer(AbstractDetailSerializerModel):
    employee_inherit = serializers.SerializerMethodField()
    opportunity = serializers.SerializerMethodField()
    customer = serializers.SerializerMethodField()
    attachment_data = serializers.SerializerMethodField()
    product_categories = serializers.SerializerMethodField()
    process = serializers.SerializerMethodField()
    process_stage_app = serializers.SerializerMethodField()

    class Meta:
        model = Consulting
        fields = (
            'title',
            'opportunity',
            'customer',
            'value',
            'due_date',
            'employee_inherit',
            'employee_created_id',
            'abstract_content',
            'attachment_data',
            'product_categories',
            'process',
            'process_stage_app',
        )

    @classmethod
    def get_process(cls, obj):
        if obj.process:
            return {
                'id': obj.process.id,
                'title': obj.process.title,
                'remark': obj.process.remark,
            }
        return {}

    @classmethod
    def get_process_stage_app(cls, obj):
        if obj.process_stage_app:
            return {
                'id': obj.process_stage_app.id,
                'title': obj.process_stage_app.title,
                'remark': obj.process_stage_app.remark,
            }
        return {}

    @classmethod
    def get_customer(cls, obj):
        return {
            'id': obj.customer_id,
            'title': obj.customer.name,
            'code': obj.customer.code,
        } if obj.customer else {}

    @classmethod
    def get_employee_inherit(cls, obj):
        return {
            'id': obj.employee_inherit_id,
            'full_name': obj.employee_inherit.get_full_name(2),
            'code': obj.employee_inherit.code,
        } if obj.employee_inherit else {}

    @classmethod
    def get_opportunity(cls, obj):
        return {
            'id': obj.opportunity_id,
            'title': obj.opportunity.title,
            'code': obj.opportunity.code,
        } if obj.opportunity else {}

    @classmethod
    def get_product_categories(cls, obj):
        data = []
        for item in obj.consulting_product_category_consulting.all():
            if item.product_category:
                data.append({
                    "id": item.id,
                    "value": item.value,
                    "title": item.product_category.title,
                    "product_category_id": item.product_category.id,
                    "order": item.order,
                })
        return data

    @classmethod
    def get_attachment_data(cls, obj):
        data = []
        for item in obj.consulting_document_consulting.all():
            data.append({
                "id": item.id,
                "title": item.title,
                "document_type": item.document_type.id if item.document_type else None,
                "isManual": not item.document_type,
                "remark": item.remark,
                "attachment_data": item.attachment_data,
                "order": item.order,
            })
        return data


class ConsultingUpdateSerializer(AbstractCreateSerializerModel):
    title = serializers.CharField(max_length=100)
    attachment = serializers.ListSerializer(child=serializers.CharField(), required=False)
    document_data = ConsultingDocumentCreateSerializer(many=True, required=False)
    due_date = serializers.DateField(required=True)
    value = serializers.FloatField()
    customer = serializers.UUIDField(required=False, allow_null=True)
    product_categories = ProductCategoriesCreateSerializer(many=True, required=False)
    opportunity = serializers.UUIDField(allow_null=True, required=False)
    employee_inherit = serializers.UUIDField()

    class Meta:
        model = Consulting
        fields =(
            'opportunity',
            'employee_inherit',
            'title',
            'attachment',
            'document_data',
            'due_date',
            'value',
            'abstract_content',
            'customer',
            'product_categories'
        )


    def validate_value(self, value):
        total_value = 0
        if value:
            for item in self.initial_data.get('product_categories', []):
                total_value += int(item.get('value'))
            if not total_value == value:
                raise serializers.ValidationError(
                    {'value': 'Estimated value must be equal to the sum of product category value'})
            return value
        raise serializers.ValidationError({'value': BaseMsg.REQUIRED})

    @classmethod
    def validate_opportunity(cls, value):
        if value:
            try:
                return Opportunity.objects.get_current(fill__tenant=True, fill__company=True, id=value)
            except Opportunity.DoesNotExist:
                raise serializers.ValidationError({'opportunity': BaseMsg.NOT_EXIST})
        return value

    @classmethod
    def validate_employee_inherit(cls, value):
        if value:
            try:
                return Employee.objects.get_current(fill__tenant=True, fill__company=True, id=value)
            except Employee.DoesNotExist:
                raise serializers.ValidationError({'employee_inherit': BaseMsg.NOT_EXIST})
        return value

    def validate_attachment(self, value):
        user = self.context.get('user', None)
        if user and hasattr(user, 'employee_current_id'):
            state, result = ConsultingAttachment.valid_change(
                current_ids=value, employee_id=user.employee_current_id, doc_id=self.instance.id
            )
            if state is True:
                return result
            raise serializers.ValidationError({'attachment': AttachmentMsg.SOME_FILES_NOT_CORRECT})
        raise serializers.ValidationError({'employee_id': HRMsg.EMPLOYEE_NOT_EXIST})

    def validate_customer(self, value):
        opportunity = self.initial_data.get('opportunity', None)
        if opportunity is None:
            if value:
                try:
                    return Account.objects.filter(id=value).first()
                except Account.DoesNotExist:
                    raise serializers.ValidationError({'customer': 'Customer does not exist'})
            raise serializers.ValidationError({'customer': BaseMsg.REQUIRED})
        return value

    def validate(self, validate_data):
        if validate_data.get('opportunity'):
            validate_data['customer'] = validate_data.get('opportunity').customer
        return validate_data

    @decorator_run_workflow
    def update(self, instance, validated_data):
        attachment = validated_data.pop('attachment', [])
        product_categories = validated_data.pop('product_categories', [])
        document_data = validated_data.pop('document_data', [])
        create_data = {
            'attachment': attachment,
            'product_categories': product_categories,
            'document_data': document_data,
        }
        try:
            with transaction.atomic():
                for key, value in validated_data.items():
                    setattr(instance, key, value)
                instance.save()
                ConsultingCommonCreate.create_sub_models(instance=instance, create_data=create_data)
        except Exception as err:
            logger.error(msg=f'Create consulting errors: {str(err)}')
            raise serializers.ValidationError({'consulting': 'Error creating Consulting'})

        return instance


class ConsultingAccountListSerializer(AbstractListSerializerModel):
    class Meta:
        model = Account
        fields = (
            "id",
            'code',
            "name"
        )


class ConsultingProductCategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ('id', 'code', 'title')


class ConsultingDocumentMasterDataListSerializer(serializers.ModelSerializer):

    class Meta:
        model = DocumentType
        fields = (
            "id",
            'code',
            "title",
        )
