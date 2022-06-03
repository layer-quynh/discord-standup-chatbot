from django.urls import path

from backend import views


urlpatterns = [
    path('test', views.TestView.as_view()),
    path('user', views.SaveUser.as_view()),
    path('post', views.SavePost.as_view()),
]