from django.urls import path
from LMSAPP.views.api_views.project_page_api_views import (
    get_projects_api,
    add_project_api,
    update_project_api,
    delete_project_api,
    bulk_delete_projects_api,
    get_project_tasks_api
)

urlpatterns = [
    path('api/projects/', get_projects_api, name='get_projects_api'),
    path('api/projects/tasks/', get_project_tasks_api, name='get_project_tasks_api'),
    path('api/projects/add/', add_project_api, name='add_project_api'),
    path('api/projects/update/', update_project_api, name='update_project_api'),
    path('api/projects/delete/', delete_project_api, name='delete_project_api'),
    path('api/projects/bulk-delete/', bulk_delete_projects_api, name='bulk_delete_projects_api'),
]
