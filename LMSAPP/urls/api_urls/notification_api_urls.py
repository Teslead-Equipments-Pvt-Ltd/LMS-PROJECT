from django.urls import path
from LMSAPP.views.api_views.notification_api_views import (
    get_notifications_api,
    check_approval_api
)

urlpatterns = [
    path('api/notifications/', get_notifications_api, name='get_notifications_api'),
    path('api/notifications/check-approval/', check_approval_api, name='check_approval_api'),
]
