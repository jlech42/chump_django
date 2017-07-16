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

from .models import Profile, Service, Content, UserSubscription, Tag, Content, ContentTag, UserContent
from .serializers import UserSerializer, GroupSerializer, ProfileSerializer, ServiceSerializer, ContentSerializer, UserSubscriptionSerializer, UserContentSerializer
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

def Test(request):
    return JsonResponse({})

def SimpleMessage(type, *args,**kwargs):

    print('kwargs', args)
    json = {}
    if type == 'update_already_seen':
        print('seen')
        json = {
            "messages": [
                {"text": "Great, we won't show you this rec again"},
                {"text":  "What would you like to do now?",
                    "quick_replies": [
                        {
                            "title":"See more recs",
                            "block_names":["Block1", "Block2"]
                        },
                        {
                            "title":"Change topics",
                            "block_names": ["Topics"]

                        },
                        {
                            "title":"See watchlist",
                            "block_names":["Block1", "Block2"]
                        }
                    ]
                }
            ]
        }
    if type == 'update_watchlist':
        json = {
            "messages": [
                {"text": "We've added to your watchlist"},
                {"text":  "What would you like to do now?",
                    "quick_replies": [
                        {
                            "title":"See more recs",
                            "block_names":["Block1", "Block2"]
                        },
                        {
                            "title":"Change topics",
                            "block_names": ["Topics"]

                        },
                        {
                            "title":"See watchlist",
                            "block_names":["Block1", "Block2"]
                        }
                    ]
                }
            ]
        }
    return json

@api_view(['GET','POST'])
@csrf_exempt
def UpdateUserContent(request):
    """
    API endpoint that takes in content and username and returns a relationship between a piece of content and user
    """
    payload = {}
    body = request.GET
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

def get_gallery_element_for_content(cont_obj, user_id):
    content_id = cont_obj['id']
    title = cont_obj['title']
    image_link = cont_obj['image_link']
    trailer_link = cont_obj['trailer_link']
    logline = cont_obj['logline']
    root = ROOT_URL + "/api/usercontents/manual/update/?"
    params = "content=" + str(content_id) + "&user=" + str(user_id)
    url = root+params
    element = [{
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
          "type":"json_plugin_url",
          "url": url + "&on_watchlist=true&action=update_watchlist",
          "title":"Add to watchlist"
        },
        {
          "type":"json_plugin_url",
          "url": url + "&already_seen=true&action=update_already_seen",
          "title":"Already seen"
        }
      ]
    }]
    return element

def get_elements(parsed_response, user_id):
    i = 0
    elements = []
    for cont_obj in parsed_response:
        content_id = cont_obj['id']
        title = cont_obj['title']
        image_link = cont_obj['image_link']
        trailer_link = cont_obj['trailer_link']
        logline = cont_obj['logline']
        root = ROOT_URL + "/api/usercontents/manual/update/?"
        params = "content=" + str(content_id) + "&user=" + str(user_id)
        url = root+params
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
              "type":"json_plugin_url",
              "url": url + "&on_watchlist=true&action=update_watchlist",
              "title":"Add to watchlist"
            },
            {
              "type":"json_plugin_url",
              "url": url + "&already_seen=true&action=update_already_seen",
              "title":"Already seen"
            }
          ]
        }
        if i <1:
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

def CreateGalleryElementFromContentObject(content_object, user):
    title = content_object.title
    image_link = content_object.image_link
    logline = content_object.logline
    trailer_link = content_object.trailer_link
    root = ROOT_URL + "/api/usercontents/manual/update/?"
    params = "content=" + str(content_object.id) + "&user=" + str(user)
    url = root+params
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
          "type":"json_plugin_url",
          "url": url + "&already_seen=true&action=update_already_seen" + "&user=" + str(user),
          "title":"Already seen"
        }
      ]
    }
    return element

def DisplayGalleryFromContentObjects(content_objects, user):

    elements = []
    # need to make sure gallery can hold unlimited elements
    for obj in content_objects:
        elements.append(CreateGalleryElementFromContentObject(obj.content, user))

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

    return chatfuel_response

def ShowWatchlist(request):
    user = request.GET.get('user')
    user_content_objects = UserContent.objects.all().filter(user=user, on_watchlist=True)
    chatfuel_response = DisplayGalleryFromContentObjects(user_content_objects, user=user)
    return JsonResponse(chatfuel_response)

@api_view(['GET'])
def GetContentBlocksFromTags(request):
    payload = {}
    topic_button_name = request.GET.get('last clicked button name')
    current_index = 0
    print('button name',topic_button_name)
    #content_tag = request.GET.get('content_tag')
    #payload['content_tag'] = content_tag
    content_tag = TranslateTopicButtonToTag(topic_button_name)
    print(content_tag)
    payload['content_tag'] = content_tag
    req_body = ''
    messenger_user_id = request.GET.get('messenger user id')
    user_id = User.objects.get(username=messenger_user_id).id
    print(user_id)
    payload['user_id'] = user_id
    filtered_services = GetSubscriptionFromMessengerID(messenger_user_id)
    payload = {**payload, **filtered_services}
    print(payload)
    if request.method == 'GET':
        r = requests.get(ROOT_URL+'/api/content/', params=payload)
        req_body = r.text
    parsed_response = json.loads(req_body)
    print(parsed_response)
    next_id = 1
    elements = get_gallery_element_for_content(parsed_response[current_index], user_id)
    root = ROOT_URL + "/api/custom-views/show-watchlist?user=" + str(user_id)
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
                "text":  "More commands below",
                    "quick_replies": [
                        {
                          "type":"json_plugin_url",
                          "url": root,
                          "title":"Show another rec"
                        },
                        {
                            "title":"Change topics",
                            "block_names": ["Topics"]

                        },
                        {
                            "title":"See watchlist",
                            "url": root,
                            "type":"json_plugin_url"
                        },

      ]
    }
        ]
    }

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
        # filter for tags
        tag = self.request.query_params.get('content_tag', None)
        user_id = self.request.query_params.get('user_id', None)
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
            queryset = queryset.filter(primary_mode=tag)

        #filter out content people have already seen
        #should we filter out on watchlist content?
        if user_id is not None:
            queryset = queryset.exclude(usercontent__user=user_id, usercontent__already_seen=True)
        return queryset

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
        serialized.save()
        return Response(serialized.data, status=status.HTTP_201_CREATED)
    else:
        active_user = User.objects.get(username=username)
        user_profile = active_user.profile
        user_profile.status = "test"
        user_profile.save()
        return Response(serialized._errors, status=status.HTTP_400_BAD_REQUEST)


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

class ServiceViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

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
