import datetime
from datetime import time

from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from backend.models import User, Post
from django.core import serializers
import json
from backend.serializers import UserSerializer, PostSerializer


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
        user.save()
        res = UserSerializer(instance=user).data
        return Response(res)


class GetUser(GenericAPIView):
    authentication_classes = ()

    def get(self, request, user_id):
        user = User.objects.filter(id=user_id).first()
        print(user)

        res = UserSerializer(instance=user).data
        return Response(res)


class SavePost(GenericAPIView):
    authentication_classes = ()

    def post(self, request):
        body = json.loads(request.body)
        user_id = body.get("user_id", None)
        status = body.get("status", None)
        id_channel = body.get("id_channel", None)
        do_yesterday = body.get("do_yesterday", None)
        do_today = body.get("do_today", None)
        content = body.get("content", None)

        post = Post(user_id=user_id, status=status, id_channel=id_channel, do_yesterday=do_yesterday, do_today=do_today,
                    content=content, time_post=datetime.datetime.now())
        post.save()
        post_serializer = PostSerializer(instance=post)
        res = post_serializer.data
        return Response(res)


class GetDoYesterday(GenericAPIView):
    authentication_classes = ()

    def get(self, request):
        do_yesterday = Post.objects.filter(datetime='2022-06-04T04:15:08.026265Z').first()
        print(do_yesterday)

        return Response({'status': 'OK'})


class GetPost(GenericAPIView):
    authentication_classes = ()

    def get(self, request, post_id):

        post = Post.objects.filter(id=post_id).first()

        post_serializer = PostSerializer(instance=post)
        res = post_serializer.data
        return Response(res)


class UserView(GenericAPIView):
    authentication_classes = ()

    def get(self, request):
        body = json.loads(request.body)
        params = request.GET
        print(body)

    def put(self, request):
        body = json.loads(request.body)
