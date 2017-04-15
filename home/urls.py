"""
Contains routes for the content side of the webserver (website).
"""
from django.conf.urls import url
from . import views
urlpatterns = [
    url('^$',views.index)
]