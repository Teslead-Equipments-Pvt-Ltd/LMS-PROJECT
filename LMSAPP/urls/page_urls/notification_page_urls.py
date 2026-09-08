from django.urls import path 
from LMSAPP.views.page_views.notification_page_views import notification_page

urlpatterns = [
    path('notification/',notification_page,name='notification_page'),
]
