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
        return self.user.username

# signals to hook up user to profile
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class Tag(models.Model):
    name = models.CharField(max_length=128)
    tag_type = models.CharField(max_length=128)
    def __str__(self):
        return self.name

class Content(models.Model):
    imdb_id = models.CharField(max_length=128, blank=True)
    tmdb_id = models.CharField(max_length=128, unique=True)
    content_type = models.CharField(max_length=128, blank=True)
    title = models.TextField(blank=True)
    logline = models.TextField(blank=True)
    no_seasons = models.IntegerField(null=True)
    no_episodes = models.IntegerField(null=True)
    runtime_per_episode = models.IntegerField(null=True)
    runtime = models.IntegerField(null=True)
    imdb_rating = models.FloatField(null=True)
    rt_rating = models.FloatField(null=True)
    director = models.CharField(max_length=128, blank=True)
    trailer_link = models.CharField(max_length=128, blank=True)
    image_link = models.CharField(max_length=128, blank=True)
    topic_one = models.CharField(max_length=128, blank=True)
    topic_two = models.CharField(max_length=128, null=True, blank=True)
    on_netflix = models.BooleanField(default=False)
    on_amazon = models.BooleanField(default=False)
    on_hulu = models.BooleanField(default=False)
    on_hbo = models.BooleanField(default=False)
    on_other = models.CharField(max_length=128, blank=True)
    tag = models.ManyToManyField(Tag, through='ContentTag')
    def __str__(self):
        return self.title

class Service(models.Model):
    name = models.CharField(max_length=128, unique=True)
    users = models.ManyToManyField(User, through='UserSubscription')
    content = models.ManyToManyField(Content, through='ServiceContent')
    def __str__(self):
        return self.name

class UserSubscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    class Meta:
        unique_together = ('user', 'service',)

class ServiceContent(models.Model):
    content = models.ForeignKey(Content, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    class Meta:
        unique_together = ('content', 'service',)

class ContentTag(models.Model):
    content = models.ForeignKey(Content, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    class Meta:
        unique_together = ('content', 'tag',)
