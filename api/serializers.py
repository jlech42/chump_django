from rest_framework import serializers
from django.contrib.auth.models import User, Group
from .models import Profile, Service, Content


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('pk','url', 'username', 'email', 'groups')


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')

class ProfileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Profile
        fields = ('pk','url', 'name', 'status', 'user')

class ServiceSerializer(serializers.HyperlinkedModelSerializer):
    users = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all())
    class Meta:
        model = Service
        fields = ('pk','url', 'name', 'users')

class ContentSerializer(serializers.HyperlinkedModelSerializer):
    services = serializers.PrimaryKeyRelatedField(many=True, queryset=Service.objects.all())
    class Meta:
        model = Content
        fields = ('pk','url', 'name', 'services')

'''
from .models import Book, Program, ProgramData, ProgramScenario, Company, CompanyData

class BookSerializer(serializers.ModelSerializer):

	class Meta:
		model = Book
		fields = ('title', 'author')

class ProgramDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgramData
        fields = ('program', 'year')
'''
