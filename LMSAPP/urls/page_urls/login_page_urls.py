from django.urls import path
from LMSAPP.views.page_views.loginpage_views import loginpage, base_page

urlpatterns = [
    path('login/', loginpage, name='loginpage'),
    path('base/', base_page, name='base_page'),
    path('', loginpage, name='home'),
]
