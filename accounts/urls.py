from django.urls import path

from .views import google_views, kakao_views

urlpatterns = [
    path("google/login/", google_views.google_login, name="google_login"),
    path("google/callback/", google_views.google_callback, name="google_callback"),
    path(
        "google/login/finish/",
        google_views.GoogleLogin.as_view(),
        name="google_login_to_django",
    ),

    path("kakao/login/", kakao_views.kakao_login, name="kakao_login"),
    path("kakao/callback/", kakao_views.kakao_callback, name="kakao_callback"),
    path(
        "kakao/login/finish/",
        kakao_views.KakaoLogin.as_view(),
        name="kakao_login_to_django"
    )
]
