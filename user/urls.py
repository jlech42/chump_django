from . import views
from django.conf.urls import url, include
from rest_framework import routers
from rest_framework_bulk.routes import BulkRouter

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet, 'user')
router.register(r'groups', views.GroupViewSet)
router.register(r'profiles', views.ProfileViewSet)
router.register(r'user-subscriptions', views.UserSubscriptionViewSet)
router.register(r'user-contents', views.UserContentViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url(r'^', include(router.urls)),
    #url(r'^createuser', views.CreateUser),
    #url(r'^usersubscriptions/manual/create', views.CreateUserSubscription),
    url(r'^integrations/user-subscriptions', views.IntegrateUserSubscription),
    url(r'^integrationrks/user-watchlist', views.ShowWatchlistFromMessengerId),
    url(r'^integrations/update-user-content', views.UpdateUserContent),
    #url(r'^custom-views/content-blocks', views.GetContentBlocksFromTags),
    #url(r'^usercontents/manual/update', views.UpdateUserContent),
    #url(r'^custom-views/show-watchlist', views.ShowWatchlist),
    #url(r'^custom-views/get-watchlist-from-messenger-id', views.ShowWatchlistFromMessengerId),
    #url(r'^getcontentblocks', views.GetContentBlocks),
    #url(r'^test/$', views.Test),
]
