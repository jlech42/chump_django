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
from user.utilities import get_user_id_from_messenger_id


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
from django.views.decorators.clickjacking import xframe_options_exempt



@api_view(['GET','POST'])
def webview_services(request):
    body = request.GET
    username = body.get('username')
    print('webview services')
    user_id = get_user_id_from_messenger_id(username)
    print('username',user_id)
    #print(username)

    json = {
      "messages": [
        {
          "attachment": {
            "type": "template",
            "payload": {
              "template_type": "button",
              "text": "see the watchlist",
              "buttons":[
                  {
                      "type":"json_plugin_url",
                      "url": "www.google.com",
                      "title":"Test"
                  },
                  {
                      "type":"web_url",
                      "url":"http://6ba1c310.ngrok.io/webviews/services/?user_id="+str(user_id),
                      "title":"See watchlist"
                  }
                  ]
            }
          }
        }]}

    return JsonResponse(json)

@api_view(['GET','POST'])
def watchlist_text(request):
    body = request.GET
    username = body.get('username')
    print(username)
    user_id = get_user_id_from_messenger_id(username)
    print('username',user_id)
    #print(username)

    json = {
      "messages": [
        {
          "attachment": {
            "type": "template",
            "payload": {
              "template_type": "button",
              "text": "see the watchlist",
              "buttons":[
                  {
                      "type":"json_plugin_url",
                      "url": "www.google.com",
                      "title":"Test"
                  },
                  {
                      "type":"web_url",
                      "url":"http://6ba1c310.ngrok.io/webviews/watchlist/?user_id="+str(user_id),
                      "title":"See watchlist"
                  }
                  ]
            }
          }
        }]}

    return JsonResponse(json)



@api_view(['GET','POST'])
def services_webview(request):
    user_id = request.GET.get('user_id')
    print('services webview body', user_id)
    return render(request, 'service_selection.html', {'user_id': user_id})

@api_view(['GET','POST'])
def watchlist_webview(request):

    user_id = request.GET.get('user_id')
    print('webview body', user_id)
    return render(request, 'base.html', {'user_id': user_id})

@api_view(['GET','POST'])
def ContentLearnMoreMessageResponse(request):
    # request has a content id and response with a text of the content description
    body = request.GET
    content_id = int(body['content_id'])
    user = body['username']
    print('request body!!',body)
    description = Content.objects.get(id=content_id).long_description
    json = {
      "messages": [
        {
          "attachment": {
            "type": "template",
            "payload": {
              "template_type": "button",
              "text": description,
              "buttons":[
                  {
                      "type":"json_plugin_url",
                      "url": ROOT_URL+"/api/integrations/update-user-content/"+"?content="+str(content_id)+"&user="+str(user)+"&on_watchlist=true&action=add_to_watchlist",
                      "title":"Add to watchlist"
                  },
                  {
                      "type":"json_plugin_url",
                      "url": ROOT_URL+"/api/integrations/update-user-content/"+"?content="+str(content_id)+"&user="+str(user)+"&on_watchlist=false&watching_now=true&already_seen=true&action=watching_now_from_watchlist",
                      "title":"I watched this"
                  }
                  ]
            }
          }
        },
        {
            "text":  "You can also use the below options",
                "quick_replies": [
                    {
                        "title":"Keep exploring",
                        "block_names":["explore_content"]
                    },
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
    '''
    json = {
        "messages": [
            {"text": description,
            "buttons":[
                {
                    "type":"json_plugin_url",
                    "url": ROOT_URL+"/api/integrations/update-user-content/"+"?content="+content_id+"&user="+str(user)+"&on_watchlist=true&action=add_to_watchlist",
                    "title":"Add to watchlist"
                },
                {
                    "type":"json_plugin_url",
                    "url": ROOT_URL+"/api/integrations/update-user-content/"+"?content="+content_id+"&user="+str(user)+"&on_watchlist=false&watching_now=true&already_seen=true&action=watching_now_from_watchlist",
                    "title":"I watched / Im gonna"
                }
                ]
            },
            {"quick_replies": [
                {
                    "title":"Keep exploring",
                    "block_names":["explore_content"]
                },
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
    '''
    return JsonResponse(json)


@api_view(['GET','POST'])
def ShowExploreOptions(request):
    username = request.GET.get('username')
    user_id = get_user_id_from_messenger_id(username)
    print('user',user_id)
    json = {
        "messages": [
            {"text": "What would you like to see?",
                "quick_replies": [
                    {
                        "set_attributes":
                        {
                          "explore_tag": "best-new-shows",
                        },
                        "url":  ROOT_URL + '/api/explore-content-selection-from-tag/?username=' + str(user_id) + '&explore_tag=best-new-shows',
                        "type":"json_plugin_url",
                        "title":"Best new shows"
                    },
                    {
                        "set_attributes":
                        {
                          "explore_tag": "movies-worth-watching",
                        },

                        "url":  ROOT_URL + '/api/explore-content-selection-from-tag/?username=' + str(user_id) + '&explore_tag=movies-worth-watching',
                        "type":"json_plugin_url",
                        "title":"Flix worth watching"
                    },
                    {
                        "set_attributes":
                        {
                          "explore_tag": "leaving",
                        },
                        "url":  ROOT_URL + '/api/explore-content-selection-from-tag/?username=' + str(user_id) + '&explore_tag=leaving',
                        "type":"json_plugin_url",
                        "title":"Leaving soon"

                    },
                    {
                        "title":"Watchlist",
                        "block_names":["watchlist"]
                    }
                    ]
                }
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
          "url": ROOT_URL+'/api/text-response/'+'?content_id='+content_id,
          "title":"Read a description"
        },
        {
          "type":"json_plugin_url",
          "url": ROOT_URL+"/api/integrations/update-user-content/"+"?content="+content_id+"&user="+str(user)+"&on_watchlist=true&action=add_to_watchlist",
          "title":"Add to watchlist"
        },
        {
          "type":"json_plugin_url",
          "url": ROOT_URL+"/api/integrations/update-user-content/"+"?content="+content_id+"&user="+str(user)+"&on_watchlist=false&already_seen=true&action=add_already_seen",
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
                "text": "Check out our recs above or keep exploring with the options below",
                "quick_replies": [
                    {
                        "title":"Keep exploring",
                        "block_names":["explore_routing"]
                    },
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
