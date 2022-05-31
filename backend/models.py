from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
class User(models.Model):
    id = models.IntegerField(primary_key=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=False, blank=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    email = models.EmailField(unique=True)
    name = models.CharField(null=True, blank=True, max_length=100)
    time_zone = models.CharField(null=False, max_length=100)
    is_superadmin = models.BooleanField(default=False)

    class Meta:
        db_table = 'users'


class Report(models.Model):
    id = models.IntegerField(primary_key=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=False, blank=False)
    work_done = models.TextField(null=True)
    work_will_do = models.TextField(null=True)
    report_content = models.TextField(null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = 'reports'
