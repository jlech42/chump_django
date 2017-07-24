from rest_framework import serializers
from django.contrib.auth.models import User, Group
from .models import Service, ServiceContent

class ServiceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Service
        fields = ('pk','url', 'name', 'content')
