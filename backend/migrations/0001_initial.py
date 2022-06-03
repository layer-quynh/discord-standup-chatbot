# Generated by Django 4.0.5 on 2022-06-02 15:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.IntegerField(editable=False, primary_key=True, serialize=False)),
                ('discord_user_id', models.CharField(max_length=18)),
                ('user_name', models.TextField(null=True)),
            ],
            options={
                'db_table': 'users',
            },
        ),
        migrations.CreateModel(
            name='post',
            fields=[
                ('id', models.IntegerField(editable=False, primary_key=True, serialize=False)),
                ('date_create', models.DateTimeField(auto_now_add=True)),
                ('status', models.TextField()),
                ('id_channel', models.CharField(max_length=18)),
                ('do_yesterday', models.TextField()),
                ('do_today', models.TextField()),
                ('content', models.TextField()),
                ('time_post', models.DateTimeField()),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.user')),
            ],
            options={
                'db_table': 'post',
            },
        ),
    ]