import requests
from json.decoder import JSONDecodeError

from django.shortcuts import redirect
from django.conf import settings
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _

from rest_framework import status

from dj_rest_auth.registration.views import SocialLoginView

from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.providers.naver import views as naver_view
from allauth.socialaccount.providers.oauth2.client import OAuth2Client

from ..models import CustomUser


BASE_URL = "http://localhost:8000/"
NAVER_CALLBACK_URI = BASE_URL + "accounts/naver/callback/"
NAVER_CLIENT_ID = getattr(settings, "NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = getattr(settings, "NAVER_CLIENT_SECRET")

state = getattr(settings, "STATE")


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
    adapter_class = naver_view.NaverOAuth2Adapter
    client_class = OAuth2Client
    callback_url = NAVER_CALLBACK_URI
