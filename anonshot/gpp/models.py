from django.db import models
from django.contrib.auth.models import User
import requests, json
from django.utils import timezone
import re, uuid

class Photo(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lat = models.FloatField()
    lon = models.FloatField()
    poster = models.CharField(max_length=50, default="anon")
    timestamp = models.DateTimeField(auto_now_add=True)
    place = models.CharField(max_length=255, default="Tuvalvu")
    visible = models.BooleanField(default=True)
    ipadd = models.CharField(max_length=50, default="anon")
    caption = models.CharField(max_length=125, default="")
    def return_comments(self):
        comments = Comments.objects.filter(photouuid=self.uuid).order_by('date')
        return comments

class Profil(models.Model):
    user = models.OneToOneField(User, related_name='profil') #1 to 1 link with Django User
    activation_key = models.CharField(max_length=40)
    key_expires = models.DateTimeField()
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dateCreated = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    bio = models.CharField(max_length=255, default='')
    profileImg = models.CharField(max_length=40, default='')

class Comments(models.Model):
    ipadd = models.CharField(max_length=50, default="anon")
    user = models.CharField(max_length=80, default="anon")
    photouuid = models.UUIDField(default=None)
    comment = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

class Messages(models.Model):
    sender = models.CharField(max_length=50, default="anon")
    date = models.DateTimeField(auto_now_add=True)
    message = models.CharField(max_length=255, default='')
