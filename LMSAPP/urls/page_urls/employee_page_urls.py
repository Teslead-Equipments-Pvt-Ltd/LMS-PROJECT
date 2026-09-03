from django.urls import path
from LMSAPP.views.page_views.employee_page_views import employee_page

urlpatterns = [
    path("employee/", employee_page, name='employee_page'),
]
