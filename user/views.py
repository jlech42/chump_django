from django.shortcuts import render, redirect

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
from chatfuel.utilities import TranslateTopicButtonToTag, get_count_of_gallery_elements


PROD_ROOT_URL = 'http://desolate-basin-19172.herokuapp.com'
DEV_ROOT_URL = 'http://a9f4d2d9.ngrok.io'

ROOT_URL = DEV_ROOT_URL
if 'ROOT_URL' in os.environ:
    ROOT_URL = os.environ['ROOT_URL']

FB_ACCESS = 'EAADZAPRSvqasBALH2s3tcNiXVXp8ZC1iHZBvlHjQSesLoOc19PNcBfy7hFVk8wBIPnxDeJkIWxF5d2unK3xBPCKAmZBPGobG89oGg3jNyAxZAR7eAGsFszJh1X3nN5MXIIylDecPUpZAeqgTuWuEjH6b1vXUjvAr61LmKvekicyQZDZD'
VERIFY_TOKEN = 'test_token'
FB_ID_RAW = 'https://graph.facebook.com/v2.6/1241145236012339/?fields=first_name,last_name,profile_pic,locale,timezone,gender&access_token=EAADZAPRSvqasBAHQ7TiSRlEsBMT55CHOyfrLYAoDZAnEM74ZC2ct3WTIhFv0L2hm8keNhUnYMUOOtS0aZARHFiSyh8gVAOh1xE0TXM6dLrxk21bqBl0kZBJyqvf7dDNSFZBHDasLTqhZCry871iMqHznpLr7rrWQOmpQj7c1njc8gZDZD'
USER_ID = '1241145236012339'
FB_URL_ROOT = "https://graph.facebook.com/v2.6/" + USER_ID
FB_PAGE_ACCESS_TOKEN = 'EAADZAPRSvqasBALH2s3tcNiXVXp8ZC1iHZBvlHjQSesLoOc19PNcBfy7hFVk8wBIPnxDeJkIWxF5d2unK3xBPCKAmZBPGobG89oGg3jNyAxZAR7eAGsFszJh1X3nN5MXIIylDecPUpZAeqgTuWuEjH6b1vXUjvAr61LmKvekicyQZDZD'
FB_URL_PARAMS = "?fields=first_name,last_name,profile_pic,locale,timezone,gender&access_token="+FB_PAGE_ACCESS_TOKEN
FB_USER_API = FB_URL_ROOT+FB_URL_PARAMS


@csrf_exempt
@api_view(['GET','POST'])
def facebook_webhooks(request):
    print('fb webhook')
    body = request.GET
    post_body = request.POST
    print(body)
    print('post body', post_body)
    if (body.get('hub.mode') == 'subscribe') & (body.get('hub.verify_token') =='test_token'):
        print('verified!!')
        challenge_response = body.get('hub.challenge')
        print('challenge response', challenge_response)
        return HttpResponse(challenge_response)
    #res.status(200).send(req.query['hub.challenge']);
    else:
        print('failed')
    #console.error("Failed validation. Make sure the validation tokens match.");
    #res.sendStatus(403);
    return JsonResponse({})

@csrf_exempt
@api_view(['GET','POST'])
def add_to_watchlist_from_messenger_id_and_content_id(request):
    username = request.POST.get('username')
    user_id = getUserFromMessengerID(username)
    content_id = request.GET.get('content_id')
    params = '?user=' + str(user_id) + '&contet=' + str(content_id) + '&on_watchlist=true' + '&action=add_to_watchlist'
    redirect_url = ROOT_URL + '/api/integrations/update-user-content/' + params
    print(redirect_url)
    return redirect(redirect_url)

def create_watchlist_gallery_element_from_content_object(content_object, user):
    title = content_object['title']
    image_link = content_object['image_link']
    logline = content_object['logline']
    trailer_link = content_object['trailer_link']
    long_description = content_object['long_description']
    content_id = str(content_object['id'])
    root = ROOT_URL + "/api/usercontents/manual/update/?"
    params = "content=" + str(content_object['id']) + "&user=" + str(user)
    url = root+params
    element = {
      "title": title,
      "image_url":image_link,
      "subtitle": logline,
      "item_url": trailer_link,
      "buttons":[
        {
          "type":"json_plugin_url",
          "url": ROOT_URL+"/api/integrations/update-user-content/"+"?content="+content_id+"&user="+str(user)+"&on_watchlist=false&watching_now=true&already_seen=true&action=watching_now_from_watchlist",
          "title":"I watched this"
        },
        {
          "type":"json_plugin_url",
          "url": ROOT_URL+"/api/integrations/update-user-content/"+"?content="+content_id+"&user="+str(user)+"&on_watchlist=false&action=remove_from_watchlist",
          "title":"Remove"
        }
      ]
    }
    return element

def DisplayWatchlistGalleryFromContentJson(content_json, user_id):
    elements = []
    # need to make sure gallery can hold unlimited elements
    for content in content_json:
        elements.append(create_watchlist_gallery_element_from_content_object(content, user_id))
    print('elements',elements)

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
            },
            {
                "text": "Search the gallery above or use the below options",
                "quick_replies": [
                    {
                        "title":"Change category",
                        "block_names":["explore_routing"]
                    },
                    {
                        "title":"Share w/ friends",
                        "block_names":["Share"]
                    }
                ]
            }
        ]
    }

    return chatfuel_response

def empty_watchlist_redirect():
    json = {
        "redirect_to_blocks": ["empty_watchlist"]
    }
    return json

@api_view(['GET'])
def ShowWatchlistFromMessengerId(request):
    messenger_user_id = request.GET.get('username')
    user_id = User.objects.get(username=messenger_user_id).id
    payload = {}
    payload['user_id'] = user_id
    payload['on_watchlist'] = True
    payload['query_type'] = 'query_watchlist'
    print('showing watchlist', 'about to call api')
    r = requests.get(ROOT_URL+"/api/contents/", params=payload)
    user_content_objects = UserContent.objects.all().filter(user_id=user_id, on_watchlist=True)
    chatfuel_response = DisplayWatchlistGalleryFromContentJson(r.json(),user_id)
    print('chatfuel_response',chatfuel_response)
    count = get_count_of_gallery_elements(chatfuel_response)
    if count == 0:
        json = empty_watchlist_redirect()
        return JsonResponse(json)
    #print('watchlist', user_content_objects)
    #chatfuel_response = DisplayGalleryFromContentObjects(user_content_objects, user=user)
    return JsonResponse(chatfuel_response)

def getUserFromMessengerID(messenger_id):
    user = User.objects.get(username=messenger_id).id
    return user

def update_watchlist_reroute(request):
    print('rerouting')
    json = {
        "messages": [
            {"text": "We've added to your watchlist"},
            ],

            "redirect_to_blocks": ["explore_content"]


    }
    return JsonResponse(json)


def remove_from_watchlist_message():
    print('called')
    json = {
        "messages": [
            {"text": "Okay, it's off your list"}
            ],
        "redirect_to_blocks": ["watchlist"]
    }
    return json

def add_to_watchlist_message():
    print('called')
    json = {
        "messages": [
            {"text": "Awesome! Added."}
            ],
        "redirect_to_blocks": ["explore_content"]
    }
    return json

def watching_now_from_watchlist_message():
    json = {
            "redirect_to_blocks": ["watching_now_2"]
    }
    return json

def already_seen_message():
    print('already seen registered!')
    json = {
        "messages": [
            {"text": "Great! We won't show you this again."}
            ],
        "redirect_to_blocks": ["explore_content"]
    }
    return json



@api_view(['GET','POST'])
@csrf_exempt
def UpdateUserContent(request):
    """
    API endpoint that takes in content and username and returns a relationship between a piece of content and user
    """
    body = request.GET
    print('body',body)
    payload = {}
    user = body.get('user', None)
    username = body.get('username', None)
    if username:
        print('username in body')
        user = getUserFromMessengerID(username)
    print('user',user)
    content = body.get('content')
    print('content',content)
    action = body.get('action')
    print('action',action)
    payload['content'] = content
    payload['user'] = user
    print('here in method')
    # check if adding to watchlist
    if 'on_watchlist' in body:
        print('in watchlist!')
        payload['on_watchlist'] = body['on_watchlist']
        payload['was_on_watchlist'] = 'true'

    #check if already seen
    if 'already_seen' in body:
        payload['already_seen'] = body['already_seen']

    if 'watching_now' in body:
        payload['watching_now'] = body['watching_now']

    # if user content doesn't exist, create
    if len(UserContent.objects.all().filter(content=content,user=user)) == 0:
        print('user content doesnt exist')
        post_url = ROOT_URL+'/api/user-contents/'
        r = requests.post(ROOT_URL+'/api/user-contents/', data=payload)
        if action == 'remove_from_watchlist':
            print('removing from watchlist')
            chatfuel_response = remove_from_watchlist_message()
            print('here', chatfuel_response)
            return JsonResponse(chatfuel_response)

        if action == 'add_to_watchlist':
            chatfuel_response = add_to_watchlist_message()
            print('here', chatfuel_response)
            return JsonResponse(chatfuel_response)

        if action == 'watching_now_from_watchlist':
            chatfuel_response = watching_now_from_watchlist_message()
            return JsonResponse(chatfuel_response)

        if action == 'add_already_seen':
            print('seen')
            chatfuel_response = already_seen_message()
            return JsonResponse(chatfuel_response)
        if action == 'add_to_watchlist_rec_of_week':
            print('add to watchlist rec of week')
            #chatfuel_response = already_seen_message()
            return JsonResponse({})
        if action == 'add_to_gonna_watch_rec_of_week':
            print('add_to_gonna_watch_rec_of_week')
            return JsonResponse({})
        if action == 'add_to_already_seen_rec_of_week':
            print('add_to_already_seen_rec_of_week')
            return JsonResponse({})
        #json = SimpleMessage(action)


    url_pk = str(UserContent.objects.get(content=content,user=user).pk)
    r = requests.patch(ROOT_URL+'/api/user-contents/' + url_pk +'/', data=payload)
    # create new
    #json = SimpleMessage(action)
    #update_watchlist_reroute
    print('action is', action)
    if action == 'remove_from_watchlist':
        print('removing from watchlist')
        chatfuel_response = remove_from_watchlist_message()
        print('here', chatfuel_response)
        return JsonResponse(chatfuel_response)

    if action == 'add_to_watchlist':
        chatfuel_response = add_to_watchlist_message()
        print('here', chatfuel_response)
        return JsonResponse(chatfuel_response)

    if action == 'watching_now_from_watchlist':
        chatfuel_response = watching_now_from_watchlist_message()
        return JsonResponse(chatfuel_response)

    if action == 'add_already_seen':
        print('seen')
        chatfuel_response = already_seen_message()
        return JsonResponse(chatfuel_response)
    if action == 'add_to_watchlist_rec_of_week':
        print('add to watchlist rec of week')
        #chatfuel_response = already_seen_message()
        return JsonResponse({})
    if action == 'add_to_gonna_watch_rec_of_week':
        print('add_to_gonna_watch_rec_of_week')
        return JsonResponse({})
    if action == 'add_to_already_seen_rec_of_week':
        print('add_to_already_seen_rec_of_week')
        return JsonResponse({})
    return JsonResponse({})

def get_subscriptions_from_user_id(user_id):
    user_id = user_id
    user_subscriptions = UserSubscription.objects.all().filter(user_id=user_id)
    print(user_subscriptions)
    user_subs = []
    for sub in user_subscriptions:
        user_subs.append(Service.objects.get(id=sub.service_id).name)
    filtered_content = {}
    print('in subs', user_subs)
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

# Custom integration layer entry points

@api_view(['POST'])
@csrf_exempt
def IntegrateUserContent(request):
    return JsonResponse({})

@api_view(['POST'])
@csrf_exempt
def IntegrateUserSubscription(request):
    '''
    Function takes in a request with services keyword response and a messenger user id
    Updates user subscriptions based on the input
    '''
    data = request.POST
    print('user response', data)
    have_netflix = data.get('have_netflix')
    have_hbo = data.get('have_hbo')
    have_hulu = data.get('have_hulu')
    have_amazon = data.get('have_amazon')
    services = data.get('services')
    messenger_user_id = data.get('messenger user id')
    print(messenger_user_id)
    user = getUserFromMessengerID(messenger_user_id)
    user_id = user

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
