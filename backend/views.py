from django.shortcuts import render


# Create your views here.
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from backend.models import User
import json


class TestView(GenericAPIView):
    authentication_classes = ()

    def get(self, request):
        print('abcd')
        return Response({'status': 'OK'})


class UserView(GenericAPIView):
    authentication_classes = ()

    def get(self, request):
        body = json.loads(request.body)
        params = request.GET
        print(body)

    def put(self, request):
        body = json.loads(request.body)
