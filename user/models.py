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
    WATCHLIST_ADD = 'watchlist_add'
    ALREADY_SEEN_ADD = 'already_seen_add'
    BROADCAST_RESPONSE = 'broadcast_response'
    USER_SHARED = 'user_shared'
    WEEKLY_REC_ACTION = 'weekly_rec_action'
    ACTION_CHOICES = (
        (EXPLORE_TAG_SELECTED, 'Explore Tag Selected'),
        (WATCHLIST_VIEWED, 'Watchlist Viewed'),
        (EXPLORE_MODE_SELECTED, 'Explore Mode Selected'),
        (WATCHLIST_ADD, 'Watchlist Add'),
        (ALREADY_SEEN_ADD, 'Already Seen Add'),
        (BROADCAST_RESPONSE, 'Broadcast Response'),
        (USER_SHARED, 'User Shared'),
        (WEEKLY_REC_ACTION, 'Weekly Rec Action'),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=100, choices=ACTION_CHOICES)
    explore_tag = models.CharField(max_length=100, blank=True)
    content = models.ForeignKey(Content, on_delete=models.CASCADE, null=True, blank=True)
    broadcast_response_type = models.CharField(max_length=100, blank=True) #what action did people take on each broadcast
    weekly_rec_response = models.CharField(max_length=100, blank=True) #what action did people take on the weekly rec

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
