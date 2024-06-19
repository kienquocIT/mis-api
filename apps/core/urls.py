from celery.result import AsyncResult
from django.urls import path, include
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView

from apps.shared import TypeCheck, mask_view, ResponseController


class TaskBackgroundState(APIView):
    @swagger_auto_schema()
    @mask_view(login_require=True)
    def get(self, request, *args, **kwargs):
        _id = kwargs.get('pk', None)
        if _id and TypeCheck.check_uuid(_id):
            state = str(AsyncResult(_id).state)
            return ResponseController.success_200(data={'state': state}, key_data='result')
        return ResponseController.notfound_404()


urlpatterns = [
    path('auth/', include('apps.core.auths.urls')),
    path('account/', include('apps.core.account.urls')),
    path('provisioning/', include('apps.core.provisioning.urls')),
    path('hr/', include('apps.core.hr.urls')),
    path('tenant/', include('apps.core.tenant.urls')),
    path('company/', include('apps.core.company.urls')),
    path('base/', include('apps.core.base.urls')),
    path('workflow/', include('apps.core.workflow.urls')),
    path('task-bg/<str:pk>', TaskBackgroundState.as_view(), name='TaskBackgroundState'),
    path('log/', include('apps.core.log.urls')),
    path('sale-process/', include('apps.core.process.urls')),
    path('site/public/<str:company_sub_domain>/', include('apps.core.web_builder.urls.public')),
    path('site/config/', include('apps.core.web_builder.urls.config')),
    path('attachment/', include('apps.core.attachments.urls')),
    path('comment/', include('apps.core.comment.urls')),
    path('printer/', include('apps.core.printer.urls')),
    path('mailer/', include('apps.core.mailer.urls')),
    path('import-data/', include('apps.core.urls_import')),
    path('form/', include('apps.core.forms.urls')),
]
