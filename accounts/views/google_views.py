import requests
from json.decoder import JSONDecodeError

from django.shortcuts import redirect
from django.conf import settings
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _

from rest_framework import status

from dj_rest_auth.registration.views import SocialLoginView

from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.providers.google import views as google_view
from allauth.socialaccount.providers.oauth2.client import OAuth2Client

from ..models import CustomUser


BASE_URL = "http://localhost:8000/"
GOOGLE_CALLBACK_URI = BASE_URL + "accounts/google/callback/"

state = getattr(settings, "STATE")


def google_login(request):
    """
    Code Request
    구글 로그인 실행
    """
    scope = "https://www.googleapis.com/auth/userinfo.email"
    client_id = getattr(settings, "KAKAO_REST_API_KEY")
    return redirect(
        f"https://accounts.google.com/o/oauth2/v2/auth?client_id={client_id}&response_type=code&redirect_uri={GOOGLE_CALLBACK_URI}&scope={scope}"
    )


def google_callback(request):
    client_id = getattr(settings, "SOCIAL_AUTH_GOOGLE_CLIENT_ID")
    client_secret = getattr(settings, "SOCIAL_AUTH_GOOGLE_SECRET")
    code = request.GET.get("code")

    # Access Token Request
    token_request = requests.post(
        f"https://oauth2.googleapis.com/token?client_id={client_id}&client_secret={client_secret}&code={code}&grant_type=authorization_code&redirect_uri={GOOGLE_CALLBACK_URI}&state={state}"
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
        accept = requests.post(f"{BASE_URL}accounts/google/login/finish/", data=data)
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
        accept = requests.post(f"{BASE_URL}accounts/google/login/finish/", data=data)
        accept_status = accept.status_code
        if accept_status != 200:
            return JsonResponse(
                {"error_message": "failed to signup"}, status=accept_status
            )
        accept_json = accept.json()
        accept_json.pop("user", None)
        return JsonResponse(accept_json)


class GoogleLogin(SocialLoginView):
    adapter_class = google_view.GoogleOAuth2Adapter
    client_class = OAuth2Client
    callback_url = GOOGLE_CALLBACK_URI
