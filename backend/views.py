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
            user_id=user_id).order_by('-date_create').first()
        post_serializer = PostSerializer(instance=do_yesterday)
        res = post_serializer.data

        return Response(res['do_today'])


class EditPost(GenericAPIView):
    authentication_classes = ()

    def post(self, request, message_id):
        body = request.body
        body = body.decode('utf-8')

        # body = json.loads(request.body)
        # do_yesterday = body.get("do_yesterday", None)
        # do_today = body.get("do_today", None)

        # message_id = None
        do_yesterday = None
        do_today = None

        key_val = body.split('&')
        for item in key_val:
            item_key_val = item.split('=')
            print(item_key_val)
            # if item_key_val[0] == 'message_id':
            #     message_id = item_key_val[1]

            if item_key_val[0] == 'do_yesterday':
                do_yesterday = item_key_val[1]

            if item_key_val[0] == 'do_today':
                do_today = item_key_val[1]
        html = '''
            <h1>Edit Post</h1>
            <form action="../update" method="post">
              <input type="hidden" name="message_id" id="inputMessageID" value="{}" />
              <p>What did you do yesterday?</p>
              <textarea name="do_yesterday" id="inputYesterday" rows="6" cols="70">{}</textarea>
              <!-- <input type="text" name="yesterday_name" id="input_yesterday" /> -->
        
              <p>What will you do today?</p>
        
              <!-- <input type="text" name="today_name" id="input_today" /> -->
              <textarea name="do_today" id="inputToday" rows="6" cols="70">{}</textarea>
              <br />
              <br />
              <input
                type="submit"
                value="Confirm Edit"
                style="width: 200px; height: 50px"
              />
            </form>
        '''.format(message_id,do_yesterday,do_today)
        return HttpResponse(html)

class EditMessage(GenericAPIView):
    authentication_classes = ()

    def patch(self, request, message_id):
        body = request.body
        body = body.decode('utf-8')
        body = json.loads(request.body)
        message_id = body.get("message_id", None)
        content = body.get("content", None)
        doYesterday = body.get("do_yesterday", None)
        doToday = body.get("do_today", None)
        post = Post.objects.filter(message_id=message_id).first()
        post.content = content
        post.save()
        post_serializer = PostSerializer(instance=post)
        res = post_serializer.data
        return Response(res)

class UpdateMessage(GenericAPIView):
    authentication_classes = ()

    def post(self,request):
        body = request.body
        body = body.decode('utf-8')

        message_id = None
        do_yesterday = None
        do_today = None

        key_val = body.split('&')
        for item in key_val:
            item_key_val = item.split('=')
            print(item_key_val)
            if item_key_val[0] == 'message_id':
                message_id = item_key_val[1]

            if item_key_val[0] == 'do_yesterday':
                do_yesterday = item_key_val[1]

            if item_key_val[0] == 'do_today':
                do_today = item_key_val[1]

        print(message_id)
        print(do_today)
        print(do_yesterday)
        # body = json.loads(body)
        # print(body)
        # body = json.loads(request.body)
        # print(body)
        # abc = request.body
        # body = json.loads(request.body)
        # print(str(abc))
        # print(type(abc))
        # print(type(str(abc)))
        # # body = json.loads(request.body)
        # # message_id = body.get("message_id", None)
        # # print(message_id)
        # html = '''
        #     <p>{}</p>
        #     <p>{}</p>
        #     <p>{}</p>
        # '''.format(message_id,do_today,do_yesterday)
        # return HttpResponse(html)
        try:
            post = Post.objects.filter(message_id=message_id).first()
            # post.content = content
            post.do_today=do_today
            post.do_yesterday = do_yesterday
            post.save()
        except:
            return HttpResponse('Error')

        return HttpResponse('success')
        #
        # post_serializer = PostSerializer(instance=post)
        # res = post_serializer.data
        # return Response(res)

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
        userid = param.get("id", None)

        user = User.objects.filter(id=userid).first()
        print(user)

        # convert to json using UserSerializer
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
