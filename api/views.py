from django.shortcuts import render

# Create your views here.

from rest_framework import generics
from rest_framework import viewsets
from .models import Profile, Service, Content
from .serializers import UserSerializer, GroupSerializer, ProfileSerializer, ServiceSerializer, ContentSerializer
from django.contrib.auth.models import User, Group


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer

class ProfileViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows profiles to be viewed or edited.
    """
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

class ServiceViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

class ContentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Content.objects.all()
    serializer_class = ContentSerializer

'''
from rest_framework import generics

from .models import Book, ProgramData
from .serializers import BookSerializer, ProgramDataSerializer

class BookList(generics.ListCreateAPIView):
	"""
	API endpoint for listing and creating Book objects
	"""
	queryset = Book.objects.all()
	serializer_class = BookSerializer

class ProgramDataList(generics.ListCreateAPIView):
	serializer_class = ProgramDataSerializer

	def get_queryset(self):
		"""This view should return a list of all the programdata for
		the program as determined by the program_id portion of the URL.
		"""
		program_id = self.kwargs['program_id']
		print (program_id)
		return ProgramData.objects.filter(program=program_id)

'''
