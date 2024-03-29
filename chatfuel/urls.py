from . import views
from django.conf.urls import url, include
from rest_framework import routers
from rest_framework_bulk.routes import BulkRouter

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url(r'^text-response', views.ContentLearnMoreMessageResponse),
    url(r'^explore-options', views.ShowExploreOptions),
    url(r'^watchlist-text', views.watchlist_text),
    url(r'^webview-services', views.webview_services),
]
