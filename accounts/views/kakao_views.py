import requests
from json.decoder import JSONDecodeError

from django.shortcuts import redirect
from django.conf import settings
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _

from rest_framework import status

from dj_rest_auth.registration.views import SocialLoginView

from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.providers.kakao import views as kakao_view
from allauth.socialaccount.providers.oauth2.client import OAuth2Client

from ..models import CustomUser


BASE_URL = "http://localhost:8000/"
KAKAO_CALLBACK_URI = BASE_URL + "accounts/kakao/callback/"

state = getattr(settings, "STATE")


def kakao_login(request):
    """
    카카오 로그인을 통해 인가 코드 받기
    이후 코드는 redirect_uri로 전달됨
    """
    rest_api_key = getattr(settings, "KAKAO_REST_API_KEY")
    return redirect(
        f"https://kauth.kakao.com/oauth/authorize?client_id={rest_api_key}&redirect_uri={KAKAO_CALLBACK_URI}&response_type=code"
    )


def kakao_callback(request):
    rest_api_key = getattr(settings, "KAKAO_REST_API_KEY")
    code = request.GET.get("code") # 토큰 받기 요청에 필요한 인가 코드

    # Access Token Request
    token_request = requests.post(
        f"https://kauth.kakao.com/oauth/token?grant_type=authorization_code&client_id={rest_api_key}&redirect_uri={KAKAO_CALLBACK_URI}&code={code}"
    )
    token_request_json = token_request.json()
    error = token_request_json.get("error")
    if error:
        raise JSONDecodeError(error)
    access_token = token_request_json.get("access_token")

    # Email Request
    profile_request = requests.get(
        "https://kapi.kakao.com/v2/user/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    profile_json = profile_request.json()
    error = profile_json.get("error")
    if error:
        raise JSONDecodeError(error)
    kakao_account = profile_json.get("kakao_account")
    email = kakao_account.get("email")

    # Signup or Signin Request
    try:
        user = CustomUser.objects.get(email=email)
        # 기존에 가입된 유저의 Provider가 kakao 아니면 에러 발생, 맞으면 로그인
        social_user = SocialAccount.objects.get(user=user)
        if not social_user:
            return JsonResponse(
                {"error_message": "email exists but not social user"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if social_user.provider != "kakao":
            return JsonResponse(
                {"error_message": "no matching social type"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # kakao 유저
        data = {"access_token": access_token, "code": code}
        accept = requests.post(
            f"{BASE_URL}accounts/kakao/login/finish/", data=data)
        accept_status = accept.status_code
        if accept_status != 200:
            return JsonResponse(
                {"error_message": "failed to signin"}, status=accept_status
            )
        accept_json = accept.json()
        accept_json.pop("user", None)
        return JsonResponse(accept_json)
    except CustomUser.DoesNotExist:
        # 가입된 유저가 아니라면 새로 가입
        data = {"access_token": access_token, "code": code}
        accept = requests.post(
            f"{BASE_URL}accounts/kakao/login/finish/", data=data)
        accept_status = accept.status_code
        if accept_status != 200:
            return JsonResponse(
                {"error_message": "failed to signup"}, status=accept_status
            )
        accept_json = accept.json()
        accept_json.pop("user", None)
        return JsonResponse(accept_json)


class KakaoLogin(SocialLoginView):
    adapter_class = kakao_view.KakaoOAuth2Adapter
    client_class = OAuth2Client
    callback_url = KAKAO_CALLBACK_URI
