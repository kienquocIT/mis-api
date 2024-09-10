from datetime import datetime, timedelta

from django.contrib.auth.models import AnonymousUser
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView

from apps.sales.task.models import OpportunityTaskSummaryDaily
from apps.sales.task.signals import OppTaskSummaryHandler
from apps.shared import mask_view, Caching, ResponseController
from misapi.mongo_client import mongo_log_opp_task


class MyTaskReportView(APIView):
    def get_ratio_report(self, start_time, end_time):
        task_status_specials = [
            "FINISH_TASK",
            "ASSIGN_TASK",
            "NOT_FINISH",
        ]
        pipeline = [
            {
                "$match": {
                    "timestamp": {"$gte": start_time, "$lt": end_time},
                    "metadata.employee_inherit_id": str(self.request.user.employee_current_id),
                    "metadata.tenant_id": str(self.request.user.tenant_current_id),
                    "metadata.company_id": str(self.request.user.company_current_id),
                    "task_status": {
                        "$nin": task_status_specials,
                    }
                },
            },
            {
                "$addFields": {
                    "date": {
                        "$dateTrunc": {"date": "$timestamp", "unit": "day"}
                    }
                }
            },
            {
                "$group": {
                    "_id": {
                        "task_id": "$task_id",
                        "task_status": "$task_status",
                    },
                    "task_status_translate": {"$first": "$task_status_translate"},
                    "task_color": {"$first": "$task_color"},
                    "not_finish_total": {"$first": "$not_finish_total"},
                }
            },
            {
                "$group": {
                    "_id": "$_id.task_status",
                    "count": {"$sum": 1},
                    "task_status_translate": {"$first": "$task_status_translate"},
                    "task_color": {"$first": "$task_color"},
                    "not_finish_total": {"$first": "$not_finish_total"},
                }
            },
            {
                "$sort": {"_id": 1}
            },
        ]
        queries = mongo_log_opp_task.aggregate(pipeline)
        results = [
            {
                'task_status': result['_id'],
                'task_status_translate': result['task_status_translate'],
                'task_color': result['task_color'],
                'count': result['count'],
            }
            for result in queries
        ]
        return results

    def get_by_day_report(self, start_time, end_time):
        # task_status_specials = [
        #     "FINISH_TASK",
        #     "ASSIGN_TASK",
        # ]
        pipeline = [
            {
                "$match": {
                    "timestamp": {"$gte": start_time, "$lt": end_time},
                    "metadata.employee_inherit_id": str(self.request.user.employee_current_id),
                    "metadata.tenant_id": str(self.request.user.tenant_current_id),
                    "metadata.company_id": str(self.request.user.company_current_id),
                    # "task_status": {
                    #     "$in": task_status_specials
                    # },
                },
            },
            {
                "$addFields": {
                    "date": {
                        "$dateTrunc": {"date": "$timestamp", "unit": "day"}
                    }
                }
            },
            {
                "$group": {
                    "_id": {
                        "task_id": "$task_id",
                        "task_status": "$task_status",
                        "date": "$date"
                    },
                    "task_status_translate": {"$first": "$task_status_translate"},
                    "task_color": {"$first": "$task_color"},
                }
            },
            {
                "$group": {
                    "_id": {
                        "date": "$_id.date",
                        "task_status": "$_id.task_status"
                    },
                    "count": {"$sum": 1},
                    "task_status_translate": {"$first": "$task_status_translate"},
                    "task_color": {"$first": "$task_color"},
                }
            },
            {
                "$group": {
                    "_id": "$_id.date",
                    "details": {
                        "$push": {
                            "task_status": "$_id.task_status",
                            "task_status_translate": "$task_status_translate",
                            "task_color": "$task_color",
                            "count": "$count",
                        }
                    }
                }
            },
            {
                "$sort": {"_id": 1}
            },
        ]
        queries = mongo_log_opp_task.aggregate(pipeline)
        results = [
            {
                'date': result['_id'],
                'details': result['details'],
            }
            for result in queries
        ]
        return results

    @swagger_auto_schema(operation_summary='Report for employee inherit')
    @mask_view(login_require=True)
    def get(self, request, *args, **kwargs):  # pylint: disable=R0914
        if request.user and request.user.is_authenticated and not isinstance(request.user, AnonymousUser):
            employee_id = request.user.employee_current_id
            if employee_id:
                report_type = request.query_params.get('report_type', 'ratio')
                try:
                    range_selected = int(request.query_params.dict().get('range', 7))
                    if range_selected not in [7, 14, 30]:
                        raise ValueError()
                except ValueError:
                    range_selected = 7

                date_now = timezone.now()
                date_tmp = datetime(year=date_now.year, month=date_now.month, day=date_now.day)
                end_time = date_tmp + timedelta(hours=24)
                start_time = date_tmp - timedelta(days=range_selected)

                dt_format = "%Y_%m_%d_%H_%M_%S"
                key_of_cache = f'my_task_report_{str(request.user.id.hex)}'
                key_of_cache += f'__{report_type}'
                key_of_cache += f'__{start_time.strftime(dt_format)}_{end_time.strftime(dt_format)}'
                cache_cls = Caching()

                results_cached = cache_cls.get(key=key_of_cache)
                if results_cached:
                    results = results_cached
                else:
                    results = {
                        # 'ratio': self.get_ratio_report(start_time=start_time, end_time=end_time),
                        'by_day': self.get_by_day_report(start_time=start_time, end_time=end_time),
                    }

                if results:
                    cache_cls.set(key=key_of_cache, value=results, timeout=60)  # 60 seconds
                    return ResponseController.success_200(data=results)
        return ResponseController.success_200(data=[])


class MyTaskSummaryReportView(APIView):
    @swagger_auto_schema(operation_summary='Summary Report for employee inherit')
    @mask_view(login_require=True)
    def get(self, request, *args, **kwargs):
        if request.user and request.user.is_authenticated and not isinstance(request.user, AnonymousUser):
            employee_id = request.user.employee_current_id
            if employee_id:
                summary_obj = OppTaskSummaryHandler(employee_id=request.user.employee_current_id)
                obj = summary_obj.get_obj()
                if isinstance(obj, OpportunityTaskSummaryDaily) \
                        and obj.state == 1 \
                        and obj.updated_at.date() == timezone.now().date():
                    report_data = summary_obj.summary_report(obj=obj)
                    return ResponseController.success_200(data={'state': 'READY', 'data': report_data})
        return ResponseController.success_200(data={'state': 'WAIT'})
