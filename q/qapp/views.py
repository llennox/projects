from django.shortcuts import render
from django.http import Http404, HttpResponse
from itertools import chain
from rest_framework import viewsets, permissions, status, authentication
from qapp.models import Photo, Comments, Profile
from django.contrib.gis.geoip2 import GeoIP2
from django.utils import timezone
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from django.core.mail import send_mail
from rest_framework.views import APIView
from rest_framework.response import Response
from boto.s3.key import Key
from math import radians, cos, sin, asin, sqrt
import math, hashlib, sys, random, os, boto, string
from qapp.serializers import PhotoSerializer, CommentsSerializer, UserSerializer
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login, logout
import operator



bucket_name ='anonshot'


def api_documentation(request):  ### popup that presents rules. 
    
    return render(request, 'api_docs.html') 


class LILOViewSet(APIView):
 
    def post(self, request, *args, format=None):
        if 'authtoken' not in request.data:
            try:
                username = request.data['username']
                password = request.data['password']
            except:
                return HttpResponse('please send a username and password or authtoken', status=status.HTTP_400_BAD_REQUEST)
            try:
                user = User.objects.get(username=username)
                print(password)
                print(user.password)
                if user.check_password(password) == True:
                    user.is_active = True
                    user.save()
                    profile = Profile.objects.get(user=user)
                    profile.isanon = request.data['isanon']
                    profile.save()
                    user = authenticate(username=username, password=password)
                    login(request, user)
                    data = {}
                    data['message'] = 'user is now logged in'
                    data['username'] = user.username
                    data['authtoken'] = user.auth_token.key
                    return Response(data, status=status.HTTP_202_ACCEPTED)
                else:
                    return HttpResponse('the password or username you entered was incorrect', status=status.HTTP_400_BAD_REQUEST)
            except User.DoesNotExist:
                return HttpResponse('that user does not exist', status=status.HTTP_400_BAD_REQUEST)
        else:
            try:
                user = User.objects.get(auth_token=request.data['authtoken'])
            except:

                return HttpResponse('please send a username and password or authtoken', status=status.HTTP_400_BAD_REQUEST)
            if user is not None:
                data = {}
                if user.is_active:
                    print("User is valid, active and authenticated")
                    login(request, user)
                    profile = Profile.objects.get(user=user)
                    profile.isanon = request.data['isanon']
                    profile.save()
                    data['message'] = 'user is now logged in'
                    data['username'] = user.username
                    data['authtoken'] = user.auth_token.key
                    return Response(data, status=status.HTTP_202_ACCEPTED)
                else:
                    user.is_active = True
                    user.save()
                    profile = Profile.objects.get(user=user)
                    profile.isanon = request.data['isanon']
                    profile.save()
                    data['message'] = 'user is now logged in and active'
                    data['username'] = user.username
                    data['authtoken'] = user.auth_token.key
                    return Response(data, status=status.HTTP_202_ACCEPTED)
                return HttpResponse('user is inactive', status=status.HTTP_400_BAD_REQUEST)
            return HttpResponse('that user does not exist', status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, format=None): # this might work doesn't really matter 
        photos = PhotoViewSet()
        user = photos.auth(args[0])
        if user.is_authenticated() == True:
            request.user = user
            logout(request)
            return HttpResponse('user has been logged out', status=status.HTTP_202_ACCEPTED)
        else:
            return HttpResponse('user is already logged out', status=status.HTTP_400_BAD_REQUEST)

    
        

  
class UserViewSet(APIView):  # need to make a

    def post(self, request, *args, format=None): # user creation return token and log in 
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid(): 
            serializer.save()
            user = User.objects.get(username=serializer.data['username'])
            user.set_password(serializer.data['password'])
            user.save()
            try:
                profile = Profile.objects.create(user=user, isanon=request.data['isanon'])
                profile.save()
            except:
                profile = Profile.objects.create(user=user, isanon=True)
                profile.save()
            token = Token.objects.get(user=user)
            data = serializer.data
            data['authtoken'] = token.key
            data['password']= 'XXXXXXXXXX'
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, format=None):# change password or username make this more secure in the future
        auth = PhotoViewSet()
        user = auth.auth(request.data['authtoken'])
        print(args[0])
        if args[0] == user.username and user.check_password(request.data['password']) == True:
            user.set_password(request.data['newpassword'])
            user.save()
            return Response('new password has been set', status=status.HTTP_202_ACCEPTED)
        else:
            return Response('username and authtoken and or password do not match', status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, format=None):
        auth = PhotoViewSet()
        user = auth.auth(request.data['authtoken'])
        if args[0] == user.username and user.check_password(request.data['password']) == True:
            user.is_active = False
            user.save()
            return Response('user has been made inactive', status=status.HTTP_202_ACCEPTED)
        else:
            return Response('username and authtoken and or password do not match', status=status.HTTP_400_BAD_REQUEST)
 
    def get(self, request, *args, format=None): # if arg is uuid return photo if arg is username return users photos
        auth = PhotoViewSet()
        user = auth.auth(args[1]) 
        profile = Profile.objects.get(user=user)
        if user.username == args[0]:
            photos = Photo.objects.filter(useruuid=profile.uuid)
            serializer = PhotoSerializer(photos, many=True)
            for photo in serializer.data:
                uuid = list(photo.values())[0]
                counter = 0
                for comment1 in Photo.return_comments(uuid):  
                    counter += 1             
                    photo['comment' + str(counter)] = {'comment_poster':comment1.poster,'comment_timestamp': comment1.timestamp,'comment_message':comment1.comment,'comment_uuid':comment1.uuid,'comment_photouuid':comment1.photouuid }
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        try: 
            photos = Photo.objects.filter(uuid=args[0])
            serializer = PhotoSerializer(photos, many=True)
            for photo in serializer.data:
                uuid = list(photo.values())[0]
                counter = 0
                for comment1 in Photo.return_comments(uuid):  
                    counter += 1             
                    photo['comment' + str(counter)] = {'comment_poster':comment1.poster,'comment_timestamp': comment1.timestamp,'comment_message':comment1.comment,'comment_uuid':comment1.uuid,'comment_photouuid':comment1.photouuid }
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        except Photo.DoesNotExist:
            return Response("photo or user not found", status=status.HTTP_400_BAD_REQUEST)
        try: 
            user = User.objects.get(username=args[0])
            photos = Photo.objects.filter(poster=user.username).order_by('timestamp')
            serializer = PhotoSerializer(photos, many=True)
            for photo in serializer.data:
                uuid = list(photo.values())[0]
                counter = 0
                for comment1 in Photo.return_comments(uuid):  
                    counter += 1             
                    photo['comment' + str(counter)] = {'comment_poster':comment1.poster,'comment_timestamp': comment1.timestamp,'comment_message':comment1.comment,'comment_uuid':comment1.uuid,'comment_photouuid':comment1.photouuid }
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        except User.DoesNotExist:
            return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)
        else: 
            return Response("photo or user not found", status=status.HTTP_400_BAD_REQUEST)

class CommentViewSet(APIView):

    def post(self, request, format=None): ###I'm here, add user etc.
        auth = PhotoViewSet()
        user = auth.auth(request.data['authtoken'])
        profile = Profile.objects.get(user=user)
        request.data['useruuid'] = str(profile.uuid)
        if profile.isanon == True:
            request.data['poster'] = 'anon'
        else: 
            request.data['poster'] = user.username
        serializer = CommentsSerializer(data=request.data)
        if serializer.is_valid(): 
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request, format=None): 
        auth = PhotoViewSet()
        user = auth.auth(request.data['authtoken'])
        profile = Profile.objects.get(user=user)
        try:
            comment = Comments.objects.get(uuid=request.data['uuid'])
            if profile.uuid == comment.useruuid:
                comment.delete()
                return Response("comment deleted", status=status.HTTP_202_ACCEPTED)
            else:
                return Response("user does not own comment", status=status.HTTP_400_BAD_REQUEST)
        except Comments.DoesNotExist:
            return Response("failure to delete comment", status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, format=None):
        auth = PhotoViewSet()
        user = auth.auth(request.data['authtoken'])
        profile = Profile.objects.get(user=user)
        comment = Comments.objects.get(uuid=request.data['commentuuid'])
        if comment.useruuid == profile.uuid:
            comment.comment = request.data['comment']
            comment.save()
            return Response("comment updated", status=status.HTTP_201_CREATED)
        else:
            return Response("user does not own comment", status=status.HTTP_400_BAD_REQUEST)
        

class PhotoViewSet(APIView):  #need to issue tokens for anon users and logged in users. 

    def auth(self, authtoken):
        
        user = User.objects.get(auth_token=authtoken)
        if user.is_authenticated():
            return user
        elif user.exists() == False:
            return HttpResponse('user does not exist', status=status.HTTP_400_BAD_REQUEST)
        elif user.is_authenticated() == False:
            return HttpResponse('you must log in first', status=status.HTTP_400_BAD_REQUEST)
        else:
            return HttpResponse('user does not exist or authtoken is incorrect', status=status.HTTP_400_BAD_REQUEST)

    def clean_content(self, form):
        content = form.cleaned_data['photo']
        content_type = content.content_type.split('/')[0]
        #print(content_type)
        if content_type in settings.CONTENT_TYPES:
            if content._size > settings.MAX_UPLOAD_SIZE:
                return False
        else:
            return False
        return content


    def get(self, request, *args, format=None):# return 60~ photos close to current gps give photos a points value I guess, return comments
        # first query database find gps data closest to users then retrieve the 60 most similar going up and down
# then find all comments attached to those photos and assign point system based on date published distance to user and comments 
        #fetchmany()   
        try:
            user = self.auth(args[2])
        except:
            return HttpResponse('authtoken is invalid', status=status.HTTP_400_BAD_REQUEST)
        photos = self.returnObjects(*args)
        serializer = PhotoSerializer(photos, many=True)
        lat1 = self.roundGET(args[0], 3)
        lon1 = self.roundGET(args[1], 3)
        for photo in serializer.data: # do the haversin and attach comments proly a new litt func 
            lat2 = float(photo['lat'])
            lon2 = float(photo['lon'])
            photo['distance'] = self.haversine(lon1, lat1, lon2, lat2) #add points based number of comments, distance, age order by these
            uuid = list(photo.values())[0]
            #photoinstance = Photo.objects.get(uuid=uuid)
            counter = 0
            for comment1 in Photo.return_comments(uuid):  
                counter += 1             
                photo['comment' + str(counter)] = {'comment_poster':comment1.poster,'comment_timestamp': comment1.timestamp,'comment_message':comment1.comment,'comment_uuid':comment1.uuid,'comment_photouuid':comment1.photouuid }
        data = serializer.data
        return Response(data, status=status.HTTP_200_OK)



    def haversine(self, lon1, lat1, lon2, lat2):
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2]) 
        dlon = lon2 - lon1 
        dlat = lat2 - lat1 
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a)) 
        r = 3956 # Radius of earth in kilometers. Use 3956 for miles
        distance = c * r
        distance = self.roundGET(distance, 4)
        return distance


    def returnObject(self, *args):
        uuid = args[0]
        photo = Photo.objects.get(uuid=uuid)
        return photo 


    def returnObjects(self, *args):  
        lat = self.roundGET(args[0], 0)
        lon = self.roundGET(args[1], 0)
        lat = int(lat)
        lon = int(lat)
        #lon = int(lon)
        photos1 = Photo.objects.filter(lat__startswith=lat, lon__startswith=lon)
        #self.return_comments(photos1)
        nlat = lat + 1
        photos2 = Photo.objects.filter(lat__startswith=nlat, lon__startswith=lon)
        nlat = lat - 1
        photos3 = Photo.objects.filter(lat__startswith=nlat, lon__startswith=lon) 
        nlon = lon + 1 
        photos4 = Photo.objects.filter(lat__startswith=lat, lon__startswith=nlon)
        nlon = lon - 1 
        photos5 = Photo.objects.filter(lat__startswith=lat, lon__startswith=nlon)
        nlon = lon - 1 
        nlat = lat - 1 
        photos6 = Photo.objects.filter(lat__startswith=nlat, lon__startswith=nlon)
        nlon = lon + 1 
        nlat = lat + 1 
        photos7 = Photo.objects.filter(lat__startswith=nlat, lon__startswith=nlon)
        nlon = lon + 1 
        nlat = lat - 1 
        photos8 = Photo.objects.filter(lat__startswith=nlat, lon__startswith=nlon)
        nlon = lon - 1 
        nlat = lat + 1 
        photos9 = Photo.objects.filter(lat__startswith=nlat, lon__startswith=nlon)
        photos = list(chain(photos1, photos2, photos3, photos4, photos5, photos6, photos7, photos8, photos9))
        lat1 = self.roundGET(args[0], 3)
        lon1 = self.roundGET(args[1], 3)
        for photo in photos: # do the haversin and attach comments proly a new litt func 
            lat2 = float(photo.lat)
            lon2 = float(photo.lon)
            photo.distance = self.haversine(lon1, lat1, lon2, lat2) #add points based number of comments, distance, age order by these
        photos.sort(key=lambda photo:photo.distance) #x:(x['title'], x['title_url'], x['id']))
        return photos[:100]# attach comments and do the haversine 
        #for arg in *args search query database for ex. 32.32*, 23.23* if .count() >= 60: otherfunc(query) else query for 32.3*, 23.2*  
        # and so on and so forth 


    def roundGET(self, var, n):
        wasNegative = False 
        var = float(var)
        if var < 0:
            var = var * -1
            wasNegative = True 
        var = math.floor(var * 10 ** n) / 10 ** n
        if wasNegative == True:
            var = var * -1
        return var

    



    def post(self, request, format=None):#save photo to amazon save url, uuid, lat, long, timestamp, visible IO, poster uuid
        user = self.auth(request.data['authtoken'])
        profile = Profile.objects.get(user=user)
        request.data['useruuid'] = str(profile.uuid)
        if profile.isanon == True:
            request.data['poster'] = 'anon'
        else:
            request.data['poster'] = user.username
        request.data['visible'] = True 
        self.roundgps('lon' ,request)
        self.roundgps('lat' ,request)
        serializer = PhotoSerializer(data=request.data)
        if serializer.is_valid(): # save info to model then send to amazon, if fail delete photo 
            serializer.save()
            uuid = serializer.data['uuid']
            f=request.data['media']
            destination=open('%s.jpg' % uuid , 'wb+')
            photo = '%s.jpg' % uuid
            for chunk in f.chunks():
                destination.write(chunk) ####delete this later writes photos to memory
            destination.close()
            try:
                #self.push_picture_to_s3(uuid)  
                os.remove(photo)
            except:
                Photo.objects.get(uuid=uuid).delete()
                os.remove(photo)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            data = serializer.data
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request): # make sure user owns photo delete comments too
        user = self.auth(request.data['authtoken'])
        profile = Profile.objects.get(user=user)
        try:
            photo = Photo.objects.get(uuid=request.data['uuid'])
            if profile.uuid == photo.useruuid:
                comments = Comments.objects.filter(photouuid=photo.uuid)
                photo.delete()
                self.delete_picture_from_s3(request.data['uuid'])
                return Response("photo deleted", status=status.HTTP_202_ACCEPTED)
            else:
                return Response("user does not own photo", status=status.HTTP_400_BAD_REQUEST)
        except Photo.DoesNotExist:
            return Response("failure to delete photo from server", status=status.HTTP_400_BAD_REQUEST)

            
  
    def delete_picture_from_s3(self,uuid):  # check auth to delete photo 

        try:
            conn = boto.connect_s3(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)

            bucket = conn.get_bucket(bucket_name)
            # go through each version of the file
            key = '%s.jpg' % uuid
            fn = '%s.jpg' % uuid
            k = Key(bucket)

            k.delete_key(key)          
            # we need to make it public so it can be accessed publicly
            # using a URL like http://s3.amazonaws.com/bucket_name/key

            # remove the file from the web server


        except:
            return HttpResponse(status=500)


    def push_picture_to_s3(self,uuid):
        try:
            conn = boto.connect_s3(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
            bucket = conn.get_bucket(bucket_name)
    # go through each version of the file
            key = '%s.jpg' % uuid
            fn = '%s.jpg' % uuid
            # create a key to keep track of our file in the storage 
            k = Key(bucket)
            k.key = key            
            k.set_contents_from_filename(fn)          
            # we need to make it public so it can be accessed publicly
            # using a URL like http://s3.amazonaws.com/bucket_name/key
            k.make_public()
            # remove the file from the web server

            return 
        except:
            raise Exception
            return HttpResponse(status=500)

        
        
    def roundgps(self, fl, request):
        var = request.data[fl]
        var = float(var)
        wasNegative = False 
        if var < 0:
            var = var * -1
            wasNegative = True 
        var = math.floor(var * 10 ** 3) / 10 ** 3
        if wasNegative == True:
            var = var * -1
        request.data[fl]=var
        var = str(var)
        if var[::-1].find('.') == 3:
            return request
        else:
            request.data[fl]='fail'
            return request




