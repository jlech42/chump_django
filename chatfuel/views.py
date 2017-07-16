from django.shortcuts import render
from django.shortcuts import render

# Create your views here.
import os
from django.http import JsonResponse
from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
import requests
import json
from django.contrib.auth.models import User, Group
# Create your views here.

def GalleryFactory():
    elements = []
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
                            "title":"Show an other rec",
                            "block_names":["Block1", "Block2"]
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
    return chatfuel_response

def QuickReplyFactory():
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
                        "type": "show_block",
                        "block_name": "test",
                        "title":"Change topics"

                    },
                    {
                        "title":"See watchlist",
                        "block_names":["Block1", "Block2"]
                    }
                ]
            }
        ]
    }
    return JsonResponse json
