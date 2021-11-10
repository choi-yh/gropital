from django.urls import path

from .views import google_views, kakao_views, naver_views

urlpatterns = [
    # Google url
    path("google/login/", google_views.google_login, name="google_login"),
    path("google/callback/", google_views.google_callback, name="google_callback"),
    path(
        "google/login/finish/",
        google_views.GoogleLogin.as_view(),
        name="google_login_to_django",
    ),

    # Kakao url
    path("kakao/login/", kakao_views.kakao_login, name="kakao_login"),
    path("kakao/callback/", kakao_views.kakao_callback, name="kakao_callback"),
    path(
        "kakao/login/finish/",
        kakao_views.KakaoLogin.as_view(),
        name="kakao_login_to_django"
    ),

    # Naver url
    path("naver/login/", naver_views.naver_login, name="naver_login"),
    path("naver/callback/", naver_views.naver_callback, name="naver_callback"),
    path(
        "naver/login/finish/",
        naver_views.NaverLogin.as_view(),
        name="naver_login_to_django",
    )
]
