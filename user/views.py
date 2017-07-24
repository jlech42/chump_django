from django.shortcuts import render

# Create your views here.
import os
from rest_framework import viewsets, status, generics
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.mixins import UpdateModelMixin
import requests
import json
from rest_framework.decorators import detail_route, list_route
from .models import UserSubscription, Profile, UserContent
from service.models import Service
from .serializers import UserSerializer, GroupSerializer, ProfileSerializer, UserSubscriptionSerializer, UserContentSerializer
from django.contrib.auth.models import User, Group
from chatfuel.utilities import TranslateTopicButtonToTag

PROD_ROOT_URL = 'http://desolate-basin-19172.herokuapp.com'
DEV_ROOT_URL = 'http://a9f4d2d9.ngrok.io'

ROOT_URL = DEV_ROOT_URL
if 'ROOT_URL' in os.environ:
    ROOT_URL = os.environ['ROOT_URL']

FB_ID_RAW = 'https://graph.facebook.com/v2.6/1241145236012339/?fields=first_name,last_name,profile_pic,locale,timezone,gender&access_token=EAADZAPRSvqasBAHQ7TiSRlEsBMT55CHOyfrLYAoDZAnEM74ZC2ct3WTIhFv0L2hm8keNhUnYMUOOtS0aZARHFiSyh8gVAOh1xE0TXM6dLrxk21bqBl0kZBJyqvf7dDNSFZBHDasLTqhZCry871iMqHznpLr7rrWQOmpQj7c1njc8gZDZD'
USER_ID = '1241145236012339'
FB_URL_ROOT = "https://graph.facebook.com/v2.6/" + USER_ID
FB_PAGE_ACCESS_TOKEN = 'EAADZAPRSvqasBAHQ7TiSRlEsBMT55CHOyfrLYAoDZAnEM74ZC2ct3WTIhFv0L2hm8keNhUnYMUOOtS0aZARHFiSyh8gVAOh1xE0TXM6dLrxk21bqBl0kZBJyqvf7dDNSFZBHDasLTqhZCry871iMqHznpLr7rrWQOmpQj7c1njc8gZDZD'
FB_URL_PARAMS = "?fields=first_name,last_name,profile_pic,locale,timezone,gender&access_token="+FB_PAGE_ACCESS_TOKEN
FB_USER_API = FB_URL_ROOT+FB_URL_PARAMS

def getUserFromMessengerID(messenger_id):
    user = User.objects.get(username=messenger_id)
    return user

@api_view(['GET','POST'])
@csrf_exempt
def UpdateUserContent(request, **kwargs):
    """
    API endpoint that takes in content and username and returns a relationship between a piece of content and user
    """
    body = request.GET
    #next_url = ROOT_URL+'/api/custom-views/content-blocks/?messenger+user+id=' + body.get('messenger_user_id') + '&last+clicked+button+name=' + body.get('topic_button_name') + '&index=' + body.get('index')
    payload = {}

    user = body.get('user')
    content = body.get('content')
    action = body.get('action')
    payload['content'] = content
    payload['user'] = user
    # check if adding to watchlist
    if 'on_watchlist' in body:
        payload['on_watchlist'] = body['on_watchlist']
    #check if already seen
    if 'already_seen' in body:
        payload['already_seen'] = body['already_seen']
    if not UserContent.objects.all().filter(content=content,user=user):
        post_url = ROOT_URL+'/api/usercontents/'
        r = requests.post(ROOT_URL+'/api/usercontents/', data=payload)
        json = SimpleMessage(action)
        return JsonResponse(json)
    url_pk = str(UserContent.objects.get(content=content,user=user).pk)
    r = requests.patch(ROOT_URL+'/api/usercontents/' + url_pk +'/', data=payload)
    # create new
    json = SimpleMessage(action)
    return JsonResponse(json)

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


@api_view(['POST'])
@csrf_exempt
def IntegrateUserSubscription(request):
    data = request.POST
    have_netflix = data.get('have_netflix')
    have_hbo = data.get('have_hbo')
    have_hulu = data.get('have_hulu')
    have_amazon = data.get('have_amazon')
    services = data.get('services')
    messenger_user_id = data.get('messenger user id')
    user = getUserFromMessengerID(messenger_user_id)
    user_id = user.id

    # need to update this code!!
    user_subscription_responses = {"Netflix": have_netflix, "HBO": have_hbo, "Amazon": have_amazon, "Hulu": have_hulu}

    # function takes the user id and dictionary of user reponses
    def updateUserSubscriptions(user_id, user_subscription_responses):
        for service, response in user_subscription_responses.items():
            service_id = Service.objects.get(name=service).id

            # if user said they have service
            if response == 'True':
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
    updateUserSubscriptions(user_id, user_subscription_responses)
    return JsonResponse({})

### ViewSets ###

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


#@api_view(['GET','PUT','POST'])
class UserContentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = UserContent.objects.all()
    serializer_class = UserContentSerializer



class UserSubscriptionViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = UserSubscription.objects.all()
    serializer_class = UserSubscriptionSerializer
