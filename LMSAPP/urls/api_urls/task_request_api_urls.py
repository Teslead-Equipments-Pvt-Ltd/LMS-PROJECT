
from django.urls import path
from LMSAPP.views.api_views.task_request_api_views import (
    request_task_inprogress_api,
    action_task_request_api
)


urlpatterns=[
       path('api/tasks/request-inprogress/', request_task_inprogress_api, name='request_task_inprogress_api'),
       path('api/tasks/request-action/', action_task_request_api, name='action_task_request_api'),
]
