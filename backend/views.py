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


# Lay thoi gian tra ve dung dinh dang
class GetToday(GenericAPIView):
    authentication_classes = ()

    def get(self, request):
        date_today = datetime.date.today()
        print(date_today)
        return Response({'today': str(date_today)})


class GetYesterdayPost(GenericAPIView):
    authentication_classes = ()

    def get(self, request, user_id):
        do_yesterday = Post.objects.filter(
            date_create__gt=str(datetime.date.today() - datetime.timedelta(days=1)) + 'T00:00:00.000000Z',
            date_create__lt=str(datetime.date.today() - datetime.timedelta(days=1)) + 'T23:59:59.000000Z',
            user_id=user_id).exclude(status='for_tomorrow').order_by('-date_create').first()
        post_serializer = PostSerializer(instance=do_yesterday)
        res = post_serializer.data

        return Response(res['do_today'])


class GetTodayPost(GenericAPIView):
    authentication_classes = ()

    def get(self, request, user_id):
        # do_today = Post.objects.filter(
        #     date_create__gt=str(datetime.date.today() - datetime.timedelta(days=1)) + 'T00:00:00.000000Z',
        #     date_create__lt=str(datetime.date.today() - datetime.timedelta(days=1)) + 'T23:59:59.000000Z',
        #     user_id=user_id, status='for_tomorrow').order_by('-date_create').first()
        # do_today = Post.objects.filter(
        #     date_create__gt=str(datetime.datetime.now() - datetime.timedelta(minutes=1)),
        #     date_create__lt=str(datetime.datetime.now()),
        #     user_id=user_id, status='for_tomorrow').order_by('-date_create').first()
        do_today = Post.objects.filter(user_id=user_id, status='for_tomorrow').order_by('-date_create').first()
        if do_today is None:
            return Response({'id': None})
        post_serializer = PostSerializer(instance=do_today)
        res = post_serializer.data

        return Response(res)


class GetTomorrowPost(GenericAPIView):
    authentication_classes = ()

    def get(self, request, user_id):
        # post_tomorrow = Post.objects.filter(
        #     date_create__gt=str(datetime.date.today() - datetime.timedelta(days=1)) + 'T00:00:00.000000Z',
        #     date_create__lt=str(datetime.date.today() - datetime.timedelta(days=1)) + 'T23:59:59.000000Z',
        #     user_id=user_id, status='for_tomorrow').order_by('-date_create').first()
        post_tomorrow = Post.objects.filter(
            date_create__gt=str(datetime.date.today()) + 'T00:00:00.000000Z',
            date_create__lt=str(datetime.date.today()) + 'T23:59:59.000000Z',
            user_id=user_id, status='for_tomorrow').order_by('-date_create').first()
        print(post_tomorrow)
        if post_tomorrow is None:
            return Response({'id': None})
        post_serializer = PostSerializer(instance=post_tomorrow)
        res = post_serializer.data

        return Response(res)


class GetReportedPost(GenericAPIView):
    authentication_classes = ()

    def get(self, request, user_id):
        post_tomorrow = Post.objects.filter(
            date_create__gt=str(datetime.date.today()) + 'T00:00:00.000000Z',
            date_create__lt=str(datetime.date.today()) + 'T23:59:59.000000Z',
            user_id=user_id).exclude(status='for_tomorrow').order_by('-date_create').first()
        print(post_tomorrow)
        # do_today = Post.objects.filter(id=1).first()
        if post_tomorrow is None:
            return Response({'id': None})
        post_serializer = PostSerializer(instance=post_tomorrow)
        res = post_serializer.data

        return Response(res)


class PostView(GenericAPIView):
    authentication_classes = ()

    def put(self, request, post_id):
        body = json.loads(request.body)
        post = Post.objects.filter(id=post_id).first()

        try:
            print(body)
            post_serializer = PostSerializer(instance=post, data=body, partial=True)
            post_serializer.is_valid(raise_exception=True)
            post_serializer.save()
        except Exception as ex:
            print(ex)

        return Response(post_serializer.data)


class EditPost(GenericAPIView):
    authentication_classes = ()

    def get(self, request, message_id):
        html = '''
            <h1>Edit Post</h1>
            <form action="update" method="post">
              <input type="hidden" name="" id="inputMessageID" value="{}" />
              <p>What did you do yesterday?</p>
              <textarea id="inputYesterday" rows="6" cols="70"></textarea>
              <!-- <input type="text" name="yesterday_name" id="input_yesterday" /> -->
        
              <p>What will you do today?</p>
        
              <!-- <input type="text" name="today_name" id="input_today" /> -->
              <textarea id="inputToday" rows="6" cols="70"></textarea>
              <br />
              <br />
              <input
                type="submit"
                value="Confirm Edit"
                style="width: 200px; height: 50px"
              />
            </form>
        '''.format(message_id)
        return HttpResponse(html)


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

    def get(self, request):
        param = request.GET
        discord_user_id = param.get("discord_user_id", None)

        user = User.objects.filter(discord_user_id=discord_user_id).first()
        # print(user)
        if user is None:
            return Response({'id': None})

        # convert to json using UserSerializer
        res = UserSerializer(instance=user).data
        return Response(res)


class SavePost(GenericAPIView):
    authentication_classes = ()

    def post(self, request):
        body = json.loads(request.body)
        print(body)
        user_id = body.get("user_id", None)
        status = body.get("status", None)
        id_channel = body.get("id_channel", None)
        do_yesterday = body.get("do_yesterday", None)
        do_today = body.get("do_today", None)
        content = body.get("content", None)
        message_id = body.get("message_id", '982949153174847558')

        post = Post(user_id=user_id, status=status, id_channel=id_channel, do_yesterday=do_yesterday, do_today=do_today,
                    content=content, time_post=datetime.datetime.now(), message_id=message_id)
        post.save()
        post_serializer = PostSerializer(instance=post)
        res = post_serializer.data
        return Response(res)


class GetPost(GenericAPIView):
    authentication_classes = ()

    def get(self, request):
        param = request.GET
        post_id = param.get("id", None)

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
