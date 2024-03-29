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
from .models import Content, Tag
from .serializers import ContentSerializer, TagSerializer
from django.contrib.auth.models import User, Group
from chatfuel.utilities import TranslateTopicButtonToTag
#from user.views import GetSubscriptionFromMessengerID
from user.utilities import get_user_id_from_messenger_id
from chatfuel.views import DisplayGalleryFromContentJson
from chatfuel.utilities import get_count_of_gallery_elements
from user.views import get_subscriptions_from_user_id
from service.models import ServiceContent, Service

PROD_ROOT_URL = 'http://desolate-basin-19172.herokuapp.com/'
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

# Create your views here.

def out_of_recs_redirect():
    json = {
        "redirect_to_blocks": ["out_of_recs"]
    }

    return json

def update_user_log_with_explore_tag(user_id, explore_tag):
    #update user log with explore tag selected
    user_log_action = 'explore_tag_selected'
    post_url = ROOT_URL + '/api/user-logs/'
    post_data = {}
    post_data['user'] = user_id
    post_data['explore_tag'] = explore_tag
    post_data['action'] = user_log_action
    print('about to post')
    r = requests.post(post_url, data=post_data)
    return

@csrf_exempt
@api_view(['GET','POST'])
def get_content_from_explore_tag_and_user(request):
    print('getting content')
    body = request.GET
    username = body['username']
    explore_tag = body['explore_tag']
    uri = '/api/contents/'
    payload = {} # {'test': }
    payload['explore_tag'] = explore_tag
    user_id = get_user_id_from_messenger_id(username)
    payload['user_id'] = user_id
    subscriptions = get_subscriptions_from_user_id(user_id)
    #get content from tag
    r = requests.get(ROOT_URL+uri, params=payload)
    request_json_response = r.json()
    json_count = len(request_json_response)
    print('json_count', json_count)
    if json_count == 0:
        out_of_recs = out_of_recs_redirect()
        return JsonResponse(out_of_recs)

    request_json_response = request_json_response[::-1]
    request_json_response = request_json_response[0:9]
    #display gallery of content
    chatfuel_response = DisplayGalleryFromContentJson(request_json_response , user_id)
    # get count of elements in chatfuel gallery response
    count = get_count_of_gallery_elements(chatfuel_response)
    print('explore tag', explore_tag)
    update_user_log_with_explore_tag(user_id, explore_tag)
    return JsonResponse(chatfuel_response)

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

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
        explore_tag = self.request.query_params.get('explore_tag', None)
        query_type = self.request.query_params.get('query_type', None)
        user_id = self.request.query_params.get('user_id', None)
        if explore_tag is not None:
            tag_id = Tag.objects.get(name=explore_tag).id
            queryset = queryset.filter(contenttag__tag_id=tag_id)
            print('queryset count', len(queryset))
        if query_type is not None:
            if query_type == 'query_watchlist':
                # takes a user id and returns a watchlist
                queryset = queryset.filter(usercontent__user_id=user_id, usercontent__on_watchlist=True)
                return queryset

        user_id = self.request.query_params.get('user_id', None)
        if user_id is not None:
            queryset = queryset.exclude(usercontent__user=user_id, usercontent__already_seen=True)
            queryset = queryset.exclude(usercontent__user=user_id, usercontent__on_watchlist=True)
            #filter out by user subscriptions
            user_subs = get_subscriptions_from_user_id(user_id)
            print('user subscriptions',user_subs)
            if ('on_netflix' in user_subs) == True:
                service_id = Service.objects.get(name='Netflix').id
                queryset = queryset.exclude(servicecontent__service=service_id)
            if ('on_amazon' in user_subs) == True:
                service_id = Service.objects.get(name='Amazon').id
                queryset = queryset.exclude(servicecontent__service=service_id)
            if ('on_hulu' in user_subs) == True:
                service_id = Service.objects.get(name='Hulu').id
                queryset = queryset.exclude(servicecontent__service=service_id)
            if ('on_hbo' in user_subs) == True:
                service_id = Service.objects.get(name='HBO').id
                queryset = queryset.exclude(servicecontent__service=service_id)
        return queryset
