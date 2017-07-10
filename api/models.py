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
    name = models.CharField(max_length=128)
    content_type = models.CharField(max_length=128)
    tag = models.ManyToManyField(Tag, through='ContentTag')
    image_url = models.CharField(max_length=512, default="" )
    description = models.CharField(max_length=128, default="")
    trailer = models.CharField(max_length=512, default="")
    def __str__(self):
        return self.name

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
