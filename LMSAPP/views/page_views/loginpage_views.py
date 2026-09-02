from django.shortcuts import render

def loginpage(request):
    return render(request, "loginpage.html")

def base_page(request):
    return render(request, "base.html")