from django.shortcuts import render

# Create your views here.

from rest_framework import viewsets, status, generics
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .models import Profile, Service, Content, UserSubscription
from .serializers import UserSerializer, GroupSerializer, ProfileSerializer, ServiceSerializer, ContentSerializer, UserSubscriptionSerializer
from django.contrib.auth.models import User, Group


@csrf_exempt
def TestView(request):
    return JsonResponse({})

@csrf_exempt
def Webviews(request):
    data = request.GET.get('type')
    print(data)
    json_response = {
        "messages": [
            {"text": "awesome, thanks!"}
            ]
    }
    return JsonResponse(json_response)

@api_view(['POST'])
@csrf_exempt
#@permission_classes((AllowAny,))
def CreateUser(request):
    data = request.POST
    first_name = data.get('first name')
    last_name = data.get('last name')
    username = data.get('chatfuel user id')
    messenger_user_id = data.get('messenger user id')
    password = 'admin'
    user_json = {
        'first_name': first_name,
        'last_name': last_name,
        'username': 'testuser2',
        'password': password
    }
    print(user_json)
    serialized = UserSerializer(data=user_json)
    if serialized.is_valid():
        print('valid')
        serialized.save()
        return Response(serialized.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serialized._errors, status=status.HTTP_400_BAD_REQUEST)

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

class UserSubscriptionViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = UserSubscription.objects.all()
    serializer_class = UserSubscriptionSerializer

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
