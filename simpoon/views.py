from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    return HttpResponse("Simpoon과 함께하는 맞춤형 성공 전략")

