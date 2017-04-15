"""
Contains handlers for the content side of the webserver (website).
"""
from django.shortcuts import render

def index(request):
    return render(request,"home/index.html")
    