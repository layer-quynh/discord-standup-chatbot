from django.urls import path

from backend import views


urlpatterns = [
    path('test', views.TestView.as_view()),
    path('users/<int:user_id>', views.GetUser.as_view()),
    path('posts/<int:post_id>', views.GetPost.as_view()),

    path('user', views.SaveUser.as_view()),
    path('post', views.SavePost.as_view()),

    path('get-do-yesterday', views.GetDoYesterday.as_view()),


]