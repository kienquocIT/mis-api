from django.urls import path

from apps.core.forms.views import (
    FormList, FormDetail, FormDetailTurnOnOff, FormPublishedDetail,
    FormSanitizeHTML, FormPublishedDetailForm, FormDetailForEntries,
    RuntimeFormPublishedDetail,
    FormEntriesList, FormEntriesRefNameList, RuntimeFormHasSubmitted, FormEntrySubmitted, FormDetailTheme,
    FormDetailDuplicate,
)

urlpatterns = [
    # config
    path('list', FormList.as_view(), name='FormList'),
    path('detail/<str:pk>', FormDetail.as_view(), name='FormDetail'),
    path('detail/<str:pk>/theme', FormDetailTheme.as_view(), name='FormDetailTheme'),
    path('detail/<str:pk>/turn-on-off', FormDetailTurnOnOff.as_view(), name='FormDetailTurnOnOff'),
    path('detail/<str:pk>/duplicate', FormDetailDuplicate.as_view(), name='FormDetailDuplicate'),
    path('detail/<str:pk>/for-entries', FormDetailForEntries.as_view(), name='FormDetailForEntries'),
    path('published/form/<str:pk_form>', FormPublishedDetailForm.as_view(), name='FormPublishedDetailForm'),
    path('published/<str:pk>', FormPublishedDetail.as_view(), name='FormPublishedDetail'),

    # util
    path('sanitize-html', FormSanitizeHTML.as_view(), name='FormSanitizeHTML'),

    # runtime
    path(
        'runtime/submit/<str:tenant_code>/<str:form_code>/<str:use_at>', RuntimeFormPublishedDetail.as_view(),
        name='RuntimeFormPublishedDetail'
    ),
    path(
        'runtime/submit/<str:tenant_code>/<str:form_code>/<str:use_at>/<str:pk_submitted>',
        FormEntrySubmitted.as_view(), name='FormEntrySubmitted'
    ),
    path(
        'runtime/submitted/data/<str:tenant_code>/<str:form_code>', RuntimeFormHasSubmitted.as_view(),
        name='RuntimeFormHasSubmitted'
    ),

    # entries
    path('entries/<str:pk>/list', FormEntriesList.as_view(), name='FormEntriesList'),
    path('entries/<str:pk>/ref-name/list', FormEntriesRefNameList.as_view(), name='FormEntriesRefNameList'),
]
