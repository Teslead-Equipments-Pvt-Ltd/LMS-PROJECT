from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView


# PAGE URLS
page_patterns = [
    path('admin/', admin.site.urls),
    path('', include('LMSAPP.urls.page_urls.login_page_urls')),
    path('', include('LMSAPP.urls.page_urls.project_page_urls')),
    path('', include('LMSAPP.urls.page_urls.task_page_urls')),
    path('',include('LMSAPP.urls.page_urls.employee_page_urls')),
]

# API URLS
api_patterns = [
    path('', include('LMSAPP.urls.api_urls.login_api_urls')),
    path('', include('LMSAPP.urls.api_urls.project_api_urls')),
    path('', include('LMSAPP.urls.api_urls.task_api_urls')),
]

urlpatterns = page_patterns + api_patterns