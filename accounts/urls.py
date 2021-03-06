from django.urls import path

from . import views

urlpatterns = [
    # Google url
    path("google/login/", views.google_login, name="google_login"),
    path("google/callback/", views.google_callback, name="google_callback"),
    path(
        "google/login/finish/",
        views.GoogleLogin.as_view(),
        name="google_login_to_django",
    ),

    # Kakao url
    path("kakao/login/", views.kakao_login, name="kakao_login"),
    path("kakao/callback/", views.kakao_callback, name="kakao_callback"),
    path(
        "kakao/login/finish/",
        views.KakaoLogin.as_view(),
        name="kakao_login_to_django"
    ),

    # Naver url
    path("naver/login/", views.naver_login, name="naver_login"),
    path("naver/callback/", views.naver_callback, name="naver_callback"),
    path(
        "naver/login/finish/",
        views.NaverLogin.as_view(),
        name="naver_login_to_django",
    )
]
