from django.urls import path
from LMSAPP.views.page_views.loginpage_views import loginpage, base_page, logout_view

urlpatterns = [
    path('login/', loginpage, name='loginpage'),
    path('logout/', logout_view, name='logout_view'),
    path('base/', base_page, name='base_page'),
    path('', loginpage, name='home'),
]
