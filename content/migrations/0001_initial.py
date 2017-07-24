# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-07-24 01:29
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Content',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chump_id', models.IntegerField(blank=True, default=None, null=True)),
                ('imdb_id', models.CharField(blank=True, max_length=128)),
                ('tmdb_id', models.CharField(blank=True, max_length=128, unique=True)),
                ('content_type', models.CharField(blank=True, max_length=128)),
                ('title', models.TextField(blank=True)),
                ('logline', models.TextField(blank=True)),
                ('no_seasons', models.IntegerField(blank=True, default=None, null=True)),
                ('no_episodes', models.IntegerField(blank=True, default=None, null=True)),
                ('runtime_per_episode', models.IntegerField(blank=True, default=None, null=True)),
                ('runtime', models.IntegerField(blank=True, default=None, null=True)),
                ('imdb_rating', models.FloatField(blank=True, default=None, null=True)),
                ('rt_rating', models.FloatField(blank=True, default=None, null=True)),
                ('meta_score', models.FloatField(blank=True, default=None, null=True)),
                ('director', models.CharField(blank=True, max_length=128)),
                ('trailer_link', models.URLField(blank=True, max_length=128)),
                ('image_link', models.URLField(blank=True, max_length=128)),
                ('discovery_mode', models.CharField(blank=True, max_length=128)),
                ('in_set', models.IntegerField(blank=True, null=True)),
                ('primary_mode', models.CharField(blank=True, max_length=128)),
                ('topic_one', models.CharField(blank=True, max_length=128)),
                ('topic_two', models.CharField(blank=True, max_length=128, null=True)),
                ('on_netflix', models.BooleanField(default=False)),
                ('on_amazon', models.BooleanField(default=False)),
                ('on_hulu', models.BooleanField(default=False)),
                ('on_hbo', models.BooleanField(default=False)),
                ('on_other', models.CharField(blank=True, max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='ContentTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='content.Content')),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('tag_type', models.CharField(max_length=128)),
            ],
        ),
        migrations.AddField(
            model_name='contenttag',
            name='tag',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='content.Tag'),
        ),
        migrations.AddField(
            model_name='content',
            name='tag',
            field=models.ManyToManyField(default='', through='content.ContentTag', to='content.Tag'),
        ),
        migrations.AlterUniqueTogether(
            name='contenttag',
            unique_together=set([('content', 'tag')]),
        ),
    ]