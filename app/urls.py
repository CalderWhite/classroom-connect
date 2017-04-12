from django.conf.urls import url, include
from django.contrib import admin
from . import views

urlpatterns = [
    url(r'signup/$',views.handler.signupPage),
    url(r'login/$',views.handler.loginPage),
    url(r'auth/$',views.handler.authenticate)
]
