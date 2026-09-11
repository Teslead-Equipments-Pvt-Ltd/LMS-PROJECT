
from django.shortcuts import render


def assigned_task_page(request):
    return render(request,'assigned_task.html')