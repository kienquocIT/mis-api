from django.urls import path

from apps.core.chat3rd.views import (
    MessengerWebHooks,
    MessengerLimit, MessengerConnect, MessengerAccountSync, MessengerPersonView,
    MessengerPersonChats, MessengerPersonDetailLead, MessengerPersonDetailContact,

    ZaloWebHooks,
)

urlpatterns = [
    path('messenger/webhooks', MessengerWebHooks.as_view(), name='MessengerWebHooks'),
    path('messenger/limit', MessengerLimit.as_view(), name='MessengerLimit'),
    path('messenger/connect', MessengerConnect.as_view(), name='MessengerConnect'),
    path('messenger/parent/<str:pk>/accounts-sync', MessengerAccountSync.as_view(), name='MessengerAccountSync'),
    path('messenger/persons/page/<str:page_id>', MessengerPersonView.as_view(), name='MessengerPersonView'),
    path('messenger/chat/<str:page_id>/<str:person_id>', MessengerPersonChats.as_view(), name='MessengerPersonChats'),
    path(
        'messenger/person/<str:pk>/contact', MessengerPersonDetailContact.as_view(), name='MessengerPersonDetailContact'
    ),
    path('messenger/person/<str:pk>/lead', MessengerPersonDetailLead.as_view(), name='MessengerPersonDetailLead'),
]
urlpatterns += [
    path('zalo/webhooks', ZaloWebHooks.as_view(), name='ZaloWebHooks'),
]
