from django.contrib import admin
from .models import Content, Tag, ContentTag

# Register your models here.
admin.site.register(Content)
admin.site.register(Tag)
admin.site.register(ContentTag)
