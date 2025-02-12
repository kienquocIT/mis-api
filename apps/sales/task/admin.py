from datetime import timedelta

from django.contrib import admin
from django.utils import timezone
from django.utils.safestring import mark_safe

from apps.core.hr.models import Employee
from apps.sharedapp.admin import AbstractAdmin, my_admin_site
from apps.sales.task.models import OpportunityTask
from misapi.mongo_client import mongo_log_opp_task


@admin.register(OpportunityTask, site=my_admin_site)
class OpportunityTaskAdmin(AbstractAdmin):
    list_display = [
        'title', 'code', 'task_status', 'start_date_short', 'end_date_short', 'estimate',
        'employee_inherit',
    ]

    @classmethod
    def start_date_short(cls, obj):
        return obj.start_date.strftime("%Y-%m-%d")

    @classmethod
    def end_date_short(cls, obj):
        return obj.end_date.strftime("%Y-%m-%d")

    list_filter = [
        'company',
        'employee_inherit',
    ]


class LogTaskOfEmployee(Employee):
    class Meta:
        proxy = True
        verbose_name = "Log Task of Employee"
        verbose_name_plural = "Log Task of Employee"
        app_label = 'task'


@admin.register(LogTaskOfEmployee, site=my_admin_site)
class LogTaskOfEmployeeAdmin(AbstractAdmin):
    list_display = [
        'first_name', 'last_name',
        'company',
    ]

    list_filter = ['company', ]
    ordering = ['company_id', 'first_name', ]
    search_fields = ['first_name', 'last_name', ]

    fields = [
        'tenant', 'company', 'code', 'first_name', 'last_name',
        'summary_by_day',
        'task_log',
    ]

    @classmethod
    def summary_by_day(cls, obj):
        pipeline = [
            {
                "$match": {
                    "metadata.employee_inherit_id": str(obj.id),
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
                "$sort": {"_id": -1}
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

        if len(results) == 0:
            return "-"

        html = []
        for item in results:
            html_li = []
            for child in item.get('details', []):
                html_li.append(
                    f"""
                        <div style="display: grid;grid-template-columns: 200px 100px;">
                            <span>{child.get('task_status', '-')}</span>
                            <span>{child.get('count', '-')}</span>
                        </div>
                    """
                )

            html.append(
                f"""
                    <tr>
                        <td>{item['date']}</td>
                        <td>
                            <div style="display: grid;grid-template-columns: auto;gap: 10px;">
                                {"".join(html_li)}
                            </div>
                        </td>
                    </tr>
                """
            )

        return mark_safe(
            f"""
                <table style="width: 100%;">
                    <thead>
                        <tr>
                            <th>Date</th>
                            <th>Details</th>
                        </tr>
                    </thead>
                    <tbody>{"".join(html)}</tbody>
                </table>
            """
        )

    @classmethod
    def task_log(cls, obj):
        queries = mongo_log_opp_task.find(
            filter_data={
                'metadata.employee_inherit_id': str(obj.id)
            },
        )
        results = [
            {
                "timestamp": str(item["timestamp"]),
                "task_id": item['task_id'],
                "task_status": item['task_status'],
                "not_finish_total": item.get('not_finish_total', '-'),
                "log_level": item.get('log_level', '-'),
                "errors": item.get('errors', '-'),
            } for item in queries
        ]
        html = []
        for item in results:
            html.append(
                f"""
                    <tr>
                        <td>{item['timestamp']}</td>
                        <td>{item['task_id']}</td>
                        <td>{item['task_status']}</td>
                        <td>{item['not_finish_total']}</td>
                        <td>{item['log_level']}</td>
                        <td>{item['errors']}</td>
                    </tr>
                """
            )

        return mark_safe(
            f"""
                <table style="width: 100%;">
                    <thead>
                        <tr>
                            <th>Timestamp</th>
                            <th>Task ID</th>
                            <th>Status</th>
                            <th>Finish Total</th>
                            <th>Level</th>
                            <th>Errors</th>
                        </tr>
                    </thead>
                    <tbody>{"".join(html)}</tbody>
                </table>
            """
        )
