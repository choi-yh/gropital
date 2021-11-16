import requests
from json.decoder import JSONDecodeError

from django.shortcuts import redirect
from django.conf import settings
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _

from rest_framework import status

from dj_rest_auth.registration.views import SocialLoginView

from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.kakao.views import KakaoOAuth2Adapter
from allauth.socialaccount.providers.naver.views import NaverOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client

from .models import CustomUser


BASE_URL = "http://localhost:8000/"

GOOGLE_CLIENT_ID = getattr(settings, "GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = getattr(settings, "GOOGLE_CLIENT_SECRET")
GOOGLE_CALLBACK_URI = BASE_URL + "accounts/google/callback/"

KAKAO_REST_API_KEY = getattr(settings, "KAKAO_REST_API_KEY")
KAKAO_CALLBACK_URI = BASE_URL + "accounts/kakao/callback/"

NAVER_CLIENT_ID = getattr(settings, "NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = getattr(settings, "NAVER_CLIENT_SECRET")
NAVER_CALLBACK_URI = BASE_URL + "accounts/naver/callback/"

state = getattr(settings, "STATE")


def google_login(request):
    """
    Code Request
    구글 로그인 실행
    """
    scope = "https://www.googleapis.com/auth/userinfo.email"
    return redirect(
        f"https://accounts.google.com/o/oauth2/v2/auth?client_id={GOOGLE_CLIENT_ID}&response_type=code&redirect_uri={GOOGLE_CALLBACK_URI}&scope={scope}"
    )


def google_callback(request):
    code = request.GET.get("code")

    # Access Token Request
    token_request = requests.post(
        f"https://oauth2.googleapis.com/token?client_id={GOOGLE_CLIENT_ID}&client_secret={GOOGLE_CLIENT_SECRET}&code={code}&grant_type=authorization_code&redirect_uri={GOOGLE_CALLBACK_URI}&state={state}"
    )
    token_request_json = token_request.json()
    error = token_request_json.get("error")
    if error:
        raise JSONDecodeError(error)
    access_token = token_request_json.get("access_token")

    # Email Request
    email_request = requests.get(
        f"https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={access_token}"
    )
    email_request_status = email_request.status_code
    if email_request_status != 200:
        return JsonResponse(
            {"error_message": "failed to get email"}, status=status.HTTP_400_BAD_REQUEST
        )
    email_request_json = email_request.json()
    email = email_request_json.get("email")

    # Signup or Signin Request
    try:
        user = CustomUser.objects.get(email=email)
        # 기존에 가입된 유저의 Provider가 google이 아니면 에러 발생, 맞으면 로그인
        social_user = SocialAccount.objects.get(user=user)
        if not social_user:
            return JsonResponse(
                {"error_message": "email exists but not social user"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if social_user.provider != "google":
            return JsonResponse(
                {"error_message": "no matching social type"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # google 유저
        data = {"access_token": access_token, "code": code}
        accept = requests.post(
            f"{BASE_URL}accounts/google/login/finish/", data=data)
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
            f"{BASE_URL}accounts/google/login/finish/", data=data)
        accept_status = accept.status_code
        if accept_status != 200:
            return JsonResponse(
                {"error_message": "failed to signup"}, status=accept_status
            )
        accept_json = accept.json()
        accept_json.pop("user", None)
        return JsonResponse(accept_json)


class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    client_class = OAuth2Client
    callback_url = GOOGLE_CALLBACK_URI


def kakao_login(request):
    """
    카카오 로그인을 통해 인가 코드 받기
    이후 코드는 redirect_uri로 전달됨
    """
    return redirect(
        f"https://kauth.kakao.com/oauth/authorize?client_id={KAKAO_REST_API_KEY}&redirect_uri={KAKAO_CALLBACK_URI}&response_type=code"
    )


def kakao_callback(request):
    code = request.GET.get("code")  # 토큰 받기 요청에 필요한 인가 코드

    # Access Token Request
    token_request = requests.post(
        f"https://kauth.kakao.com/oauth/token?grant_type=authorization_code&client_id={KAKAO_REST_API_KEY}&redirect_uri={KAKAO_CALLBACK_URI}&code={code}"
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
    adapter_class = KakaoOAuth2Adapter
    client_class = OAuth2Client
    callback_url = KAKAO_CALLBACK_URI


def naver_login(request):
    return redirect(
        f"https://nid.naver.com/oauth2.0/authorize?response_type=code&client_id={NAVER_CLIENT_ID}&redirect_uri={NAVER_CALLBACK_URI}&state={state}"
    )


def naver_callback(request):
    code = request.GET.get("code")

    # 토큰 발급
    token_request = requests.post(
        f"https://nid.naver.com/oauth2.0/token?grant_type=authorization_code&client_id={NAVER_CLIENT_ID}&client_secret={NAVER_CLIENT_SECRET}&code={code}&state={state}"
    )
    token_request_json = token_request.json()
    error = token_request_json.get("error")
    if error:
        raise JSONDecodeError(error)
    access_token = token_request_json.get("access_token")

    # email 요청
    email_request = requests.get(
        f"https://openapi.naver.com/v1/nid/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    email_request_json = email_request.json()
    email = email_request_json.get("response/email")

    # Signup or Signin Request
    try:
        user = CustomUser.objects.get(email=email)
        social_user = SocialAccount.objects.get(user=user)
        if not social_user:
            return JsonResponse(
                {"error_message": "email exists but not social user"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if social_user.provider != "naver":
            return JsonResponse(
                {"error_message": "no matching social type"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # naver 유저
        data = {"access_token": access_token, "code": code}
        accept = requests.post(
            f"{BASE_URL}accounts/naver/login/finish/", data=data)
        accept_status = accept.status_code
        if accept_status != 200:
            return JsonResponse(
                {"error_message": "failed to signin"}, status=accept_status
            )
        accept_json = accept.json()
        accept_json.pop("user", None)
        return JsonResponse(accept_json)
    except CustomUser.DoesNotExist:
        data = {"access_token": access_token, "code": code}
        accept = requests.post(
            f"{BASE_URL}accounts/naver/login/finish/", data=data)
        accept_status = accept.status_code
        if accept_status != 200:
            return JsonResponse(
                {"error_message": "failed to signup"}, status=accept_status
            )
        accept_json = accept.json()
        accept_json.pop("user", None)
        return JsonResponse(accept_json)


class NaverLogin(SocialLoginView):
    adapter_class = NaverOAuth2Adapter
    client_class = OAuth2Client
    callback_url = NAVER_CALLBACK_URI
