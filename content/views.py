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
# Create your views here.

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
        return queryset
