import logging
from django.apps import apps

from rest_framework import serializers

from apps.core.base.models import ApplicationProperty
from apps.core.hr.models import Employee
from apps.masterdata.saledata.models import Contact, Account, Industry
from apps.sales.opportunity.models import OpportunityConfigStage
from apps.sales.partnercenter.models import List, DataObject
from apps.sales.partnercenter.services import ListFilterService
from apps.sales.partnercenter.translation import ListMsg
from apps.shared import BaseMsg

logger = logging.getLogger(__name__)


class ListDataObjectListSerializer(serializers.ModelSerializer):

    class Meta:
        model = DataObject
        fields = (
            'id',
            'title',
            'application_id'
        )


class ListListSerializer(serializers.ModelSerializer):
    data_object = serializers.SerializerMethodField()

    class Meta:
        model = List
        fields = (
            'id',
            'title',
            'data_object',
            'num_of_records',
            'date_created'
        )

    @classmethod
    def get_data_object(cls, obj):
        return {
            'id': obj.data_object.id,
            'title': obj.data_object.title,
        } if obj.data_object else {}


class ListCreateSerializer(serializers.ModelSerializer):
    filter_condition = serializers.JSONField()
    data_object = serializers.UUIDField(required=False)

    class Meta:
        model = List
        fields = (
            'title',
            'data_object',
            'filter_condition'
        )

    @classmethod
    def validate_data_object(cls, value):
        if value:
            try:
                return DataObject.objects.get(id=value)
            except:
                raise serializers.ValidationError({'data_object': BaseMsg.NOT_EXIST})
        raise serializers.ValidationError({'data_object': BaseMsg.REQUIRED})

    @classmethod
    def validate_filter_condition(cls, value):
        if not value:
            raise serializers.ValidationError({'filter_condition': BaseMsg.REQUIRED})
        return value

    def validate(self, validate_data): # pylint: disable=R0914
        filter_condition = validate_data['filter_condition']
        for filter_group in filter_condition:
            for filter_item in filter_group:
                left_id = filter_item.get('left', None)
                right = filter_item.get('right', None)
                left_type = filter_item.get('type', None)
                operator = filter_item.get('operator', None)

                if (not left_type) or (str(left_type) not in ['1', '2', '3', '4', '5', '6']):
                    raise serializers.ValidationError({'filter_condition': ListMsg.TYPE_MISSING})

                if str(left_type) == '6' and not right.isnumeric():
                    raise serializers.ValidationError({'right': ListMsg.VAL_MUST_BE_A_NUMBER})

                if operator not in ('exactnull', 'notexactnull'):
                    if not left_id or not right:
                        raise serializers.ValidationError({'filter_condition': ListMsg.OPERAND_MISSING})

                # validate left object
                left_obj = ApplicationProperty.objects.filter(id=left_id).first()
                if not left_obj:
                    logging.error('Application Property Object not found')
                    raise serializers.ValidationError(ListMsg.STH_WENT_WRONG)

                filter_item['left'] = {
                    "id": str(left_obj.id),
                    "code": f'{left_obj.code}',
                    "title": left_obj.title,
                    "type": left_obj.type,
                }

                if left_type == 5:
                    if operator not in ('exactnull', 'notexactnull'):
                        right_id = right.get('id', None)
                        content_type = getattr(left_obj, 'content_type', None)
                        if not content_type:
                            logging.error('Application Property Object missing content_type')
                            raise serializers.ValidationError(ListMsg.STH_WENT_WRONG)

                        app_label = content_type.split('.')[0]
                        model_name = content_type.split('.')[1]
                        model_class = apps.get_model(app_label=app_label, model_name=model_name)
                        if not model_class:
                            logging.error('Model Class for right operand not found')
                            raise serializers.ValidationError(ListMsg.STH_WENT_WRONG)

                        right_obj = model_class.objects.filter(id=right_id).first()

                        if not right_obj:
                            logging.error('Model Class Object for right operand not found')
                            raise serializers.ValidationError(ListMsg.STH_WENT_WRONG)

                        filter_item['right']['id'] = right_id
                    filter_item['left'] = {
                        "id": str(left_obj.id),
                        "code": f'{left_obj.code}_id',
                        "title": left_obj.title,
                        "type": left_obj.type,
                        "content_type": left_obj.content_type,
                    }
        return validate_data

    def create(self, validated_data):
        instance = List.objects.create(**validated_data)
        return instance


class ListUpdateSerializer(serializers.ModelSerializer):
    filter_condition = serializers.JSONField()
    data_object = serializers.UUIDField(required=False)

    class Meta:
        model = List
        fields = (
            'title',
            'data_object',
            'filter_condition'
        )

    @classmethod
    def validate_data_object(cls, value):
        if value:
            try:
                return DataObject.objects.get(id=value)
            except:
                raise serializers.ValidationError({'data_object': BaseMsg.NOT_EXIST})
        raise serializers.ValidationError({'data_object': BaseMsg.REQUIRED})

    @classmethod
    def validate_filter_condition(cls, value):
        if not value:
            raise serializers.ValidationError({'filter_condition': BaseMsg.REQUIRED})
        return value

    def validate(self, validate_data): # pylint: disable=R0914
        filter_condition = validate_data['filter_condition']
        for filter_group in filter_condition:
            for filter_item in filter_group:
                left_id = filter_item.get('left', None)
                right = filter_item.get('right', None)
                left_type = filter_item.get('type', None)
                operator = filter_item.get('operator', None)
                if (not left_type) or (str(left_type) not in ['1', '2', '3', '4', '5', '6']):
                    raise serializers.ValidationError({'filter_condition': ListMsg.TYPE_MISSING})

                if str(left_type) == '6' and not right.isnumeric():
                    raise serializers.ValidationError({'right': ListMsg.VAL_MUST_BE_A_NUMBER})

                if operator not in ('exactnull', 'notexactnull'):
                    if not left_id or not right:
                        raise serializers.ValidationError({'filter_condition': ListMsg.OPERAND_MISSING})

                # validate left object
                left_obj = ApplicationProperty.objects.filter(id=left_id).first()
                if not left_obj:
                    logging.error('Application Property Object not found')
                    raise serializers.ValidationError(ListMsg.STH_WENT_WRONG)

                filter_item['left'] = {
                    "id": str(left_obj.id),
                    "code": f'{left_obj.code}',
                    "title": left_obj.title,
                    "type": left_obj.type,
                }

                if left_type == 5:
                    if operator not in ('exactnull', 'notexactnull'):

                        right_id = right.get('id')
                        content_type = getattr(left_obj, 'content_type', None)
                        if not content_type:
                            logging.error('Application Property Object missing content_type')
                            raise serializers.ValidationError(ListMsg.STH_WENT_WRONG)

                        app_label = content_type.split('.')[0]
                        model_name = content_type.split('.')[1]
                        model_class = apps.get_model(app_label=app_label, model_name=model_name)
                        if not model_class:
                            logging.error('Model Class for right operand not found')
                            raise serializers.ValidationError(ListMsg.STH_WENT_WRONG)

                        right_obj = model_class.objects.filter(id=right_id).first()

                        if not right_obj:
                            logging.error('Model Class Object for right operand not found')
                            raise serializers.ValidationError(ListMsg.STH_WENT_WRONG)
                        filter_item['right']['id'] = right_id

                    filter_item['left'] = {
                        "id": str(left_obj.id),
                        "code": f'{left_obj.code}_id',
                        "title": left_obj.title,
                        "type": left_obj.type,
                        "content_type": left_obj.content_type,
                    }
        return validate_data

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance


class ListDetailSerializer(serializers.ModelSerializer):
    data_object = serializers.SerializerMethodField()
    filter_condition = serializers.SerializerMethodField()

    class Meta:
        model = List
        fields = (
            'title',
            'data_object',
            'filter_condition',
        )

    @classmethod
    def get_data_object(cls, obj):
        return {
            'id': obj.data_object.id,
            'title': obj.data_object.title,
        } if obj.data_object else {}

    @classmethod
    def get_filter_condition(cls, obj):
        # if obj.filter_condition.type == 5 :
        #     for filter_group in obj.filter_condition:
        #         for filter_item in filter_group:
        #             # obj =
        #             ...
        return obj.filter_condition


class ListResultListSerializer(serializers.ModelSerializer):
    list_result = serializers.SerializerMethodField()
    data_object = serializers.SerializerMethodField()

    class Meta:
        model = List
        fields = (
            'id',
            'title',
            'filter_condition',
            'list_result',
            'data_object'
        )

    @classmethod
    def get_list_result(cls, obj):
        filter_data_list = ListFilterService.get_filtered_data(obj)
        return filter_data_list

    @classmethod
    def get_data_object(cls, obj):
        return obj.data_object.title


class ListEmployeeListSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = (
            'id',
            'code',
            'title'
        )

    @classmethod
    def get_title(cls, obj):
        return obj.get_full_name(2)


class ListContactListSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()

    class Meta:
        model = Contact
        fields = (
            'id',
            'code',
            'title'
        )

    @classmethod
    def get_title(cls, obj):
        return obj.fullname


class ListIndustryListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Industry
        fields = (
            'id',
            'code',
            'title'
        )


class ListOpportunityConfigStageListSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()

    class Meta:
        model = OpportunityConfigStage
        fields = (
            'id',
            'title'
        )

    @classmethod
    def get_title(cls, obj):
        return obj.indicator


class ListAccountListSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()

    class Meta:
        model = Account
        fields = (
            'id',
            'code',
            'title'
        )

    @classmethod
    def get_title(cls, obj):
        return obj.name
