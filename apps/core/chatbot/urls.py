from django.urls import path

from apps.core.chatbot.views import ChatbotView

urlpatterns = [
    path('chat', ChatbotView.as_view(), name='ChatbotView'),
]
