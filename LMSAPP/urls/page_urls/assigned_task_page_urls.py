from django.urls import path
from LMSAPP.views.page_views.assigned_task_page_views import assigned_task_page
urlpatterns = [
    path('assigned_task/',assigned_task_page,name='assigned_task_page'),
]
