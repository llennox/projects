
from gpp.forms import RegistrationForm, SignInForm, ChangePassForm, EmailNewPass, LeaveCommentForm, UploadForm, ProfileBioForm, ProfileImgForm
from rest_framework import viewsets, permissions, status
from gpp.models import Photo, Comments, Profil
from gpp.serializers import PhotoSerializer, UserSerializer, CommentsSerializer, GroupSerializer
from django.contrib.auth.models import User, Group
from django.contrib.gis.geoip2 import GeoIP2
from django.utils import timezone
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from django.shortcuts import redirect, HttpResponseRedirect, get_object_or_404, render
from django.core.mail import send_mail
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from boto.s3.key import Key
from math import radians, cos, sin, asin, sqrt
import math, hashlib, sys, random, os, boto, string
from django.template.defaultfilters import filesizeformat
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django import forms, http



# WEB VERSION 1/4/2017
#account creation
#upload view
#send message view, includes any prior convo
#view photos view 
#forgot pass view etc. 
#custom auth 
#
#
#
PRIVATE_IPS_PREFIX = ('10.', '172.', '192.', )
BLOCKED_IPS =['68.97.193.129','127.0.0.1']
bucket_name =os.environ['bucket_name']
AWS_ACCESS_KEY_ID=os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY=os.environ['AWS_SECRET_ACCESS_KEY']

class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)



def get_client_ip(request):
    """get the client ip from the request
    """
    remote_address = request.META['REMOTE_ADDR']

    # set the default value of the ip to be the REMOTE_ADDR if available
    # else None
    ip = remote_address
    # try to get the first non-proxy ip (not a private ip) from the
    # HTTP_X_FORWARDED_FOR
    x_forwarded_for = request.META['HTTP_X_FORWARDED_FOR']
    print(x_forwarded_for)
    if x_forwarded_for:
        proxies = x_forwarded_for.split(',')
        # remove the private ips from the beginning
        while (len(proxies) > 0 and
                proxies[0].startswith(PRIVATE_IPS_PREFIX)):
            proxies.pop(0)
        # take the first ip which is not a private one (of a proxy)
        if len(proxies) > 0:
            ip = proxies[0]

    return ip

def home_page(request):  ### popup that presents rules. 
    g = GeoIP2()
    ip = get_client_ip(request)
    try:
        lat,lng = g.lat_lon(ip)
        city = g.city(ip)
        place = city['city'] + ', ' + city['country_name']
    except:
        lat,lng = -7.480207, 178.675933
        place = "Tuvalu"
        success = "We can't find your location so your photo will be posted to the Island Nation of Tuvalu"
    photos = Photo.objects.all().order_by('timestamp')[:60][::-1]
    for photo in photos:
        lon2 = photo.lon
        lat2 = photo.lat
        uuid = photo.uuid   
        getPhotos = PhotoViewSet()
        photo.distance = getPhotos.haversine(lng, lat, lon2, lat2)
    return render(request, 'home.html',{'photos':photos, 'place':place}) 

def api_documentation(request):  ### popup that presents rules. 
    
    return render(request, 'api_docs.html') 

def upload_page(request): #upload photos, size limit and gps data included$!!!!!!!!!!!!!!!!ability to roll for random city upload
    success = ''
    fail = False
    form = UploadForm()
    g = GeoIP2()
    ip = get_client_ip(request)
    try:
        lat,lng = g.lat_lon(ip)
        city = g.city(ip)
        place = city['city'] + ', ' + city['country_name']
    except:
        lat,lng = -7.480207, 178.675933
        place = "Tuvalu"
        success = "We can't find your location so your photo will be posted to the Island Nation of Tuvalu"
    if request.method == 'POST':
        myrequest = request.POST.copy()
        form = UploadForm(request.POST, request.FILES)
        
        if form.is_valid():
            getPhotos = PhotoViewSet()
            if getPhotos.clean_content(form) == False:
                fail = True

            myrequest['lat'] = lat
            myrequest['lon'] = lng
            if request.user.is_authenticated():
                myrequest['poster'] = request.user.username
            else:
                myrequest['poster'] = "anon"
            if fail == False:
                photo = Photo(poster=myrequest['poster'],lat=lat, lon=lng,caption=myrequest['caption'], place=place)
                photo.save()
                f=request.FILES['photo']
                uuid = photo.uuid
                destination=open('%s.jpg' % uuid , 'wb+')
                for chunk in f.chunks():
                    destination.write(chunk) 
                destination.close()
              
                try:
                    success = getPhotos.push_picture_to_s3(uuid) 
                    #if success != '':
                        #return render(request, 'upload.html', {'form':form, 'place':place,'success':success,'fail':fail}) 
                        
                    
                except:
                    return render(request, 'upload.html', {'form':form, 'place':place,'success':success,'fail':fail}) 
                mystring = '/photos/' + '#' + str(uuid)
                return redirect(mystring)
        else:
            success = "there was a problem uploading the file"
  
    return render(request, 'upload.html', {'form':form, 'place':place,'success':success,'fail':fail}) 

def photos_page(request): #return photos within range of user, order by distance
    g = GeoIP2()
    ip = get_client_ip(request)
    try:
        lat,lng = g.lat_lon(ip)
        city = g.city(ip)
        place = city['city'] + ', ' + city['country_name']
    except:
        lat,lng = -7.480207, 178.675933
        place = "Tuvalu"
    getPhotos = PhotoViewSet()
    photos = getPhotos.returnObjects(lat, lng)
    #photos.order_by('distance')
    for photo in photos:
        lon2 = photo.lon
        lat2 = photo.lat
        uuid = photo.uuid        
        photo.distance = getPhotos.haversine(lng, lat, lon2, lat2)
    form = LeaveCommentForm()
    if request.method == 'POST': #make this into a modal
        form = LeaveCommentForm(request.POST)
        if form.is_valid():
            message = form.cleaned_data['message']
            photouuid = request.POST['uuid']
            if request.user.is_authenticated():
                ser = request.user.username
                comment = Comments(comment=message, user=ser,photouuid=photouuid)
            else: 
                comment = Comments(comment=message,photouuid=photouuid)
            comment.save()
            form = LeaveCommentForm()
            return redirect('/photos/')
    return render(request, 'photos.html',{'photos':photos, 'place':place,'form':form})  

def viewProfile_page(request, username): 
    user = User.objects.get(username=username)
    profile = Profil.objects.get(user=user)
    bioform = ProfileBioForm()
    imgform = ProfileImgForm() 
    g = GeoIP2()
    ip = get_client_ip(request)
    try:
        lat,lng = g.lat_lon(ip)
        city = g.city(ip)
        place = city['city'] + ', ' + city['country_name']
    except:
        lat,lng = -7.480207, 178.675933
        place = "Tuvalu"
    photos = Photo.objects.filter(poster=username).order_by('timestamp').reverse()
    #print(request.user.username)
    #print(username)
    if request.user.username == username:
        owner = True
    else:
        owner = False
    if photos.exists():
        getPhotos = PhotoViewSet()
        for photo in photos:
            lon2 = photo.lon
            lat2 = photo.lat
            uuid = photo.uuid        
            photo.distance = getPhotos.haversine(lng, lat, lon2, lat2)
        
        form = LeaveCommentForm()
        if request.method == 'POST': #make this into a modal
            form = LeaveCommentForm(request.POST)
            if form.is_valid():
                message = form.cleaned_data['message']
                photouuid = request.POST['uuid']
                if request.user.is_authenticated():
                    ser = request.user.username
                    comment = Comments(comment=message, user=ser,photouuid=photouuid)
                else: 
                    comment = Comments(comment=message,photouuid=photouuid)
                comment.save()
                form = LeaveCommentForm()
                url = '/viewProfile_page/' + username
                return redirect(url)
        return render(request, 'viewProfile_page.html',{'username':username,'owner':owner,'photos':photos,'place':place,'form':form,'imgform':imgform,'bioform':bioform,'profile':profile}) 
    else: 
        form = LeaveCommentForm()
        return render(request, 'viewProfile_page.html',{'username':username,'owner':owner,'place':place,'form':form,'imgform':imgform,'bioform':bioform,'profile':profile}) 

def editBio(request, username): 
    if request.user.username == username:
        owner = True
        if request.method == 'POST':
            form = ProfileBioForm(request.POST)
            if form.is_valid():

                profil = Profil.objects.get(user=request.user)
                profil.bio = request.POST['bio'] 
                profil.save()
        mystring = '/viewProfile_page/' + username
        return redirect(mystring)

    else:
        owner = False
        mystring = '/viewProfile_page/' + username
        return redirect(mystring)
        #return render(request, 'viewProfile_page.html',{'username':username,'owner':owner,'place':place,'form':form,'imgform':imgform,'bioform':bioform}) 

def editProfileImg(request, username):
    fail = False
    if request.user.username == username: 
        if request.method == 'POST':
            myrequest = request.POST.copy()
            form = ProfileImgForm(request.POST, request.FILES)
        
            if form.is_valid():
                getPhotos = PhotoViewSet()
                if getPhotos.clean_content(form) == False:
                    fail = True
             
                if fail == False:
                    profil = Profil.objects.get(user=request.user)
                    f=request.FILES['photo']
                    uuid = profil.uuid
                    print(profil.user)
                    print(uuid)
                    getPhotos.delete_picture_s3(uuid)
                    destination=open('%s.jpg' % uuid , 'wb+')
                    for chunk in f.chunks():
                        destination.write(chunk) ####delete this later writes photos to memory
                    destination.close()
               
                    getPhotos.push_picture_to_s3(uuid) 
                    success = True  
            
        else:
            success = "there was a problem uploading the file"
        mystring = '/viewProfile_page/' + username
        return redirect(mystring)
    else:
        mystring = '/viewProfile_page/' + username
        return redirect(mystring)

def messages_page(request, username):  #user name
    
    return render(request, 'messages.html') 

def photo_page(request, uuid):  #user name
    g = GeoIP2()
    ip = get_client_ip(request)
    try:
        lat,lng = g.lat_lon(ip)
        city = g.city(ip)
        place = city['city'] + ', ' + city['country_name']
    except:
        lat,lng = -7.480207, 178.675933
        place = "Tuvalu"
    if request.user.is_authenticated:
        owner = True
    else:
        owner = False
    form = LeaveCommentForm()
    if request.method == 'POST': #make this into a modal
        form = LeaveCommentForm(request.POST)
        if form.is_valid():
            message = form.cleaned_data['message']
            photouuid = request.POST['uuid']
            if request.user.is_authenticated():
                ser = request.user.username
                comment = Comments(comment=message, user=ser,photouuid=photouuid)
            else: 
                comment = Comments(comment=message,photouuid=photouuid)
            comment.save()
            form = LeaveCommentForm()
    getPhoto = PhotoViewSet()
    photo = getPhoto.returnObject(uuid)
    return render(request, 'photoView.html',{'photo':photo,'owner':owner,'form':form,'place':place}) 

def logout_view(request):
  
    logout(request)

    return render(request, 'home.html') 

def delete_comment(request, uuid, username, photouuid):
    if request.user.username == username:
        comment = Comments.objects.get(uuid=uuid)
        comment.delete()
        mystring = '/photoView/' + photouuid + '/#bottom'
        return redirect(mystring)
        #return render(request, 'photoView.html',{'photo':photo,'form':form}) 
    else:
        return redirect('/')

def delete_photo(request, uuid, username):
    if request.user.username == username or request.user.is_superuser:
        photo = Photo.objects.get(uuid=uuid)
        photo.delete()
        getPhotos = PhotoViewSet()
        getPhotos.delete_picture_s3(uuid)
        mystring = '/viewProfile_page/' + username
        return redirect(mystring)
    else:
        return redirect('/')

def flag_photo(request, uuid):
     send_mail('photo flagged', 'this photo was flagged https://s3.amazonaws.com/anonshot/' + uuid + '.jpg' , 'gonnellcough@gmail.com', ['gonnellcough@gmail.com'], fail_silently=False)
     return render(request, 'photoflagged.html')


def register_page(request):
    email_taken = False
    username_taken = False
    if request.user.is_authenticated():
        return render(request, 'home.html')
    registration_form = RegistrationForm()
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            datas={}
            if User.objects.filter(username=form.cleaned_data['username']).exists():
                username_taken = True
                return render(request, 'register_page.html', {'form':registration_form,'username_taken': username_taken})
            elif User.objects.filter(email=form.cleaned_data['email']).exists():
                email_taken = True
                return render(request, 'register_page.html', {'form':registration_form,'email_taken': email_taken})
            datas['username']=form.cleaned_data['username']
            datas['email']=form.cleaned_data['email']
            datas['password1']=form.cleaned_data['password1']
            salt = hashlib.sha1(str(random.random()).encode('utf-8')).hexdigest()[:5]
            usernamesalt = datas['email']
            if isinstance(usernamesalt, str):
                usernamesalt=str.encode(usernamesalt)
            if isinstance(salt, str):
                salt=str.encode(salt)
            #print(salt)
            #print(usernamesalt)
            datas['activation_key']=hashlib.sha1(salt+usernamesalt).hexdigest()
            datas['email_path']="/home/gene-art/anonshot/gpp/static/ActivationEmail.txt"
            datas['email_subject']="activate your account"
            form.sendEmail(datas) #Send validation email
            form.save(datas) #Save the user and his profile
            request.session['registered']=True #For display purposes
            return render(request, 'register_page.html', {'email_sent':True})
        else:

            registration_form = form #Display form with error messages (incorrect fields, etc
    return render(request, 'register_page.html', {'form':registration_form})




def activation(request, key):
    activation_expired = False
    already_active = False
    profil = get_object_or_404(Profil, activation_key=key)
    if profil.user.is_active == False:
        now = timezone.now()
        if now > profil.key_expires:
            activation_expired = True #Display : offer to user to have another activation link (a link in template sending to the view new_activation_link)
            id_user = profil.user.username
            
        else: #Activation successful
            profil.user.is_active = True
            profil.user.save()
            id_user = None
    #If user is already active, simply display error message
    else:
        id_user = None
        already_active = True #Display : error message
    return render(request, 'activation.html', {'activation_expired':activation_expired,'already_active':already_active,'id_user':id_user})#need to fix this

def new_activation_link(request, user_id):# check if it's the same user and if they are already authed # new email not being sent



    form = RegistrationForm()
    datas={}
    user = User.objects.get(username=user_id)
   
    
    if user is not None and not user.is_active:#here
        datas['username']=user.username
        datas['email']=user.email
        datas['email_path']="/home/gene-art/anonshot/gpp/static/ResendEmail.txt"
        datas['email_subject']="Welcome to anonshot alpha release"

        salt = hashlib.sha1(str(random.random()).encode('utf-8')).hexdigest()[:5]
        usernamesalt = datas['email']
            
        if isinstance(usernamesalt, str):
            usernamesalt=str.encode(usernamesalt)
        if isinstance(salt, str):
            salt=str.encode(salt)
        datas['activation_key']= hashlib.sha1(salt+usernamesalt).hexdigest()

        profil = Profil.objects.get(user=user)
        profil.activation_key = datas['activation_key']
        profil.key_expires=timezone.now() + datetime.timedelta(days=1)
        # generate public child from wallet file here 
        profil.save()

        form.sendEmail(datas)
        request.session['new_link']=True #Display : new link send
        return render(request, 'register_page.html', {'email_sent':True})
    else:
        return render(request, 'home.html')

def reset_password(request): #send email with new password set new password, check if email exists 
    email_new_pass = EmailNewPass()
    form = EmailNewPass(request.POST)
    if request.method == 'POST' and form.is_valid():
   
        if User.objects.filter(email=form.cleaned_data['email']).exists() == False:
            email_invalid = True
            return render(request,'passwordsent.html',{'form':email_new_pass, 'email_invalid': email_invalid})
        N = 12
        password = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(N))
        u = User.objects.get(email=form.cleaned_data['email'])
        u.set_password(password)
        u.save()
        send_mail('new password', 'hello, please log with this password and change it:' + password, 'gonnellcough@gmail.com', [form.cleaned_data['email']], fail_silently=False)
        success = True
        return render(request,'passwordsent.html',{'success': success})
    
    else: 
        return render(request,'passwordsent.html',{'form':email_new_pass})

def sign_page(request):
    disabled_account = False
    incorrect_pass_or_username = False
    
    if request.user.is_authenticated():
        return render(request, 'sign_in.html')
    sign_in_form = SignInForm()
    if request.method == 'POST':

        form = SignInForm(request.POST)
        if form.is_valid():
            datas={}
          
            datas['username']=form.cleaned_data['username']
            datas['password1']=form.cleaned_data['password1']
            user = authenticate(username=datas['username'], password=datas['password1'])
            if user is not None:
    # the password verified for the user
                if user.is_active:
                    #print("User is valid, active and authenticated")
                    login(request, user)
                    profil = Profil.objects.get(user=request.user)
                    
                    
                    return render(request,'home.html')
                else:
                    disabled_account = True
                    #print("The password is valid, but the account has been disabled! you may need to verify email")
            else:
    # the authentication system was unable to verify the username and password
                #print("The username or password were incorrect.")
                incorrect_pass_or_username = True
    return render(request, 'sign_in.html', {'form':sign_in_form, 'disabled_account': disabled_account, 'incorrect':incorrect_pass_or_username})#add error messages here!!!! 



def change_password(request):
    successful = False
    form = ChangePassForm(request.POST)
    if request.user.is_authenticated() and request.method == 'POST' and form.is_valid():# if password is correct for user, change to new password

 
        datas = {}
        datas['password1']=form.cleaned_data['password1']
        datas['password2']=form.cleaned_data['newpassword1']
        datas['password3']=form.cleaned_data['newpassword2']
        if request.user.check_password(datas['password1']) == True and datas['password2'] == datas['password3']:
            request.user.set_password(datas['password2'])
            successful = True
            request.user.save()
            return render(request, 'change_password.html',{'form':form,'successful':successful})
        elif request.user.check_password(datas['password1']) == False:
            incorrect_pass = True
            return render(request, 'change_password.html',{'form':form,'successful':successful, 'incorrect_pass':incorrect_pass})
        else:
            passwords_mismatch = True
            return render(request, 'change_password.html',{'form':form,'successful':successful, 'passwords_mismatch':passwords_mismatch})            
    else:
        change_pass_form = ChangePassForm()
        return render(request, 'change_password.html',{'form':change_pass_form})# get error messages to work





######################################################################API VIEW BELOW 






class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

class CommentViewSet(APIView):

    def post(self, request, format=None): ###I'm here, add user etc.

        #request.POST['ipadd'] = get_client_ip(request)
        #request.POST['active'] = True 
        #data.active = True
        serializer = CommentsSerializer(data=request.POST)
        #print(seializer.data)
        #serializer.active = True
        if serializer.is_valid(): 
            serializer.validated_data['active'] = True
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PhotoViewSet(APIView):  #need to issue tokens for anon users and logged in users. 

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
        photos = self.returnObjects(*args)
        serializer = PhotoSerializer(photos, many=True)
        lat1 = self.roundGET(args[0], 3)
        lon1 = self.roundGET(args[1], 3)
        for photo in serializer.data: # do the haversin and attach comments proly a new litt func 
            lat2 = float(photo['lat'])
            lon2 = float(photo['lon'])
            photo['distance'] = self.haversine(lon1, lat1, lon2, lat2) #add points based number of comments, distance, age order by these 
        data = serializer.data
        return Response(data)



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
        lat = self.roundGET(args[0], 2)
        lon = self.roundGET(args[1], 2)
        photos = Photo.objects.filter(lat__startswith=lat, lon__startswith=lon, visible=True).order_by('timestamp').reverse()
        if photos.count() <= 60:
            lat = self.roundGET(args[0], 1)
            lon = self.roundGET(args[1], 1)
            photos = Photo.objects.filter(lat__startswith=lat, lon__startswith=lon, visible=True).order_by('timestamp').reverse()
        if photos.count() <= 60:
            lat = int(lat)
            lon = int(lon)
            photos = Photo.objects.filter(lat__startswith=lat, lon__startswith=lon, visible=True).order_by('timestamp').reverse()
        #photos.order_by('timestamp').reverse()
        return photos# attach comments and do the haversine 
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
        request['ipadd'] = get_client_ip(request)
        request['visible'] = True 
        self.roundgps('lon' ,request)
        self.roundgps('lat' ,request)
        serializer = PhotoSerializer(data=request.POST)
        if serializer.is_valid(): # save info to model then send to amazon, if fail delete photo 
            serializer.save()

            uuid = serializer.data['uuid']
            f=request.FILES['media']
            destination=open('%s.jpg' % uuid , 'wb+')
            for chunk in f.chunks():
                destination.write(chunk) ####delete this later writes photos to memory

            destination.close()
            self.push_picture_to_s3(uuid)  
            os.remove(destination)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
  
    def delete_picture_s3(self,uuid):

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
            os.remove(fn)

        except:
            return  

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
            os.remove(fn)
            print("success")
        except:
            success = "your photo failed to upload"
            return success
        
        
    def roundgps(self, fl, request):
        var = request.POST[fl]
        var = float(var)
        wasNegative = False 
        if var < 0:
            var = var * -1
            wasNegative = True 
        var = math.floor(var * 10 ** 3) / 10 ** 3
        if wasNegative == True:
            var = var * -1
        request.POST[fl]=var
        var = str(var)
        if var[::-1].find('.') == 3:
            return request
        else:
            request.POST[fl]='fail'
            return request

























