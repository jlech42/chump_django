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
from service.models import Service
from content.models import Content, Tag, Content, ContentTag
from service.serializers import ServiceSerializer
from content.serializers import ContentSerializer
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

def getUserFromMessengerID(messenger_id):
    user = User.objects.get(username=messenger_id)
    return user

def SimpleMessage(type, *args,**kwargs):
    json = {}
    if type == 'update_already_seen':

        json = {
            "messages": [
                    {"text": "Great, we won't show you this rec again"}
                ],
            "redirect_to_blocks": ["Recommendations"]
        }
    if type == 'update_watchlist':
        json = {
            "messages": [
                {"text": "We've added to your watchlist"},
                ],
            "redirect_to_blocks": ["Recommendations"]
        }
    if type == 'seen_on_watchlist':
        json = {
            "messages": [
                {"text": "We hope you enjoyed it!"},
                {"text":  "What would you like to do now?",
                    "quick_replies": [
                        {
                            "title":"Change topics",
                            "block_names": ["Topics"]

                        },
                        {
                            "title":"See watchlist",
                            "block_names":["Watchlist"]
                        }
                    ]
                }
            ]
        }



    if type == 'remove_from_watchlist':
        json = {
            "messages": [
                {"text": "We've removed this doc from your list"},
                {"text":  "What would you like to do now?",
                    "quick_replies": [
                        {
                            "title":"Change topics",
                            "block_names": ["Topics"]

                        },
                        {
                            "title":"See watchlist",
                            "block_names":["Watchlist"]
                        }
                    ]
                }
            ]
        }
    return json

def get_gallery_element_for_content(cont_obj, user_id, **kwargs):
    messenger_user_id = kwargs['messenger_user_id']
    last_clicked_button = kwargs['last_clicked_button']
    content_id = cont_obj['id']
    title = cont_obj['title']
    image_link = cont_obj['image_link']
    trailer_link = cont_obj['trailer_link']
    logline = cont_obj['logline']
    root = ROOT_URL + "/api/usercontents/manual/update/?"
    params = "content=" + str(content_id) + "&user=" + str(user_id) + "&messenger_user_id="+messenger_user_id+"&last_clicked_button="+last_clicked_button
    url = root+params
    element = [{
      "title": title,
      "image_url":image_link,
      "subtitle": logline,
      "item_url": trailer_link,
      "buttons":[
        {
          "type":"json_plugin_url",
          "url": url + "&on_watchlist=true&action=update_watchlist",
          "title":"Add to watchlist"
        },
        {
          "type":"json_plugin_url",
          "url": url + "&already_seen=true&action=update_already_seen",
          "title":"Already seen"
        },
        {
            "type": "show_block",
            "title":"I'll watch now!",
            "block_names":["watching_now"]
        }
      ]
    }]
    return element

def get_elements(parsed_response, user_id):
    i = 0
    elements = []
    print('get elements', i, parsed_response)
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
          "item_url": trailer_link,
          "buttons":[
            {
              "type":"json_plugin_url",
              "url": url + "&on_watchlist=true&action=update_watchlist",
              "title":"Add to watchlist"
            },
            {
              "type":"json_plugin_url",
              "url": url + "&already_seen=true&action=update_already_seen",
              "title":"Already seen"
            },
            {
                "type": "show_block",
                "title":"I'll watch now!",
                "block_names":["watching_now"]
            }
          ]
        }
        if i <6:
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
      "item_url": trailer_link,
      "buttons":[
        {
          "type":"json_plugin_url",
          "url": url + "&already_seen=true&on_watchlist=false&action=seen_on_watchlist" + "&user=" + str(user),
          "title":"I've watched this!"
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

@api_view(['GET'])
def ShowWatchlistFromMessengerId(request):
    messenger_user_id = request.GET.get('messenger user id')
    user = User.objects.get(username=messenger_user_id).id
    user_content_objects = UserContent.objects.all().filter(user=user, on_watchlist=True)
    chatfuel_response = DisplayGalleryFromContentObjects(user_content_objects, user=user)
    return JsonResponse(chatfuel_response)

@api_view(['GET'])
def ShowWatchlist(request):
    user = request.GET.get('user')
    user_content_objects = UserContent.objects.all().filter(user=user, on_watchlist=True)
    chatfuel_response = DisplayGalleryFromContentObjects(user_content_objects, user=user)
    return JsonResponse(chatfuel_response)

@api_view(['GET'])
def GetContentBlocksFromTags(request):
    '''
    View takes a messenger user id, last clicked button name, topic_tag, content_start_index
    '''
    payload = {}
    req_body = ''
    topic_button_name = request.GET.get('last clicked button name')
    messenger_user_id = request.GET.get('messenger user id')
    topic_tag = request.GET.get('topic_tag')
    start_index = int(request.GET.get('content_start_index'))
    content_tag = TranslateTopicButtonToTag(topic_button_name)
    #content_tag = request.GET.get('content_tag')
    #payload['content_tag'] = content_tag
    print('start index',start_index)
    if topic_tag == "None":
        topic_tag = content_tag
    user_id = User.objects.get(username=messenger_user_id).id
    filtered_services = GetSubscriptionFromMessengerID(messenger_user_id)

    payload['content_tag'] = topic_tag
    payload['user_id'] = user_id
    payload = {**payload, **filtered_services}

    if request.method == 'GET':
        r = requests.get(ROOT_URL+'/api/content/', params=payload)
        req_body = r.text

    parsed_response = json.loads(req_body)
    topic_content_list_length = len(parsed_response)
    end_index = start_index + 3
    if end_index > topic_content_list_length:
        end_index = topic_content_list_length
        next_index = topic_content_list_length
    next_index = end_index
    root = ROOT_URL + "/api/custom-views/show-watchlist?user=" + str(user_id)
    if start_index >= topic_content_list_length:
        chatfuel_response = {
            "messages": [
                {"text": "That's all in this category. You can scroll up, or wait until we add more recs soon!"},
                {
                    "text":  "What would you like to do now?",
                        "quick_replies": [
                            {
                                "title":"Change topics",
                                "block_names": ["Topics"]

                            },
                            {
                                "title":"See watchlist",
                                "block_names": ["Watchlist"]
                            },

          ]
        }
            ]
        }
        return JsonResponse(chatfuel_response)

    #next_index = current_index+1

    next_url = ROOT_URL+'/api/custom-views/content-blocks/?messenger+user+id=' + str(messenger_user_id) + '&last+clicked+button+name=' + topic_button_name
    print('initial response', parsed_response)
    elements = get_elements(parsed_response[start_index:end_index],user_id)
    print(elements)
    #elements = get_gallery_element_for_content(parsed_response, user_id, messenger_user_id=str(messenger_user_id), last_clicked_button=topic_button_name)
    chatfuel_response = {
        "set_attributes":
        {
          "topic_tag": topic_tag,
          "content_start_index": next_index
        },
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
                "text":  "A few other options",
                    "quick_replies": [
                        {
                          "title":"Other recs",
                          "block_names": ["Recommendations"]
                        },
                        {
                            "title":"Change topics",
                            "block_names": ["Topics"]

                        },
                        {
                            "title":"See watchlist",
                            "block_names": ["Watchlist"]
                        },

      ]
    }
        ]
    }

    return JsonResponse(chatfuel_response)
