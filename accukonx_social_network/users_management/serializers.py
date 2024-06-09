from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import FriendRequest, Friend

User = get_user_model()

class UserSignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'username', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

class FriendRequestSerializer(serializers.ModelSerializer):
    from_user_username = serializers.CharField(source='from_user.username', read_only=True)
    to_user_username = serializers.CharField(source='to_user.username', read_only=True)

    class Meta:
        model = FriendRequest
        fields = ['id', 'from_user', 'from_user_username', 'to_user', 'to_user_username', 'timestamp', 'status']
        read_only_fields = ['from_user', 'timestamp', 'status']

class FriendRequestUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = ['status']

class FriendSerializer(serializers.ModelSerializer):
    users = serializers.SerializerMethodField()

    class Meta:
        model = Friend
        fields = ['id', 'users', 'current_user']

    def get_users(self, obj):
        users = obj.users.exclude(id=obj.current_user.id)
        return [{'id': user.id, 'username': user.username} for user in users]

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username']