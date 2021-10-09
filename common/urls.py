from django.urls import path
from django.contrib.auth import view as auth_views

from . import views

urlpatterns = [path("login/", auth_views.LoginView.as_view(), name="login")]