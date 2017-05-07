from gpp.models import Photo, Profil, Comments
from rest_framework import serializers
from django.contrib.auth.models import User, Group

class PhotoSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Photo
        fields = ('uuid', 'lat', 'lon', 'poster','timestamp', 'visible', 'ipadd', 'caption')

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'groups')


class CommentsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Comments
        fields = ('photouuid', 'comment', 'postedByuuid', 'date', 'active', 'ipadd', 'user')

class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')
