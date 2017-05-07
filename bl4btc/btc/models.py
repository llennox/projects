from django.db import models 
from django.contrib.auth.models import User
import requests, json
from django.utils import timezone
import re, uuid


class Profil(models.Model):
    user = models.OneToOneField(User, related_name='profil') #1 to 1 link with Django User
    activation_key = models.CharField(max_length=40)
    key_expires = models.DateTimeField()
    withdrawal_add = models.CharField(max_length=35,default=0)#custom validation field protect agains SQLi
    deposit_add = models.CharField(max_length=35,default=0)##custom validation field protect agains SQLi
    account_balance = models.FloatField(default=0)  
    in_escrow = models.FloatField(default=0)  
    referer = models.CharField(max_length=255,null=True)#right here migration #??
    myuuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False) 
    wif = models.CharField(max_length=255,default=0)

class sysvar(models.Model):
    timestamp = models.DateTimeField()
    btcPrice = models.CharField(default=10,max_length=40)
    counter = models.IntegerField(default=1)
    
class sellUrls(models.Model):
    user = models.CharField(max_length=255) #1 to 1 link with Django User
    website = models.URLField() 
    mozscore = models.IntegerField(default=0) # call bot in views
    price = models.FloatField(default=0)
    subpage = models.BooleanField(default=False)
    tags = models.CharField(max_length=255,default=None)
    urluuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  
    listed = models.BooleanField(default=False)
    tier = models.IntegerField(default=0)
            
class buyUrls(models.Model):
    user = models.CharField(max_length=255) #1 to 1 link with Django User
    activelink = models.URLField(default=None)  
    website = models.URLField() 
    validated = models.BooleanField(default=False)
    escrow = models.BooleanField(default=False)

class escrowPayoutLedger(models.Model):
    sellUrlUUID = models.UUIDField(default=None)
    validated = models.BooleanField(default=False)
    escrow = models.BooleanField(default=False)
    payeeUUID = models.UUIDField(default=None)
    payerUUID = models.UUIDField(default=None)
    backlink = models.URLField(default=None)
    domain = models.URLField(default=None)  
    price = models.FloatField(default=0)
    timestamp = models.DateTimeField(default=None)
    timestampofval = models.DateTimeField(default=None,null=True)
    timestampofval30 = models.DateTimeField(default=None,null=True)
    ledgerUUID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  
    
    #timestamp of sellers confirmation
    #timestamp of sellers confirmation + 30 days 


















    
