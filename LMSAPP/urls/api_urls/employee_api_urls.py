from django.urls import path
from LMSAPP.views.api_views.employee_api_views import (
    add_employee_api,
    update_employee_api,
    delete_employee_api
)

urlpatterns = [
    path('api/add_employee/', add_employee_api, name='add_employee_api'),
    path('api/update_employee/', update_employee_api, name='update_employee_api'),
    path('api/delete_employee/', delete_employee_api, name='delete_employee_api'),
]

