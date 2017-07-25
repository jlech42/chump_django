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
from user.utilities import get_user_id_from_messenger_id
from content.models import Content


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

@api_view(['GET','POST'])
def ContentLearnMoreMessageResponse(request):
    # request has a content id and response with a text of the content description
    body = request.GET
    content_id = int(body['content_id'])
    print('message id ', content_id)
    description = Content.objects.get(id=content_id).long_description
    print(description)
    json = {
        "messages": [
            {"text": description},
            {"quick_replies": [
                {
                    "title":"See watchlist",
                    "block_names":["watchlist"]
                },
                {
                    "title":"Share w/ friends",
                    "block_names":["Share"]
                }
            ]}
            ]
    }
    return JsonResponse(json)


@api_view(['GET','POST'])
def ShowExploreOptions(request):
    json = {
        "messages": [
            {"text": "What would you like to see?"},
            {"quick_replies": [
                {
                    "title":"Best new shows",
                    "block_names":["explore_content"],
                    "set_attributes":
                    {
                      "explore_tag": "best-new-shows",
                    }
                },
                {
                    "title":"Flix worth watching",
                    "block_names":["explore_content"],
                    "set_attributes":
                    {
                      "explore_tag": "movies-worth-watching",
                    }
                },
                {
                    "title":"Leaving soon",
                    "block_names":["explore_content"],
                    "set_attributes":
                    {
                      "explore_tag": "leaving",
                    }
                }
            ]}
            ]
    }
    print('response',json)
    return JsonResponse(json)

def CreateGalleryElementFromContentObject(content_object, user):
    title = content_object['title']
    image_link = content_object['image_link']
    logline = content_object['logline']
    trailer_link = content_object['trailer_link']
    long_description = content_object['long_description']
    content_id = content_object['id']
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
          "url": ROOT_URL+'/api/text-response/'+'?content_id='+str(content_id),
          "title":"Learn more"
        },
        {
          "type":"json_plugin_url",
          "url": url + "&already_seen=true&on_watchlist=false&action=seen_on_watchlist" + "&user=" + str(user),
          "title":"Add to watchlist"
        },
        {
          "type":"json_plugin_url",
          "url": url + "&already_seen=true&on_watchlist=false&action=seen_on_watchlist" + "&user=" + str(user),
          "title":"Already seen"
        }
      ]
    }
    return element

def DisplayGalleryFromContentJson(content_json, user_id):
    elements = []
    # need to make sure gallery can hold unlimited elements
    for content in content_json:
        elements.append(CreateGalleryElementFromContentObject(content, user_id))
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
                        "title":"See watchlist",
                        "block_names":["watchlist"]
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



# Create your views here.

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


def QuickReplyFactory():
    quick_reply = {"quick_replies": []}
    return quick_reply

def TopicQuickReply():
    response = {
        "block_names": ["Topics"],
        "title":"Change topics"

    }
    return response

'''
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
'''
