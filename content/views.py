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
from user.views import GetSubscriptionFromMessengerID


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

@api_view(['GET','POST'])
@csrf_exempt
def get_content_from_explore_tag_and_user(request):
    body = request.GET
    username = body['username']
    explore_tag = body['explore_tag']
    print(username,explore_tag)
    uri = 'api/contents/'
    payload = {} # {'test': }
    payload['explore_tag': explore_tag]
    print(payload)
    r = requests.get(PROD_ROOT_URL+uri, params=payload)
    print(r.json())
    return JsonResponse({})

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
        print(queryset)
        explore_tag = self.request.query_params.get('explore_tag', None)
        if explore_tag is not None:
            print('have tag')
            queryset = queryset.filter(contenttag__name=explore_tag)
        '''
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
            queryset = queryset.exclude(usercontent__user=user_id, usercontent__on_watchlist=True)
        '''
        return queryset
