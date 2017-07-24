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
from .models import Service, ServiceContent
from .serializers import ServiceSerializer
from django.contrib.auth.models import User, Group
from chatfuel.utilities import TranslateTopicButtonToTag

# Create your views here.

### ViewSets ###
class ServiceViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
