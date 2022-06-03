from rest_framework import serializers
from backend.models import User, Post


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        user = UserSerializer(instance.user).data

        representation['user'] = user
        return representation
