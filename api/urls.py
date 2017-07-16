from . import views
from django.conf.urls import url, include
from rest_framework import routers
from rest_framework_bulk.routes import BulkRouter

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)
router.register(r'profiles', views.ProfileViewSet)
router.register(r'services', views.ServiceViewSet)
router.register(r'content', views.ContentViewSet, 'content')
router.register(r'usersubscriptions', views.UserSubscriptionViewSet)
router.register(r'usercontents', views.UserContentViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^createuser', views.CreateUser),
    url(r'^usersubscriptions/manual/create', views.CreateUserSubscription),
    url(r'^custom-views/content-blocks', views.GetContentBlocksFromTags),
    url(r'^usercontents/manual/update', views.UpdateUserContent),
    url(r'^custom-views/show-watchlist', views.ShowWatchlist),
    #url(r'^getcontentblocks', views.GetContentBlocks),
    url(r'^webviews/$', views.Webviews),
    url(r'^test/$', views.Test),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
