from django.shortcuts import render

# Create your views here.

from rest_framework import viewsets, status, generics
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .models import Profile, Service, Content, UserSubscription, Tag, Content, ContentTag
from .serializers import UserSerializer, GroupSerializer, ProfileSerializer, ServiceSerializer, ContentSerializer, UserSubscriptionSerializer
from django.contrib.auth.models import User, Group


def CreateContentElement(content_obj):
    title = content_obj.name
    image_url = content_obj.image_url
    subtitle = content_obj.description
    trailer = content_obj.trailer
    element = {
            "title": title,
            "image_url": image_url,
            "subtitle": subtitle,
            "buttons":[
                {
                    "type": "web_url",
                    "url": trailer,
                    "title":"Trailer"
                },
                {
                    "type": "web_url",
                    "url": "http://8fc5ec0d.ngrok.io/api/webviews/",
                    "title": "Already seen"
                }
                ]
            }
    return element

def GetContentFromTagAndService(tag, services):
    tag_obj = Tag.objects.get(name=tag)
    tag_id = tag_obj.id

    # all content associated with tag
    content_for_tag = ContentTag.objects.all().filter(tag_id=tag_id)
    elements = []
    # iterate through and display
    for content_tag in content_for_tag:
        content_id = content_tag.content_id
        content_obj = Content.objects.get(id=content_id)
        element = CreateContentElement(content_obj)
        elements.append(element)

    ## need to filter by service
    return elements

@api_view(['GET'])
def GetContent(request):
    print(request)
    chatfuel_tag_id = 'content_tag'
    tag = request.GET.get(chatfuel_tag_id)
    # array of user services
    services = [1,2,3]
    elements = GetContentFromTagAndService(tag, services)
    chatfuel_response = {
        "messages": [
            {
                "attachment":{
                "type":"template",
                "payload":{
                "template_type":"generic",
                "elements": elements
                    }
                }
            }
            ]
        }

    return JsonResponse(chatfuel_response)

@api_view(['POST'])
@csrf_exempt
def CreateUserSubscription(request):
    data = request.POST
    have_netflix = data.get('have_netflix')
    have_hbo = data.get('have_hbo')
    have_hulu = data.get('have_hulu')
    have_amazon = data.get('have_amazon')
    netflix_id = Service.objects.get(name='Netflix').id
    hulu_id = Service.objects.get(name='Hulu').id
    amazon_id = Service.objects.get(name='Amazon').id
    hbo_id = Service.objects.get(name='HBO').id
    messenger_user_id = data.get('messenger user id')
    user = getUserFromMessengerID(messenger_user_id)
    user_subscription_responses = {"Netflix": have_netflix, "HBO": have_hbo, "Amazon": have_amazon, "Hulu": have_hulu}

    # function takes the user id and dictionary of user reponses
    def updateUserSubscriptions(user_id, user_subscription_responses):
        for service, response in user_subscription_responses.items():
            service_id = Service.objects.get(name=service).id

            # if user said they have service
            if response == 'Yes':
                if UserSubscription.objects.all().filter(service_id = service_id, user_id = user_id).count() > 0:
                    print('exist')
                else:
                    UserSubscription.objects.create(service_id = service_id, user_id = user_id)

            # user doesn't have service
            else:
                # delete user service from database
                if  UserSubscription.objects.all().filter(service_id = service_id, user_id = user_id).count() > 0:
                    instance = UserSubscription.objects.get(service_id = service_id, user_id = user_id)
                    instance.delete()
                else:
                    print('doesnt exist')
        return

    updateUserSubscriptions(user.id, user_subscription_responses)
    return JsonResponse({})

def getUserFromMessengerID(messenger_id):
    user = User.objects.get(username=messenger_id)
    return user

@csrf_exempt
def Webviews(request):
    tags = Tag.objects.all()
    return render(request, 'tags.html' ,{'tags': tags})

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
        'username': username,
        'password': password
    }
    serialized = UserSerializer(data=user_json)
    if serialized.is_valid():
        print('valid')
        serialized.save()
        return Response(serialized.data, status=status.HTTP_201_CREATED)
    else:
        active_user = User.objects.get(username=username)
        user_profile = active_user.profile
        user_profile.status = "test"
        user_profile.save()
        #CreateUserProfile(request)
        return Response(serialized._errors, status=status.HTTP_400_BAD_REQUEST)

def CreateUserProfile(request):
    messenger_user_id = data.get('messenger user id')
    #serialized = ProfileSerializer(data=)
    return

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
