from rest_framework import serializers
from django.contrib.auth.models import User, Group
from .models import Profile, UserSubscription, UserContent, UserLog

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('pk', 'username', 'first_name', 'last_name')

class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')

class ProfileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Profile
        fields = ('pk','url', 'status', 'user')

class UserSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSubscription
        fields = ('pk','url', 'service', 'user')

class UserContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserContent
        fields = ('content','user', 'on_watchlist', 'already_seen', 'watching_now', 'was_on_watchlist', 'shared', 'not_interested')

class UserLogSerialzier(serializers.ModelSerializer):
    class Meta:
        model = UserLog
        fields = '__all__'
