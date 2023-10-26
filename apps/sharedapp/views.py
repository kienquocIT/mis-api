from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView

from apps.shared.extends.signals import SaleDefaultData
from apps.shared import ResponseController, TypeCheck
from apps.core.base.models import Application, SubscriptionPlan, PlanApplication


class DefaultDataStorageView(APIView):
    @swagger_auto_schema()
    def get(self, request, *args, **kwargs):
        data = {
            "sale": {
                "Product Type": SaleDefaultData.ProductType_data,
                "Tax Category": SaleDefaultData.TaxCategory_data,
                "Currency": SaleDefaultData.Currency_data,
            }
        }
        return ResponseController.success_200(
            data=data,
            key_data='result',
        )


class PlanApplicationConfigData(APIView):
    @swagger_auto_schema()
    def get(self, request, *args, **kwargs):
        filter_kw = {}

        plan_id = request.query_params.dict().get('plan_id', None)
        if plan_id and TypeCheck.check_uuid(plan_id):
            filter_kw['plan_id'] = plan_id

        plan_app = {}
        for obj in PlanApplication.objects.select_related('plan', 'application').filter(**filter_kw):
            plan_id = str(obj.plan_id)
            if plan_id not in plan_app:
                plan_app[plan_id] = {
                    'id': plan_id,
                    'title': obj.plan.title,
                    'code': obj.plan.code,
                    'application': [],
                }
            plan_app[plan_id]['application'].append(
                {
                    'id': obj.application_id,
                    'title': obj.application.title,
                    'code': obj.application.code,
                    'app_label': obj.application.app_label,
                    'model_code': obj.application.model_code,
                    'is_workflow': obj.application.is_workflow,
                    'permit_mapping': obj.application.permit_mapping,
                    'depend_follow_main': obj.application.depend_follow_main,
                    'filtering_inheritor': obj.application.filtering_inheritor,
                }
            )

        app_by_id = {
            str(obj.id): {
                "id": str(obj.id),
                "title": str(obj.title),
                "code": str(obj.code),
            }
            for obj in Application.objects.filter()
        }

        return ResponseController.success_200(
            data={
                'plan_app': [value for _key, value in plan_app.items()],
                'app_by_id': app_by_id,
            }, key_data='result'
        )
