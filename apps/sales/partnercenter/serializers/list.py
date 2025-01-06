import json
import logging
import datetime
from datetime import timedelta

from django.db.models.functions import Greatest
from django.utils import timezone
from django.apps import apps
from django.db.models import Subquery, OuterRef, F, Q, Count

from rest_framework import serializers

from apps.core.base.models import ApplicationProperty
from apps.core.hr.models import Employee
from apps.masterdata.saledata.models import Contact, Account, Industry
from apps.sales.opportunity.models import OpportunityMeeting, OpportunityCallLog, \
    OpportunityEmail
from apps.sales.partnercenter.models import List, DataObject
from apps.sales.partnercenter.tasks import update_num_of_records
from apps.sales.partnercenter.translation import ListMsg
from apps.shared import BaseMsg, call_task_background

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

    def validate(self, validate_data):
        filter_condition = validate_data['filter_condition']
        for filter_group in filter_condition:
            for filter_item in filter_group:
                left_id = filter_item.get('left', None)
                right = filter_item.get('right', None)
                left_type = filter_item.get('type', None)

                if (not left_type) or (str(left_type) not in ['1', '2', '3', '4', '5', '6']):
                    raise serializers.ValidationError({'filter_condition': ListMsg.TYPE_MISSING})

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
                    right_id = right['id']
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
                    filter_item['left'] = {
                        "id": str(left_obj.id),
                        "code": f'{left_obj.code}_id',
                        "title": left_obj.title,
                        "type": left_obj.type,
                        "content_type": left_obj.content_type,
                    }
                    filter_item['right']['id'] = right_id
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

    def validate(self, validate_data):
        filter_condition = validate_data['filter_condition']
        for filter_group in filter_condition:
            for filter_item in filter_group:
                left_id = filter_item.get('left', None)
                right = filter_item.get('right', None)
                left_type = filter_item.get('type', None)

                if (not left_type) or (str(left_type) not in ['1', '2', '3', '4', '5', '6']):
                    raise serializers.ValidationError({'filter_condition': ListMsg.TYPE_MISSING})

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
                    right_id = right['id']
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
                    filter_item['left'] = {
                        "id": str(left_obj.id),
                        "code": f'{left_obj.code}_id',
                        "title": left_obj.title,
                        "type": left_obj.type,
                        "content_type": left_obj.content_type,
                    }
                    filter_item['right']['id'] = right_id
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
    def filter_revenue_ytd(cls, obj, operator, right):
        results = set()
        model_class = apps.get_model(
            app_label=obj.data_object.application.app_label,
            model_name=obj.data_object.application.model_code,
        )
        for account in model_class.objects.all():
            revenue_info = get_revenue_information(account)
            revenue_ytd = revenue_info['revenue_ytd']

            # Apply operator logic
            match operator:
                case 'gte':
                    if revenue_ytd >= float(right):
                        results.add(account.id)
                case 'lte':
                    if revenue_ytd <= float(right):
                        results.add(account.id)
                case 'gt':
                    if revenue_ytd > float(right):
                        results.add(account.id)
                case 'lt':
                    if revenue_ytd < float(right):
                        results.add(account.id)
                case 'exact':
                    if revenue_ytd == float(right):
                        results.add(account.id)
                case 'notexact':
                    if revenue_ytd != float(right):
                        results.add(account.id)
                case _:
                    raise ValueError(f"Unsupported operator for revenue_ytd: {operator}")
        return results

    @classmethod
    def filter_open_opp_num(cls, obj, operator, right):
        model_class = apps.get_model(
            app_label=obj.data_object.application.app_label,
            model_name=obj.data_object.application.model_code,
        )
        annotated_accounts = model_class.objects.annotate(
            open_opp_num=Count(
                'opportunity_customer',
                filter=Q(
                    opportunity_customer__win_rate__gt=0,
                    opportunity_customer__win_rate__lt=100
                )
            )
        )
        # Apply operator logic
        match operator:
            case 'gte':
                filtered_accounts = annotated_accounts.filter(
                    Q(open_opp_num__gte=right))
            case 'lte':
                filtered_accounts = annotated_accounts.filter(
                    Q(open_opp_num__lte=right))
            case 'gt':
                filtered_accounts = annotated_accounts.filter(
                    Q(open_opp_num__gt=right))
            case 'lt':
                filtered_accounts = annotated_accounts.filter(
                    Q(open_opp_num__lt=right))
            case 'exact':
                filtered_accounts = annotated_accounts.filter(
                    Q(open_opp_num__exact=right))
            case 'notexact':
                filtered_accounts = annotated_accounts.filter(
                    ~Q(open_opp_num__exact=right))
            case _:
                raise ValueError(f"Unsupported operator for open_opp_num: {operator}")
        return set(filtered_accounts.values_list('id', flat=True))
    @classmethod
    def filter_last_contacted_open_opp(cls, obj, operator, right):
        # Get model class
        model_class = apps.get_model(
            app_label=obj.data_object.application.app_label,
            model_name=obj.data_object.application.model_code,
        )
        cutoff_date = timezone.now() - timedelta(days=int(right))

        # Fetch latest meeting, call, and email logs using Subquery
        latest_meeting_date = Subquery(
            OpportunityMeeting.objects.filter(
                Q(opportunity__customer=OuterRef('id')) & ~Q(opportunity__win_rate=100) & ~Q(opportunity__win_rate=0)
            )
            .order_by('-meeting_date')
            .values('meeting_date')[:1]
        )

        latest_call_date = Subquery(
            OpportunityCallLog.objects.filter(
                Q(opportunity__customer=OuterRef('id')) & ~Q(opportunity__win_rate=100) & ~Q(opportunity__win_rate=0)
            )
            .order_by('-call_date')
            .values('call_date')[:1]
        )

        latest_email_date = Subquery(
            OpportunityEmail.objects.filter(
                Q(opportunity__customer=OuterRef('id')) & ~Q(opportunity__win_rate=100) & ~Q(opportunity__win_rate=0)
            )
            .order_by('-date_created')
            .values('date_created')[:1]
        )

        annotated_accounts = model_class.objects.annotate(
            latest_meeting_date=latest_meeting_date,
            latest_call_date=latest_call_date,
            latest_email_date=latest_email_date,
            latest_log_date=Greatest(
                F('latest_meeting_date'),
                F('latest_call_date'),
                F('latest_email_date'),
            ),
        )

        match operator:
            case 'gte':
                filtered_accounts = annotated_accounts.filter(latest_log_date__lte=cutoff_date)
            case 'lte':
                filtered_accounts = annotated_accounts.filter(latest_log_date__gte=cutoff_date)
            case 'gt':
                filtered_accounts = annotated_accounts.filter(latest_log_date__lt=cutoff_date)
            case 'lt':
                filtered_accounts = annotated_accounts.filter(latest_log_date__gt=cutoff_date)
            case 'exact':
                filtered_accounts = annotated_accounts.filter(latest_log_date__exact=cutoff_date)
            case 'notexact':
                filtered_accounts = annotated_accounts.filter(~Q(**{f"latest_log_date__exact": cutoff_date}))
            case _:
                raise ValueError(f"Unsupported operator for last_contacted_open_opp: {operator}")

        # Return matching account IDs
        return set(filtered_accounts.values_list('id', flat=True))

    @classmethod
    def get_list_result(cls, obj):
        application = obj.data_object.application
        model_code = application.model_code
        app_label = application.app_label
        model_class = apps.get_model(app_label=app_label, model_name=model_code)

        filter_condition = obj.filter_condition
        overall_results = set()

        # Mapping for handling programmatically filtered fields
        programmatic_handlers = {
            'revenue_ytd': cls.filter_revenue_ytd,
            'open_opp_num': cls.filter_open_opp_num,
            'last_contacted_open_opp': cls.filter_last_contacted_open_opp
        }

        # Mapping for operator handling
        operator_handlers = {
            'notexact': lambda field, value: ~Q(**{field: value}),
            'exactnull': lambda field, _: Q(**{f"{field}__exact": None}),
            'noticontains': lambda field, value: ~Q(**{f"{field}__icontains": value}),
        }

        for group in filter_condition:
            group_results = None
            for condition in group:
                left = condition.get('left')
                left_field = left.get('code')
                operator = condition.get('operator', 'exact')

                if int(condition.get('type')) == 5:
                    right_obj = condition.get('right')
                    right = str(right_obj['id']).replace('-', '')
                else:
                    right = condition.get('right')

                if left_field in programmatic_handlers:
                    handler = programmatic_handlers[left_field]
                    queryset = set(handler(obj, operator, right))
                else:
                    # Handle standard fields using operator mapping
                    filter_func = operator_handlers.get(operator, None)
                    if filter_func:
                        group_query = filter_func(left_field, right)
                    else:
                        group_query = Q(**{f"{left_field}__{operator}": right})
                    queryset = set(model_class.objects.filter(group_query).values_list('id', flat=True))

                if group_results is None:
                    group_results = queryset
                else:
                    group_results.intersection_update(queryset)

            if group_results:
                overall_results.update(group_results)
        filter_data = model_class.objects.filter(id__in=overall_results).values()

        filter_data_list = []
        size = 0
        match model_code:
            case 'account':
                for item in filter_data:
                    owner_id = item.get('owner_id', None)
                    owner_obj = None
                    if owner_id:
                        owner_obj = Contact.objects.filter(id=str(owner_id).replace('-','')).first()
                    item_obj = Account.objects.filter(id=str(item['id']).replace('-','')).first()
                    revenue_information = get_revenue_information(item_obj)
                    filter_data_list.append({
                        'code' : item.get('code'),
                        'name' : item.get('name'),
                        'account_type': item.get('account_type'),
                        'owner' : {
                            "id": owner_obj.id,
                            "fullname": owner_obj.fullname,
                        } if owner_obj else {},
                        'phone' : item.get('phone'),
                        'email': item.get('email'),
                        'manager' : item.get('manager'),
                        'credit_limit':{
                            'credit_limit_customer': item.get('credit_limit_customer', 0),
                            'credit_limit_supplier': item.get('credit_limit_supplier', 0),
                        },
                        'revenue_information': revenue_information
                    })
                    size += 1
            case 'contact':
                for item in filter_data:
                    owner_id = item.get('owner_id', None)
                    owner_obj = None
                    if owner_id:
                        owner_obj = Employee.objects.filter(id=str(owner_id).replace('-', '')).first()
                    filter_data_list.append({
                        'code': item.get('code'),
                        'name': item.get('fullname'),
                        'job_title': item.get('job_title'),
                        'owner': {
                            "id": owner_obj.id,
                            "fullname": f"{owner_obj.last_name} {owner_obj.first_name}",
                        } if owner_obj else {},
                        'phone': item.get('phone'),
                        'email': item.get('email'),
                    })
                    size += 1
        call_task_background(
            update_num_of_records,
            **{
                "list_obj": obj,
                "size": size,
            }
        )
        return filter_data_list

    @classmethod
    def get_data_object(cls, obj):
        return obj.data_object.title


def get_log_date(log):
    if isinstance(log, OpportunityMeeting):
        return log.meeting_date
    elif isinstance(log, OpportunityCallLog):
        return log.call_date
    elif isinstance(log, OpportunityEmail):
        return log.date_created
    return None

def get_revenue_information(obj):
    current_date = timezone.now()
    revenue_ytd = 0
    order_number = 0
    for period in obj.company.saledata_periods_belong_to_company.all():
        if period.fiscal_year == current_date.year:
            start_date_str = str(period.start_date) + ' 00:00:00'
            start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d %H:%M:%S")
            for customer_revenue in obj.report_customer_customer.filter(
                    group_inherit__is_delete=False, sale_order__system_status=3
            ):
                if customer_revenue.date_approved:
                    if start_date <= customer_revenue.date_approved <= current_date:
                        revenue_ytd += customer_revenue.revenue
                        order_number += 1
    return {
        'revenue_ytd': revenue_ytd,
        'order_number': order_number,
        'revenue_average': round(revenue_ytd / order_number) if order_number > 0 else 0,
    }


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
