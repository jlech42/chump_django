from django.db import models
from django.contrib.auth.models import User

#from user.models import UserSubscription

# Create your models here.

class Tag(models.Model):
    name = models.CharField(max_length=128)
    tag_type = models.CharField(max_length=128)
    def __str__(self):
        return self.name

class Content(models.Model):
    chump_id = models.IntegerField(default=0)
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
    rt_rating = models.FloatField(null=True, blank=True)
    meta_score = models.FloatField(null=True)
    director = models.CharField(max_length=128, blank=True)
    trailer_link = models.URLField(max_length=128, blank=True)
    image_link = models.URLField(max_length=128, blank=True)
    discovery_mode = models.CharField(max_length=128, blank=True)
    #keywords_list = models.CharField(max_length=128, blank=True)
    in_set = models.IntegerField(null=True)
    primary_mode = models.CharField(max_length=128, blank=True)
    topic_one = models.CharField(max_length=128, blank=True)
    topic_two = models.CharField(max_length=128, null=True, blank=True)
    on_netflix = models.BooleanField(default=False)
    on_amazon = models.BooleanField(default=False)
    on_hulu = models.BooleanField(default=False)
    on_hbo = models.BooleanField(default=False)
    on_other = models.CharField(max_length=128, blank=True)
    tag = models.ManyToManyField(Tag, through='ContentTag', default ='')
    def __str__(self):
        return self.title

class ContentTag(models.Model):
    content = models.ForeignKey(Content, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    class Meta:
        unique_together = ('content', 'tag',)
