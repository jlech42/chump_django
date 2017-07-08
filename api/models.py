from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=100)
    chatfuel_user_id = models.BigIntegerField # from chatfuel
    messenger_user_id = models.BigIntegerField # from chatfuel
    def __str__(self):
        return self.user

# signals to hook up user to profile
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class Service(models.Model):
    name = models.CharField(max_length=128)
    users = models.ManyToManyField(User)
    def __str__(self):
        return self.name

class Content(models.Model):
    name = models.CharField(max_length=128)
    content_type = models.CharField(max_length=128)
    services = models.ManyToManyField(Service)
    def __str__(self):
        return self.name


'''
class Tag(models.Model):
    user = models.ManyToManyField(User) # subscribed user
    name = models.CharField(max_length=200, unique=True)
    tag_type = models.CharField(max_length=200)
    #date_added = models.DateField(null=True, blank=True)
    def __str__(self):
        return self.name
'''
########

'''
class Watchlist(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    # add foreign key to user
    name = models.CharField(max_length=200, unique=True)
    tag_type = models.CharField(max_length=200)
'''
