from django.contrib import admin
from .models import Profile, UserSubscription, UserContent

# Register your models here.
admin.site.register(UserContent)
admin.site.register(Profile)
admin.site.register(UserSubscription)
