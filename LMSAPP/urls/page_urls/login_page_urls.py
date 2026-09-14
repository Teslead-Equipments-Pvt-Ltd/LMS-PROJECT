from django.urls import path
from LMSAPP.views.page_views.loginpage_views import loginpage, logout_view

urlpatterns = [
    path('login/', loginpage, name='loginpage'),
    path('logout/', logout_view, name='logout_view'),
    path('', loginpage, name='home'),
]
