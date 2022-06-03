from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
class User(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    discord_user_id = models.CharField(max_length=18)
    user_name = models.TextField(null=True)

    class Meta:
        db_table = 'users'


class Post(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    date_create = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)
    status = models.TextField()
    id_channel = models.CharField(max_length=18)
    do_yesterday = models.TextField()
    do_today = models.TextField()
    content = models.TextField()
    time_post = models.DateTimeField()



    class Meta:
        db_table = 'post'
