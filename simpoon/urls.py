from django.urls import path

from . import views

app_name = "simpoon"

urlpatterns = [path("", views.index), path("login/", views.login)]
