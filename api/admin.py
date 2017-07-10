from django.contrib import admin

from .models import Profile, Service, Content, ServiceContent, UserSubscription, ContentTag, Tag

# Register your models here.
admin.site.register(Profile)
admin.site.register(Service)
admin.site.register(Content)
admin.site.register(UserSubscription)
admin.site.register(ServiceContent)
admin.site.register(ContentTag)
admin.site.register(Tag)
