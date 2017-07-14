from django.shortcuts import render

# Create your views here.

from rest_framework import viewsets, status, generics
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
import requests
import json

from .models import Profile, Service, Content, UserSubscription, Tag, Content, ContentTag
from .serializers import UserSerializer, GroupSerializer, ProfileSerializer, ServiceSerializer, ContentSerializer, UserSubscriptionSerializer
from django.contrib.auth.models import User, Group


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
    print('testing user')
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


def get_elements(parsed_response):
    i = 0
    elements = []
    for cont_obj in parsed_response:
        title = cont_obj['title']
        image_link = cont_obj['image_link']
        trailer_link = cont_obj['trailer_link']
        logline = cont_obj['logline']
        element = {
          "title": title,
          "image_url":image_link,
          "subtitle": logline,
          "buttons":[
            {
              "type":"web_url",
              "url": trailer_link,
              "title":"Trailer"
            },
            {
              "type":"web_url",
              "url": "https://youtu.be/3TfxHdVhz0M",
              "title":"Already seen"
            }
          ]
        }
        if i <5:
            elements.append(element)
            i = i + 1
        else:
            break
    return elements

def GetSubscriptionFromMessengerID(id):
    user_id = User.objects.get(username=id).id
    user_subscriptions = UserSubscription.objects.all().filter(user_id=user_id)
    user_subs = []
    params = []
    for sub in user_subscriptions:
        user_subs.append(Service.objects.get(id=sub.service_id).name)
    filtered_content = {}
    # Need to add case where content is on multiple
    if ("Netflix" in user_subs) == False:
        filtered_content['on_netflix'] = False
    if ("Amazon" in user_subs) == False:
        filtered_content['on_amazon'] = False
    if ("Hulu" in user_subs) == False:
        filtered_content['on_hulu'] = False
    if ("HBO" in user_subs) == False:
        filtered_content['on_hbo'] = False
    return filtered_content

@api_view(['GET'])
def GetContentBlocksFromTags(request):
    req_body = ''
    payload = {}
    content_tag = request.GET.get('content_tag')
    payload['content_tag'] = content_tag
    messenger_user_id = request.GET.get('messenger user id')
    filtered_services = GetSubscriptionFromMessengerID(messenger_user_id)
    payload = {**payload, **filtered_services}
    print('about to send', payload)
    if request.method == 'GET':
        r = requests.get('http://desolate-basin-19172.herokuapp.com/api/content/', params=payload)
        req_body = r.text
        print('body',req_body)
    parsed_response = json.loads(req_body)
    elements = get_elements(parsed_response)
    chatfuel_response = {
        "messages": [
            {
                "attachment":{
                    "type":"template",
                    "payload":{
                        "template_type":"generic",
                        "elements":elements
                    }
                }
            },
            {
                "text":  "Commands below",
                    "quick_replies": [
                        {
                        #"title":"See another",
                        "block_names":["Block1", "Block2"]
                            },
                            {
                            "title":"Go back",
                            "block_names":["Block1", "Block2"]
                                },

      ]
    }
        ]
    }
    print(chatfuel_response)
    return JsonResponse(chatfuel_response)

class ContentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Content to be viewed or edited.
    """
    serializer_class = ContentSerializer
    def get_queryset(self):
        '''
        Optionally restricts the returned content to a given user,
        by filtering against a `username` query parameter in the URL +
        filters by tags.
        '''
        queryset = Content.objects.all()
        print('viewset')

        # filter for tags
        tag = self.request.query_params.get('content_tag', None)
        # filter for user services - needs to be tested
        on_netflix = self.request.query_params.get('on_netflix', None)
        on_hulu = self.request.query_params.get('on_hulu', None)
        on_hbo = self.request.query_params.get('on_hbo', None)
        on_amazon = self.request.query_params.get('on_amazon', None)
        if on_netflix is not None:
            queryset = queryset.filter(on_netflix=False)
        if on_amazon is not None:
            queryset = queryset.filter(on_amazon=False)
        if on_hulu is not None:
            queryset = queryset.filter(on_hulu=False)
        if on_hbo is not None:
            queryset = queryset.filter(on_hbo=False)
        if tag is not None:
            queryset = queryset.filter(topic_one=tag)

        return queryset


class UserSubscriptionViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = UserSubscription.objects.all()
    serializer_class = UserSubscriptionSerializer
