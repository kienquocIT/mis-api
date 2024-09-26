from datetime import timedelta, datetime

from django.contrib.auth.models import AnonymousUser
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from apps.core.hr.models import Employee

from apps.eoffice.meeting.models import MeetingSchedule
from apps.eoffice.businesstrip.models import BusinessRequest
from apps.eoffice.leave.models import (
    LeaveRequestDateListRegister, WorkingHolidayConfig, WorkingCalendarConfig,
    WorkingYearConfig,
)
from apps.sales.opportunity.models import OpportunityMeeting, OpportunityMeetingEmployeeAttended
from apps.shared import mask_view, ResponseController, FORMATTING, Caching, AuthMsg

from misapi.mongo_client import MongoViewParse, mongo_log_auth


class AliveCheckView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(operation_summary='Check session is alive')
    @mask_view(login_require=True)
    def get(self, request, *args, **kwargs):
        user = request.user
        if not user or user.is_authenticated is False or user.is_anonymous is True:
            return ResponseController.unauthorized_401()
        return ResponseController.success_200(data={'state': 'You are still alive.'}, key_data='result')


class AuthLogsView(APIView):
    @swagger_auto_schema(operation_summary="Get log of user's authentication")
    @mask_view(login_require=True)
    def get(self, request, *args, **kwargs):
        if request.user and request.user.is_authenticated and not isinstance(request.user, AnonymousUser):
            view_parse = MongoViewParse(request=request)
            page_size = view_parse.get_page_size()
            page_index = view_parse.get_page_index()
            record_skip = page_size * (page_index - 1)
            ordering = view_parse.get_ordering(
                default_data={
                    'timestamp': -1,
                }
            )
            filter_data = {
                'metadata.service_name': 'AUTH',
                'metadata.user_id': str(request.user.id),
            }
            count = mongo_log_auth.count_documents(filter_data)
            queries = mongo_log_auth.find(
                filter_data,
                sort=ordering,
                skip=record_skip,
                limit=page_size
            )
            results = [
                {
                    'timestamp': FORMATTING.parse_datetime(item['timestamp']),
                    'service_name': item.get('endpoint', ''),
                    'log_level': item.get('log_level', ''),
                    'errors': item.get('errors', ''),
                } for item in queries
            ]
            return ResponseController.success_200(
                data=MongoViewParse.parse_return(
                    results=results,
                    page_index=page_index,
                    page_size=page_size,
                    count=count,
                ),
                key_data='',
            )
        return ResponseController.success_200(data=MongoViewParse.parse_return(results=[]))


class AuthLogReport(APIView):
    @swagger_auto_schema(operation_summary='Chart report data since 7 days')
    @mask_view(login_require=True)
    def get(self, request, *args, **kwargs):
        if request.user and request.user.is_authenticated and not isinstance(request.user, AnonymousUser):
            try:
                range_selected = int(request.query_params.dict().get('range', 7))
                if range_selected not in [7, 14, 30]:
                    raise ValueError()
            except ValueError:
                range_selected = 7

            key_of_cache = f'auth_log_${str(request.user.id)}_{range_selected}'
            data_cached = Caching().get(key_of_cache)
            if data_cached:
                results = data_cached
            else:
                end_time = timezone.now()
                start_time = datetime(year=end_time.year, month=end_time.month, day=end_time.day) - timedelta(
                    days=range_selected
                )
                pipeline = [
                    {
                        "$match": {
                            "timestamp": {"$gte": start_time},
                            "metadata.service_name": "AUTH",
                            "metadata.user_id": str(request.user.id),
                        },
                    },
                    {
                        "$addFields": {"date": {"$dateTrunc": {"date": "$timestamp", "unit": "day"}}}
                    }, {
                        "$group": {
                            "_id": {
                                "date": "$date",
                                "endpoint": "$endpoint",
                                "log_level": "$log_level"
                            },
                            "count": {
                                "$sum": 1
                            }
                        }
                    },
                    {
                        "$group": {
                            "_id": "$_id.date",
                            "details": {
                                "$push": {
                                    "endpoint": "$_id.endpoint",
                                    "log_level": "$_id.log_level",
                                    "count": "$count"
                                }
                            }
                        }
                    },
                    {
                        "$sort": {"_id": 1}
                    },
                ]
                queries = mongo_log_auth.aggregate(pipeline)

                results = [
                    {
                        'date': result['_id'],
                        'details': result['details'],
                    }
                    for result in queries
                ]
                Caching().set(key_of_cache, results, timeout=60)
            return ResponseController.success_200(data=results)
        return ResponseController.success_200(data=MongoViewParse.parse_return(results=[]))


class CalendarByDay(APIView):
    @classmethod
    def parse_day(cls, date_str) -> datetime.date:
        try:
            return datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            pass
        raise serializers.ValidationError(
            {
                'day': AuthMsg.HOME_DAY_CALENDAR_FORMAT_INCORRECT
            }
        )

    @swagger_auto_schema(operation_summary='Get event at day')
    @mask_view(login_require=True)
    def get(self, request, *args, **kwargs):  # pylint: disable=R0914,R0912
        result = {}
        day_check = request.query_params.get('day', None)
        if day_check:  # pylint: disable=R1702
            day_check = self.parse_day(date_str=day_check)
            if day_check:
                employee_id = request.user.employee_current_id
                if employee_id:
                    category = request.query_params.get('category', None)
                    category = [category] if category else [
                        'meeting', 'meeting_opp', 'business_trip', 'leave', 'holiday', 'birthday',
                    ]
                    if 'meeting' in category:
                        objs = MeetingSchedule.objects.select_related('meeting_room_mapped').filter(
                            meeting_start_date=day_check,
                            meeting_schedule_mapped__is_external=False,
                            meeting_schedule_mapped__internal_id=employee_id,
                        )
                        result['meeting'] = []
                        for obj in objs:
                            date_start = datetime.combine(obj.meeting_start_date, obj.meeting_start_time)
                            result['meeting'].append(
                                {
                                    'category': 'EOffice Meeting',
                                    'id': obj.id,
                                    'title': obj.title,
                                    'remark': obj.meeting_content,
                                    'start_date': date_start,
                                    'end_date': date_start + timedelta(minutes=obj.meeting_duration),
                                    **(
                                        {
                                            'location_address': obj.meeting_room_mapped.location,
                                            'location_title': obj.meeting_room_mapped.title,
                                        } if obj.meeting_room_mapped else {}
                                    ),
                                }
                            )
                    if 'meeting_opp' in category:
                        opp_meet_ids = OpportunityMeeting.objects.filter(
                            meeting_date__date=day_check
                        ).values_list('id', flat=True)
                        objs = OpportunityMeetingEmployeeAttended.objects.select_related('meeting_mapped').filter(
                            meeting_mapped_id__in=opp_meet_ids,
                            employee_attended_mapped_id=employee_id,
                        )
                        result['meeting_opp'] = []
                        for obj in objs:
                            date_start = datetime.combine(
                                obj.meeting_mapped.meeting_date, obj.meeting_mapped.meeting_from_time
                            )
                            date_end = datetime.combine(
                                obj.meeting_mapped.meeting_date, obj.meeting_mapped.meeting_to_time
                            )
                            result['meeting_opp'].append(
                                {
                                    'category': 'Opportunity Meeting',
                                    'id': obj.meeting_mapped.id,
                                    'title': obj.meeting_mapped.subject,
                                    'remark': '',
                                    'start_date': date_start,
                                    'end_date': date_end,
                                    'location_address': obj.meeting_mapped.room_location,
                                    'location_title': obj.meeting_mapped.meeting_address,
                                }
                            )
                    if 'business_trip' in category:
                        objs = BusinessRequest.objects.select_related('departure', 'destination').filter(
                            date_f__date=day_check,
                            employee_inherit_id=employee_id,
                            employee_on_trip__contains=str(employee_id)
                        )
                        result['business_trip'] = []
                        for obj in objs:
                            result['business_trip'].append(
                                {
                                    'category': 'Business Trip',
                                    'id': obj.id,
                                    'title': obj.title,
                                    'remark': obj.remark,
                                    'start_date': obj.date_f,
                                    'end_date': obj.date_t,
                                    'location_address': f'{obj.departure.title} → {obj.destination.title}',
                                    'location_title': '',
                                }
                            )
                    if 'leave' in category:
                        objs = LeaveRequestDateListRegister.objects.select_related('leave').filter(
                            date_from=day_check,
                            employee_inherit_id=employee_id,
                        )
                        result['leave'] = []
                        for obj in objs:
                            result['leave'].append(
                                {
                                    'category': 'Leave Register',
                                    'id': obj.id,
                                    'title': obj.leave.title,
                                    'remark': obj.remark,
                                    # 'start_date': obj.date_from,
                                    # 'end_date': obj.date_to,
                                    'start_date': None,
                                    'end_date': None,
                                    'location_address': '',
                                    'location_title': '',
                                }
                            )
                    if 'holiday' in category:
                        result['holiday'] = []
                        working_config = WorkingCalendarConfig.objects.filter_current(fill__company=True).first()
                        if working_config:
                            year_config = WorkingYearConfig.objects.filter(
                                working_calendar=working_config, config_year=timezone.now().year
                            ).first()
                            if year_config:
                                objs = WorkingHolidayConfig.objects.filter(holiday_date_to=day_check, year=year_config)
                                for obj in objs:
                                    result['holiday'].append(
                                        {
                                            'category': 'Holiday',
                                            'id': obj.id,
                                            'title': obj.remark,
                                            'remark': '',
                                            'start_date': None,
                                            'end_date': None,
                                            'location_address': '',
                                            'location_title': '',
                                        }
                                    )
                    if 'birthday' in category:
                        objs = Employee.objects.filter_current(
                            fill__tenant=True,
                            fill__company=True,
                            dob__day=day_check.day,
                            dob__month=day_check.month,
                        )
                        result['birthday'] = []
                        for obj in objs:
                            result['birthday'].append(
                                {
                                    'category': 'Birthday',
                                    'id': obj.id,
                                    'title': obj.get_full_name(),
                                    'remark': '',
                                    'start_date': None,
                                    'end_date': None,
                                    'location_address': '',
                                    'location_title': '',
                                }
                            )

                    if result:
                        cache_key = f'home_calendar_of_{str(employee_id)}'
                        Caching().set(key=cache_key, value=result, timeout=60 * 5)  # 5 minutes
        return ResponseController.success_200(data=result)
