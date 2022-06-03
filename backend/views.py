from datetime import time

from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from backend.models import User, Post
from django.core import serializers
import json


class TestView(GenericAPIView):
    authentication_classes = ()

    def get(self, request):
        print('abcd')
        return Response({'status': 'OK'})


class SaveUser(GenericAPIView):
    authentication_classes = ()

    def post(self, request):
        body = json.loads(request.body)
        user_name = body.get("user_name", None)
        discord_user_id = body.get("discord_user_id", None)

        user = User(user_name=user_name, discord_user_id=discord_user_id)
        data_response = serializers.serialize('json', [user, ])
        return HttpResponse(data_response, content_type="text/json-comment-filtered")


class SavePost(GenericAPIView):
    authentication_classes = ()

    def post(self, request):
        body = json.loads(request.body)
        user_id = body.get("user_id", None)
        status = body.get("status", None)
        id_channel = body.get("id_channel", None)
        do_yesterday = body.get("do_yesterday", None)
        do_today = body.get("do_today", None)
        time_post = body.get("time_post", None)

        content = time_post + \
                  "What you did since yesterday?" + \
                  " - " + do_yesterday + \
                  "What will you do today?" + \
                  " - " + do_today

        post = Post(user_id=user_id, status=status, id_channel=id_channel, do_yesterday=do_yesterday, do_today=do_today,
                    content=content, time_post=time_post)
        post.save()
        print(post)
        data_response = serializers.serialize('json', [post, ])
        return HttpResponse(data_response, content_type="text/json-comment-filtered")


class UserView(GenericAPIView):
    authentication_classes = ()

    def get(self, request):
        body = json.loads(request.body)
        params = request.GET
        print(body)

    def put(self, request):
        body = json.loads(request.body)
