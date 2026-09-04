from django.urls import path
from LMSAPP.views.page_views.dashboard_page_views import dashboard_page

urlpatterns = [
    path('dashboard/', dashboard_page, name='dashboard_page'),
]
