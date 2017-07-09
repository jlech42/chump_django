from django.contrib import admin

from .models import Profile, Service, Content, ServiceContent, UserSubscription

# Register your models here.
admin.site.register(Profile)
admin.site.register(Service)
admin.site.register(Content)
admin.site.register(UserSubscription)
admin.site.register(ServiceContent)
