from rest_framework import serializers
from django.contrib.auth.models import User, Group
from .models import Content, Tag, ContentTag

class ContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Content
        fields = '__all__'

class TagSerializer(serializers.HyperlinkedModelSerializer):
    #services = serializers.PrimaryKeyRelatedField(many=True, queryset=Service.objects.all())
    class Meta:
        model = Tag
        fields = ('pk','url', 'name')
