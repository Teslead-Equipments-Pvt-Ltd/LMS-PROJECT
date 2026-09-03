from django.urls import path
from LMSAPP.views.page_views.task_page_views import task_page

urlpatterns = [
    path('task/', task_page, name='task_page'),
]
