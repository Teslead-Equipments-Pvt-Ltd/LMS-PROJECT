from django.urls import path
from LMSAPP.views.api_views.notification_api_views import get_notifications_api

urlpatterns = [
    path('api/notifications/', get_notifications_api, name='get_notifications_api'),
]
