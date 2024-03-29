from . import views
from django.conf.urls import url, include
from rest_framework import routers
from rest_framework_bulk.routes import BulkRouter

router = routers.DefaultRouter()
router.register(r'contents', views.ContentViewSet, 'content')
router.register(r'tags', views.TagViewSet, 'tag')

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^explore-content-selection-from-tag', views.get_content_from_explore_tag_and_user)
]
