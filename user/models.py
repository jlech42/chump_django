from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from service.models import Service
from content.models import Content

# Create your models here.

class UserSubscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    class Meta:
        unique_together = ('user', 'service',)
    def __str__(self):
        return self.user.first_name + self.service.name

class UserContent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.ForeignKey(Content, on_delete=models.CASCADE)
    on_watchlist = models.BooleanField(default=False)
    already_seen = models.BooleanField(default=False)
    watching_now = models.BooleanField(default=False)
    was_on_watchlist = models.BooleanField(default=False)
    not_interested = models.BooleanField(default=False)
    shared = models.BooleanField(default=False)
    class Meta:
        unique_together = ('content', 'user')
    def __str__(self):
        return self.user.first_name + ' ' + self.user.last_name + ' ' + self.content.title

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=100)
    #chatfuel_user_id = models.BigIntegerField # from chatfuel
    #messenger_user_id = models.BigIntegerField # from chatfuel
    def __str__(self):
        return self.user.username

class UserLog(models.Model):
    EXPLORE_TAG_SELECTED = 'explore_tag_selected'
    WATCHLIST_VIEWED = 'watchlist_viewed'
    EXPLORE_MODE_SELECTED = 'explore_mode_selected'
    ACTION_CHOICES = (
        (EXPLORE_TAG_SELECTED, 'Explore Tag Selected'),
        (WATCHLIST_VIEWED, 'Watchlist Viewed'),
        (EXPLORE_MODE_SELECTED, 'Explore Mode Selected'),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=100, choices=ACTION_CHOICES)
    explore_tag = models.CharField(max_length=100, blank=True)



    #chatfuel_user_id = models.BigIntegerField # from chatfuel
    #messenger_user_id = models.BigIntegerField # from chatfuel
    def __str__(self):
        return self.user.first_name

# signals to hook up user to profile
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
