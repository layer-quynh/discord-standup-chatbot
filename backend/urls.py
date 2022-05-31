from django.urls import path

from backend import views


urlpatterns = [
    path('test', views.TestView.as_view()),
]