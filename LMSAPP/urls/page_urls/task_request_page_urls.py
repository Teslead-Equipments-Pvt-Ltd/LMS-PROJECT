from django.urls import path
from LMSAPP.views.page_views.task_request_page_views import task_request_page

urlpatterns = [
    path('task-request/', task_request_page, name='task_request_page'),
]
