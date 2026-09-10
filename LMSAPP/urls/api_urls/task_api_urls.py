from django.urls import path
from LMSAPP.views.api_views.task_page_api_views import (
    get_tasks_api,
    add_task_api,
    update_task_api,
    delete_task_api,
    bulk_delete_tasks_api,
    request_task_inprogress_api,
    action_task_request_api
)

urlpatterns = [
    path('api/tasks/', get_tasks_api, name='get_tasks_api'),
    path('api/tasks/add/', add_task_api, name='add_task_api'),
    path('api/tasks/update/', update_task_api, name='update_task_api'),
    path('api/tasks/delete/', delete_task_api, name='delete_task_api'),
    path('api/tasks/bulk-delete/', bulk_delete_tasks_api, name='bulk_delete_tasks_api'),
    path('api/tasks/request-inprogress/', request_task_inprogress_api, name='request_task_inprogress_api'),
    path('api/tasks/request-action/', action_task_request_api, name='action_task_request_api'),
]
