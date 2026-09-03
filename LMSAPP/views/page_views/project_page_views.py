from django.shortcuts import render
from LMSAPP.services.project_service import get_all_projects_service

def project_page(request):
    
    projects = get_all_projects_service()
    return render(request, "project.html", {"projects": projects})
