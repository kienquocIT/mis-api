import logging
from datetime import timedelta, datetime

import unicodedata
from django.db.models.functions import Greatest, Coalesce, Concat, Round
from django.utils import timezone
from django.apps import apps
from django.db.models import OuterRef, F, Q, Count, ExpressionWrapper, IntegerField, Subquery, Value, QuerySet

from rest_framework import serializers

from apps.core.hr.models import Employee
from apps.masterdata.saledata.models import Contact, Account
from apps.sales.opportunity.models import OpportunityMeeting, OpportunityCallLog, OpportunityEmail, Opportunity, \
    OpportunityStage
from apps.sales.partnercenter.models import List

logger = logging.getLogger(__name__)

class ListFilterService:
    @classmethod
    def get_filtered_data(cls, list_instance: List) -> list:# pylint: disable=R0912, R0915, R0914
        """
        Return filtered data
        Use in partner center ...
        """
        instance_data = cls.__get_instance_data(list_instance)
        model_code = instance_data['model_code']
        model_class = instance_data['model_class']
        queryset = model_class.objects


        filtered_queryset = cls.filter(list_instance, queryset)
        filter_data = filtered_queryset.values()

        filter_data_list = []
        size = 0

        match model_code:
            case 'account':
                filter_data_list, size = cls.__get_account_list(filter_data)
            case 'contact':
                filter_data_list, size = cls.__get_contact_list(filter_data)

        list_instance.num_of_records = size
        list_instance.save()

        return filter_data_list

    @classmethod
    def filter(cls, list_instance: List, queryset: QuerySet) -> QuerySet | None:
        """
        Apply filter conditions of list_instance to queryset
        Use in report ....
        """
        if list_instance is None:
            logging.error('list_instance is None')
            return None

        instance_data = cls.__get_instance_data(list_instance)

        model_class = instance_data['model_class']
        filter_condition = instance_data['filter_condition']

        overall_results = set()

        # Mapping for handling programmatically filtered fields
        programmatic_handlers = {
            'revenue_ytd': CustomFilter.filter_revenue_ytd,
            'open_opp_num': CustomFilter.filter_open_opp_num,
            'last_contacted_open_opp': CustomFilter.filter_last_contacted_open_opp,
            'curr_opp_stage_id': CustomFilter.filter_curr_opp_stage,
            'contact__owner__name': CustomFilter.filter_contact__owner__name,
            'manager': CustomFilter.filter_manager__full_name,
            'num_sale_orders': CustomFilter.filter_num_sale_orders,
            'gross_margin': CustomFilter.filter_gross_margin,
        }

        # Mapping for operator handling
        operator_handlers = {
            'notexact': lambda field, value: ~Q(**{field: value}),
            'exactnull': lambda field, _: Q(**{f"{field}__exact": None}),
            'notexactnull': lambda field, _: ~Q(**{f"{field}__exact": None}),
            'noticontains': lambda field, value: ~Q(**{f"{field}__icontains": value}),
        }

        for group in filter_condition:
            # init filter result for 1 group
            group_results = None
            for condition in group:
                left = condition.get('left')
                left_field = left.get('code')
                operator = condition.get('operator', 'exact')

                # if condition is 5, right is an object
                if int(condition.get('type')) == 5 and (operator not in ('exactnull', 'notexactnull')):
                    right_obj = condition.get('right')
                    right = str(right_obj.get('id')).replace('-', '')
                else:
                    right = condition.get('right')

                if left_field in programmatic_handlers:
                    handler = programmatic_handlers[left_field]
                    id_list = set(handler(list_instance, operator, right))
                else:
                    # Handle standard fields using operator mapping
                    filter_func = operator_handlers.get(operator, None)
                    if filter_func:
                        group_query = filter_func(left_field, right)
                    else:
                        group_query = Q(**{f"{left_field}__{operator}": right})
                    id_list = set(model_class.objects.
                                   filter_current(fill__company=True).
                                   filter(group_query).
                                   values_list('id', flat=True))

                if group_results is None:
                    group_results = id_list
                else:
                    group_results.intersection_update(id_list)

            if group_results:
                overall_results.update(group_results)

        return queryset.filter(id__in=overall_results)

    @classmethod
    def __get_instance_data(cls, list_instance: List) -> dict:
        """
            Return some data of the instance
        """
        if list_instance.data_object:
            application = list_instance.data_object.application
        else:
            application = list_instance.application
        model_code = application.model_code
        app_label = application.app_label
        model_class = apps.get_model(app_label=app_label, model_name=model_code)

        filter_condition = list_instance.filter_condition

        return {
            "model_code": model_code,
            "model_class": model_class,
            'filter_condition': filter_condition
        }

    @classmethod
    def __get_account_list(cls, filter_data: list) -> (list, int):
        acc_list = []
        size = 0
        for item in filter_data:
            owner_id = item.get('owner_id', None)
            owner_obj = None
            if owner_id:
                owner_obj = Contact.objects.filter(id=str(owner_id)).first()
            item_obj = Account.objects.filter(id=str(item.get('id'))).first()
            revenue_information = Account.get_revenue_information(item_obj)
            acc_list.append({
                'id': item.get('id'),
                'code': item.get('code'),
                'name': item.get('name'),
                'account_type': item.get('account_type'),
                'owner': {
                    "id": owner_obj.id,
                    "fullname": owner_obj.fullname,
                } if owner_obj else {},
                'phone': item.get('phone'),
                'email': item.get('email'),
                'manager': item.get('manager'),
                'credit_limit': {
                    'credit_limit_customer': item.get('credit_limit_customer', 0),
                    'credit_limit_supplier': item.get('credit_limit_supplier', 0),
                },
                'revenue_information': revenue_information
            })
            size += 1
        return acc_list, size

    @classmethod
    def __get_contact_list(cls, filter_data: list) -> (list, int):
        contact_list = []
        size = 0
        for item in filter_data:
            owner_id = item.get('owner_id', None)
            owner_obj = None
            if owner_id:
                owner_obj = Employee.objects.filter(id=str(owner_id)).first()
            contact_list.append({
                'id': item.get('id'),
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
        return contact_list, size

class CustomFilter:
    @classmethod
    def filter_revenue_ytd(cls, obj, operator, right):
        results = set()
        model_class = apps.get_model(
            app_label=obj.data_object.application.app_label,
            model_name=obj.data_object.application.model_code,
        )
        for account in model_class.objects.filter_current(fill__company=True, fill__tenant=True):
            revenue_info = Account.get_revenue_information(account)
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
                    raise serializers.ValidationError(f"Unsupported operator for revenue_ytd: {operator}")
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
                filtered_accounts = annotated_accounts.filter_current(
                    fill__company=True,
                    open_opp_num__gte=right
                )
            case 'lte':
                filtered_accounts = annotated_accounts.filter_current(
                    fill__company=True,
                    open_opp_num__lte=right)
            case 'gt':
                filtered_accounts = annotated_accounts.filter_current(
                    fill__company=True,
                    open_opp_num__gt=right)
            case 'lt':
                filtered_accounts = annotated_accounts.filter_current(
                    fill__company=True,
                    open_opp_num__lt=right)
            case 'exact':
                filtered_accounts = annotated_accounts.filter_current(
                    fill__company=True,
                    open_opp_num__exact=right)
            case 'notexact':
                filtered_accounts = annotated_accounts.filter_current(
                    fill__company=True
                ).filter(
                    ~Q(open_opp_num__exact=right)
                )
            case _:
                raise serializers.ValidationError(f"Unsupported operator for open_opp_num: {operator}")
        return set(filtered_accounts.values_list('id', flat=True))

    @classmethod
    def filter_last_contacted_open_opp(cls, obj, operator, right):  # pylint: disable=W0613
        # Fetch latest meeting, call, and email logs using Subquery
        latest_meeting_date = Subquery(
            OpportunityMeeting.objects.filter(
                Q(opportunity=OuterRef('id')) & ~Q(opportunity__win_rate=100) & ~Q(opportunity__win_rate=0)
            )
            .order_by('-meeting_date')
            .values('meeting_date')[:1]
        )

        latest_call_date = Subquery(
            OpportunityCallLog.objects.filter(
                Q(opportunity=OuterRef('id')) & ~Q(opportunity__win_rate=100) & ~Q(opportunity__win_rate=0)
            )
            .order_by('-call_date')
            .values('call_date')[:1]
        )

        latest_email_date = Subquery(
            OpportunityEmail.objects.filter(
                Q(opportunity=OuterRef('id')) & ~Q(opportunity__win_rate=100) & ~Q(opportunity__win_rate=0)
            )
            .order_by('-date_created')
            .values('date_created')[:1]
        )

        opportunities_with_logs = Opportunity.objects.annotate(
            latest_meeting_date=latest_meeting_date,
            latest_call_date=latest_call_date,
            latest_email_date=latest_email_date,
            latest_log_date=Greatest(
                Coalesce(F('latest_meeting_date'), Value(datetime(1970, 1, 1))),
                Coalesce(F('latest_call_date'), Value(datetime(1970, 1, 1))),
                Coalesce(F('latest_email_date'), Value(datetime(1970, 1, 1))),
            ),
            comparing_days=ExpressionWrapper(
                (timezone.now() - F('latest_log_date')) / timedelta(days=1),
                output_field=IntegerField()
            )
        ).filter(
            Q(latest_meeting_date__isnull=False) |
            Q(latest_call_date__isnull=False) |
            Q(latest_email_date__isnull=False)
        )

        match operator:
            case 'gte':
                filtered_opportunities = opportunities_with_logs.filter(comparing_days__gte=right)
            case 'lte':
                filtered_opportunities = opportunities_with_logs.filter(comparing_days__lte=right)
            case 'gt':
                filtered_opportunities = opportunities_with_logs.filter(comparing_days__gt=right)
            case 'lt':
                filtered_opportunities = opportunities_with_logs.filter(comparing_days__lt=right)
            case 'exact':
                filtered_opportunities = opportunities_with_logs.filter(comparing_days__exact=right)
            case 'notexact':
                filtered_opportunities = opportunities_with_logs.exclude(comparing_days__exact=right)
            case _:
                raise serializers.ValidationError(f"Unsupported operator for last_contacted_open_opp: {operator}")

        account_ids = filtered_opportunities.filter_current(fill__company=True).values_list('customer_id', flat=True)

        return set(account_ids)

    @classmethod
    def filter_curr_opp_stage(cls, obj, operator, right):
        model_class = apps.get_model(
            app_label=obj.data_object.application.app_label,
            model_name=obj.data_object.application.model_code,
        )
        curr_stage_id_subquery = OpportunityStage.objects.filter(
            opportunity__customer=OuterRef('id'),
            is_current=True
        ).values('stage_id')[:1]

        annotated_accounts = model_class.objects.annotate(
            curr_stage_id=curr_stage_id_subquery
        )

        filter_condition = {f"curr_stage_id__{operator}": right}

        filtered_accounts = annotated_accounts.filter_current(fill__company=True).filter(**filter_condition)
        return set(filtered_accounts.values_list('id', flat=True))

    @classmethod
    def filter_contact__owner__name(cls, obj, operator, right):  # pylint: disable=W0613
        annotated_employees = Employee.objects.annotate(
            full_name=Concat('last_name', Value(' '), 'first_name')
        )
        operator_handlers = {
            'notexact': lambda field, value: ~Q(**{field: value}),
            'exactnull': lambda field, _: Q(**{f"{field}__exact": None}),
            'notexactnull': lambda field, _: ~Q(**{f"{field}__exact": None}),
            'noticontains': lambda field, value: ~Q(**{f"{field}__icontains": value}),
        }
        filter_func = operator_handlers.get(operator, None)
        if filter_func:
            group_query = filter_func('full_name', right)
        else:
            group_query = Q(**{f"full_name__{operator}": right})
        filtered_employees = annotated_employees.filter_current(fill__company=True).filter(group_query)

        filtered_contacts = Contact.objects.filter(
            owner__in=filtered_employees
        )

        return set(filtered_contacts.values_list('id', flat=True))

    @classmethod
    def filter_manager__full_name(cls, obj, operator, right):  # pylint: disable=W0613
        normalized_right = normalize_text(right)

        accounts = Account.objects.filter_current(fill__company=True)

        matching_account_ids = set()

        for account in accounts:
            normalized_manager_names = [normalize_text(manager.get("full_name", "")) for manager in account.manager]

            if operator == "icontains" and any(normalized_right in name for name in normalized_manager_names):
                matching_account_ids.add(account.id)
            elif operator == "noticontains" and all(normalized_right not in name for name in normalized_manager_names):
                matching_account_ids.add(account.id)
            elif operator == "exact" and any(normalized_right == name for name in normalized_manager_names):
                matching_account_ids.add(account.id)
            elif operator == "notexact" and all(normalized_right != name for name in normalized_manager_names):
                matching_account_ids.add(account.id)

        # Handle null cases
        if operator == 'exactnull':
            matching_account_ids = set(accounts.filter(manager__exact=None).values_list('id', flat=True))
        elif operator == 'notexactnull':
            matching_account_ids = set(accounts.exclude(manager__exact=None).values_list('id', flat=True))

        return matching_account_ids

    @classmethod
    def filter_num_sale_orders(cls, obj, operator, right):  # pylint: disable=W0613
        annotated_accounts = Account.objects.annotate(
            order_count=Count('sale_order_customer')
        ).filter_current(fill__company=True)
        match operator:
            case 'gte':
                filtered_accounts = annotated_accounts.filter(order_count__gte=right)
            case 'lte':
                filtered_accounts = annotated_accounts.filter(order_count__lte=right)
            case 'gt':
                filtered_accounts = annotated_accounts.filter(order_count__gt=right)
            case 'lt':
                filtered_accounts = annotated_accounts.filter(order_count__lt=right)
            case 'exact':
                filtered_accounts = annotated_accounts.filter(order_count__exact=right)
            case 'notexact':
                filtered_accounts = annotated_accounts.exclude(order_count__exact=right)
            case _:
                raise serializers.ValidationError(f"Unsupported operator for num_sale_orders: {operator}")

        account_ids = filtered_accounts.values_list('id', flat=True)

        return set(account_ids)

    @classmethod
    def filter_gross_margin(cls, obj, operator, right):
        application = obj.application
        model_code = application.model_code
        app_label = application.app_label
        model_class = apps.get_model(app_label=app_label, model_name=model_code)

        right_ratio = round(int(right) / 100, 4)

        annotated_report = model_class.objects.annotate(
            gross_margin=Round(F('gross_profit') / F('revenue'), 4)
        )
        filter_kwargs = {f"gross_margin__{operator}": right_ratio}
        return annotated_report.filter(**filter_kwargs).values_list('id', flat=True)

# e.g: Nguyễn => nguyen
def normalize_text(text):
    """Normalize text by removing diacritical marks and converting to lowercase."""
    normalized = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    return normalized.lower()