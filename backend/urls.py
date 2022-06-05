from django.urls import path

from backend import views


urlpatterns = [
    path('test', views.TestView.as_view()),
    path('user-id', views.GetUser.as_view()),
    path('post-id', views.GetPost.as_view()),

    path('user', views.SaveUser.as_view()),
    path('post', views.SavePost.as_view()),

    path('today', views.GetToday.as_view()),
    path('get-will-do-yesterday/<int:user_id>', views.GetYesterdayPost.as_view()),
    path('get-yesterday-post/<int:user_id>', views.GetTodayPost.as_view()),
    path('get-tomorrow-post/<int:user_id>', views.GetTomorrowPost.as_view()),

    path('posts/<int:post_id>', views.PostView.as_view()),

    path('edit-post/<str:message_id>',views.EditPost.as_view()),

    path('message', views.EditMessage.as_view()),

    path('update', views.UpdateMessage.as_view() ),
]