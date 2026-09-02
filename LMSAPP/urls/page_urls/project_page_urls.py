from django.urls import path
from LMSAPP.views.page_views.project_page_views import project_page

urlpatterns = [
    path('project/', project_page, name='project_page'),
]
