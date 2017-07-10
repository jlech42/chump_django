from rest_framework import serializers
from django.contrib.auth.models import User, Group
from .models import Profile, Service, Content, UserSubscription, Tag, ContentTag, ServiceContent

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

class ServiceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Service
        fields = ('pk','url', 'name', 'users', 'content')

class UserSubscriptionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = UserSubscription
        fields = ('pk','url', 'service', 'user')

class ContentSerializer(serializers.HyperlinkedModelSerializer):
    #services = serializers.PrimaryKeyRelatedField(many=True, queryset=Service.objects.all())
    class Meta:
        model = Content
        fields = ('pk','url', 'name','trailer','description','image_url')

class TagSerializer(serializers.HyperlinkedModelSerializer):
    #services = serializers.PrimaryKeyRelatedField(many=True, queryset=Service.objects.all())
    class Meta:
        model = Tag
        fields = ('pk','url', 'name')
