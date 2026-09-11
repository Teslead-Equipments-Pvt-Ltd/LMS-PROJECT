from django.shortcuts import render, redirect
from LMSAPP.services.login_service import logout_service

def loginpage(request):
    return render(request, "loginpage.html")

def base_page(request):
    return render(request, "dashboard.html")

def logout_view(request):
    logout_service(request)  # Completely clears/flushes session data
    return redirect('loginpage')