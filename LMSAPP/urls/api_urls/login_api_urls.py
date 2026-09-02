from django.urls import path
from LMSAPP.views.api_views.loginpage_api_views import( 
    
    login_api

)
urlpatterns = [
    path('api/login/', login_api, name='login_api'),
]
