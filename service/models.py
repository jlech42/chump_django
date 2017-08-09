from django.db import models
from django.contrib.auth.models import User
from content.models import Content
#from user.models import UserSubscription

# Create your models here.
class Service(models.Model):
    name = models.CharField(max_length=128, unique=True)
    #users  = models.ManyToManyField(User, through='UserSubscription')
    #content = models.ManyToManyField(Content, through='ServiceContent')
    def __str__(self):
        return self.name

class ServiceContent(models.Model):
    content = models.ForeignKey(Content, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    class Meta:
        unique_together = ('content', 'service',)
    def __str__(self):
        return self.content.title + ' ' + self.service.name
