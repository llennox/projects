from django.shortcuts import render
from btc.forms import RegistrationForm, SignInForm, ChangePassForm, EmailNewPass, btcWithdrawalForm, sellUrlForm, buyUrlForm, confirmBuy, emailForm
from btc.models import Profil, sysvar, buyUrls, sellUrls, escrowPayoutLedger
from django.contrib.auth.models import User
import hashlib, sys, random, os, datetime, string, requests, json, re, codecs ,hmac,time,base64,httplib2,robotexclusionrulesparser,lxml
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from django.shortcuts import redirect
from django.shortcuts import HttpResponseRedirect
from django.core.mail import send_mail
from bs4 import BeautifulSoup, SoupStrainer
from pycoin.key.BIP32Node import BIP32Node
from pycoin.key import Key
from pycoin.services import spendables_for_address 
from bitcoin import * 

    

def checkMozDA(url, request):
    expires = int(time.time() + 300)
    access_id = 'mozscape-88e59a4285'
    secret_key = '153ce55bdd872bf1927393a52d48bd30'
    to_sign = '%s\n%i' % (access_id, expires)
    sig = base64.b64encode(hmac.new(secret_key.encode('utf-8'),to_sign.encode('utf-8'),hashlib.sha1).digest())

    sig = str(sig)
    sig = sig.replace("b'",'')
    sig = sig.replace("'",'')
    url =('https://lsapi.seomoz.com/linkscape/url-metrics/%s/?cols=68719476736&limit=1&AccessID=mozscape-88e59a4285&Expires=%s&Signature=%s'
%(url,str(expires), sig))
    DAscore = requests.get(url)
    DAscore = DAscore.text
    DA = re.search(r'"pda":[0-9]{2}', DAscore)
    if DA:
        DA = DA.group(0)
        print(DA)
        DA = str(DA)
        DA = DA.replace('"pda":','')
        print(DA)
        #DA = DA[2:]
        #DA = DA[:-2]
        #print(DA)
        DA = float(DA)
        return DA
    else:
        print("errorrrr##########################")
        price = sysvar.objects.get(pk=1)
        btcPrice = price.btcPrice
        form = sellUrlForm()
        error = "something went wrong, please try again later"
        return error

def getcoinBalance(address):
    spendables = spendables_for_address(address, 'BTC', format="dict") ##for spendable send to address provided by 
    print(spendables)
    placeholder = 0
    for myitem in spendables:
        if myitem['does_seem_spent'] == 0:
            placeholder = placeholder + myitem['coin_value']

    placeholder = placeholder/100000
    return placeholder


def createWithdrawal(bitcoinAddress, amount, profil):
    priv = profil.wif
    print("hhhererere")
    print(priv)
    amount = amount * 100000
    amount = amount - 17600
    amount = int(amount)
    pub = privtopub(priv)
    addr = pubtoaddr(pub) 
    h = history(addr)
    outs = [{'value': amount, 'address': bitcoinAddress}]
    tx = mktx(h,outs)
    tx2 = sign(tx,0,priv)
    tx3 = sign(tx2,0,priv)
    print(tx3)
    r = requests.post('https://blockchain.info/pushtx', data = {'tx':tx3})
    print(r.text)
    print(r.status_code)
    if r.status_code == 200:
        withdrawal = "success!"
        return withdrawal
    else:
        withdrawal = "btc withdrawal failed please contact us if the problem persists"
        return withdrawal


def getBtcPrice():## add an if statement to only search if time.now is 60 minutes old
    price = sysvar.objects.get(pk=1)
    now = timezone.now() 
    if price.timestamp < now:
        url = "http://api.coindesk.com/v1/bpi/currentprice.json"
        response = requests.get(url)
        response = response.text
        m = re.search('Dollar","rate_float":[0-9]{1,5}\.[0-9]{1,5}', response)
        regex = m.group(0)
        btcP = re.search('[0-9]{1,5}\.[0-9]{1,5}', regex)
        btcP = btcP.group(0) 
        price.btcPrice = float(btcP) 
        price.timestamp = timezone.now() + datetime.timedelta(hours=1)
        price.save()
        
    
# Create your views here.

def home_page(request):
    getBtcPrice()
    price = sysvar.objects.get(pk=1)
    btcPrice = price.btcPrice 
    print(request.user)
    return render(request, 'home.html',{'btcPrice':btcPrice}) 
 
def faq_page(request):
    getBtcPrice()
    price = sysvar.objects.get(pk=1)
    btcPrice = price.btcPrice
    return render(request, 'faq_page.html',{'btcPrice':btcPrice}) 

def contact_page(request):
    getBtcPrice()
    price = sysvar.objects.get(pk=1)
    btcPrice = price.btcPrice
    message = ''
    if request.method == 'POST':
        
        emaildata = emailForm(request.POST)
        if emaildata.is_valid():
            fromemail = emaildata.cleaned_data['fromfield']
            subject = emaildata.cleaned_data['subject']
            message = emaildata.cleaned_data['body']            

            send_mail(subject, message, 'con@bl4btc.io', ['con@bl4btc.io'], fail_silently=False)
            message = 'Success!'
        else:    
            message = 'fail'
    form = emailForm()
    return render(request, 'contact_page.html',{'btcPrice':btcPrice,'form':form, 'message':message}) 


def register_page(request, refererUUID):
    getBtcPrice()
    price = sysvar.objects.get(pk=1)
    btcPrice = price.btcPrice
    counter = price.counter
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
                return render(request, 'register_page.html', {'form':registration_form,'username_taken': username_taken,'btcPrice':btcPrice})
            elif User.objects.filter(email=form.cleaned_data['email']).exists():
                email_taken = True
                return render(request, 'register_page.html', {'form':registration_form,'email_taken': email_taken,'btcPrice':btcPrice})
            datas['username']=form.cleaned_data['username']
            datas['email']=form.cleaned_data['email']
            datas['password1']=form.cleaned_data['password1']
            datas['referer']=refererUUID
            #We will generate a random activation key
            s = 'xprv9s21ZrQH143K2Lap6SnULZfdEi4ivcbottMVoY7MaupCQhVLfARkygyW9N7PKsBSPd2gTQXZr1R4iqkLCQ3TUxvs9NvwYRScCVGV8Aos7ad'
            mykey = Key.from_text(s)
            mysub = mykey.subkey(counter)
            address = Key.address(mysub)
            wif = Key.wif(mysub)
            datas['deposit_add']=address
            datas['wif']=wif
            price.counter = price.counter + 1
            price.save()
            salt = hashlib.sha1(str(random.random()).encode('utf-8')).hexdigest()[:5]
            usernamesalt = datas['email']
            
            if isinstance(usernamesalt, str):
                usernamesalt=str.encode(usernamesalt)
            if isinstance(salt, str):
                salt=str.encode(salt)
            print(salt)
            print(usernamesalt)
            datas['activation_key']=hashlib.sha1(salt+usernamesalt).hexdigest()

            datas['email_path']="/home/connell-gough/django/bl4btc/btc/static/ActivationEmail.txt"
            datas['email_subject']="activate your account"

            form.sendEmail(datas) #Send validation email
            form.save(datas) #Save the user and his profile

            request.session['registered']=True #For display purposes
            return render(request, 'register_page.html', {'email_sent':True,'btcPrice':btcPrice})
        else:

            registration_form = form #Display form with error messages (incorrect fields, etc)
    
    
    return render(request, 'register_page.html', {'form':registration_form,'btcPrice':btcPrice,'refererUUID':refererUUID})

def activation(request, key):
    getBtcPrice()
    price = sysvar.objects.get(pk=1)
    btcPrice = price.btcPrice
    activation_expired = False
    already_active = False
    print(key)
    
    print(Profil)
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
    return render(request, 'activation.html', {'activation_expired':activation_expired,'already_active':already_active,'id_user':id_user,'btcPrice':btcPrice})#need to fix this

def new_activation_link(request, user_id):# check if it's the same user and if they are already authed # new email not being sent
    getBtcPrice()
    price = sysvar.objects.get(pk=1)
    btcPrice = price.btcPrice
    form = RegistrationForm()
    datas={}
    user = User.objects.get(username=user_id)
   
    
    if user is not None and not user.is_active:#here
        datas['username']=user.username
        datas['email']=user.email
        datas['email_path']="/home/connell-gough/django/bl4btc/btc/static/ResendEmail.txt"
        datas['email_subject']="activate your account!"

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
        return render(request, 'register_page.html', {'email_sent':True,'btcPrice':btcPrice})
    else:
        return render(request, 'home.html',{'btcPrice':btcPrice})

def reset_password(request): #send email with new password set new password, check if email exists 
    getBtcPrice()
    price = sysvar.objects.get(pk=1)
    btcPrice = price.btcPrice
    email_new_pass = EmailNewPass()
    form = EmailNewPass(request.POST)
    if request.method == 'POST' and form.is_valid():
   
        if User.objects.filter(email=form.cleaned_data['email']).exists() == False:
            email_invalid = True
            return render(request,'passwordsent.html',{'form':email_new_pass, 'email_invalid': email_invalid,'btcPrice':btcPrice})
        N = 12
        password = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(N))
        u = User.objects.get(email=form.cleaned_data['email'])
        u.set_password(password)
        u.save()
        send_mail('new password', 'hello, please log with this password and change it:' + password, 'con@bl4btc.io', [form.cleaned_data['email']], fail_silently=False)
        success = True
        return render(request,'passwordsent.html',{'success': success,'btcPrice':btcPrice})
    
    else: 
        return render(request,'passwordsent.html',{'form':email_new_pass,'btcPrice':btcPrice})

def sign_page(request):
    getBtcPrice()
    price = sysvar.objects.get(pk=1)
    btcPrice = price.btcPrice
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
                    print("User is valid, active and authenticated")
                    login(request, user)
                    profil = Profil.objects.get(user=request.user)
                    
                    
                    return render(request,'home.html',{'btcPrice':btcPrice})
                else:
                    disabled_account = True
                    print("The password is valid, but the account has been disabled! you may need to verify email")
            else:
    # the authentication system was unable to verify the username and password
                print("The username or password were incorrect.")
                incorrect_pass_or_username = True
    return render(request, 'sign_in.html', {'form':sign_in_form, 'disabled_account': disabled_account, 'incorrect':incorrect_pass_or_username,'btcPrice':btcPrice})#add error messages here!!!! 

def logout_view(request):
    getBtcPrice()
    price = sysvar.objects.get(pk=1)
    btcPrice = price.btcPrice
    logout(request)

    return render(request, 'home.html') 



def change_password(request):
    getBtcPrice()
    price = sysvar.objects.get(pk=1)
    btcPrice = price.btcPrice
    successful = False
   
    form = ChangePassForm(request.POST)
    if request.user.is_authenticated() and request.method == 'POST' and form.is_valid():# if password is correct for user, change to new password
        print('post request worked')
 
        datas = {}
        datas['password1']=form.cleaned_data['password1']
        datas['password2']=form.cleaned_data['newpassword1']
        datas['password3']=form.cleaned_data['newpassword2']
        if request.user.check_password(datas['password1']) == True and datas['password2'] == datas['password3']:
            request.user.set_password(datas['password2'])
            successful = True
            request.user.save()
            return render(request, 'change_password.html',{'form':form,'successful':successful,'btcPrice':btcPrice})
        elif request.user.check_password(datas['password1']) == False:
            incorrect_pass = True
            return render(request, 'change_password.html',{'form':form,'successful':successful, 'incorrect_pass':incorrect_pass,'btcPrice':btcPrice})
        else:
            passwords_mismatch = True
            return render(request, 'change_password.html',{'form':form,'successful':successful, 'passwords_mismatch':passwords_mismatch,'btcPrice':btcPrice})            
    else:
        change_pass_form = ChangePassForm()
        return render(request, 'change_password.html',{'form':change_pass_form,'btcPrice':btcPrice})# get error messages to work


def dashboard(request):
    getBtcPrice()
    price = sysvar.objects.get(pk=1)
    btcPrice = price.btcPrice
    form = btcWithdrawalForm()
    if request.user.is_authenticated():
        profil = Profil.objects.get(user=request.user) 
        profil.account_balance = getcoinBalance(profil.deposit_add) - profil.in_escrow
        profil.save()
        if request.method == 'POST':
            form = btcWithdrawalForm(request.POST)
            if form.is_valid():# send email subtract from account balance, send bitcoins create ledger entry
                amount = form.cleaned_data['amount'] 
                bitcoinAddress = form.cleaned_data['btcAddress'] 
                print(bitcoinAddress)
                print(amount)
                if profil.account_balance >= amount:
                    print("made it here")

                    withdrawal = createWithdrawal(bitcoinAddress, amount, profil)
                    if withdrawal == "success!":
                        profil.account_balance = profil.account_balance - amount
                        profil.save()
                    try:
                        domains = sellUrls.objects.filter(user=request.user).values()
                    except sellUrls.DoesNotExist:
                        domains = None
                    try:
                        payouts = escrowPayoutLedger.objects.filter(payeeUUID=profil.myuuid).values()
                    except escrowPayoutLedger.DoesNotExist:
                        payouts = None
                    try:
                        buyerpayouts = escrowPayoutLedger.objects.filter(payerUUID=profil.myuuid).values()
                    except escrowPayoutLedger.DoesNotExist:
                        buyerpayouts = None
                    
                    return render(request, 'dashboard.html',{'btcPrice':btcPrice, 'profil': profil,'form':form, 'domains':domains,'payouts':payouts,'withdrawal':withdrawal,'buyerpayouts':buyerpayouts})
                else:
                    try:
                        domains = sellUrls.objects.filter(user=request.user).values()
                    except sellUrls.DoesNotExist:
                        domains = None
                    try:
                        payouts = escrowPayoutLedger.objects.filter(payeeUUID=profil.myuuid).values()
                
                    except escrowPayoutLedger.DoesNotExist:
                        payouts = None
                    try:
                        buyerpayouts = escrowPayoutLedger.objects.filter(payerUUID=profil.myuuid).values()
                    except escrowPayoutLedger.DoesNotExist:
                        buyerpayouts = None
                    withdrawal = "insufficient funds"
                    return render(request, 'dashboard.html',{'btcPrice':btcPrice, 'profil': profil,'form':form, 'domains':domains,'payouts':payouts,'withdrawal':withdrawal,'buyerpayouts':buyerpayouts})
             
        else:
           
            try:
                domains = sellUrls.objects.filter(user=request.user).values()
            except sellUrls.DoesNotExist:
                domains = None
            try:
                payouts = escrowPayoutLedger.objects.filter(payeeUUID=profil.myuuid).values()
                
            except escrowPayoutLedger.DoesNotExist:
                
                payouts = None
            try:
                buyerpayouts = escrowPayoutLedger.objects.filter(payerUUID=profil.myuuid).values()
            except escrowPayoutLedger.DoesNotExist:
                buyerpayouts = None
            return render(request, 'dashboard.html',{'btcPrice':btcPrice, 'profil': profil,'form':form, 'domains':domains,'payouts':payouts,'buyerpayouts':buyerpayouts})
       
    else:
        sign_in_form = SignInForm()
        return render(request, 'sign_in.html',{'form':sign_in_form,'btcPrice':btcPrice })


def list_unlist(request, link_id):
    getBtcPrice()
    price = sysvar.objects.get(pk=1)
    btcPrice = price.btcPrice
    if request.user.is_authenticated():
        obj = sellUrls.objects.get(pk=link_id)
        username = obj.user
        if request.user.username == username:
            if obj.listed == True:
                obj.listed = False
                obj.save()
                message = "your link has been unlisted"
                return render(request ,'list_unlist.html',{'message':message})
            elif obj.listed == False:
                obj.listed = True
                obj.save()
                message = "your link has been listed" 
                return render(request ,'list_unlist.html',{'message':message})
        else:
            sign_in_form = SignInForm()
            return render(request, 'sign_in.html',{'form':sign_in_form,'btcPrice':btcPrice })
    else:
        sign_in_form = SignInForm()
        return render(request, 'sign_in.html',{'form':sign_in_form,'btcPrice':btcPrice })
      

def sell_links(request):
    getBtcPrice()
    price = sysvar.objects.get(pk=1)
    btcPrice = price.btcPrice
    btcPrice = float(btcPrice)
    form = sellUrlForm()
    if request.user.is_authenticated():## username credits btc withdrawal and btc deposit address
        profil = Profil.objects.get(user=request.user)
        if request.method == 'POST':
            form = sellUrlForm(request.POST)

            if form.is_valid():# check moz score, add to models!!
                #check moz score here with script
                sellUrl = form.cleaned_data['sellUrl']
                subpage = False
                if re.match(r'^([a-z]+\:\/{2})?([\w-]+\.?[\w-]+\.\w+\/?)$', sellUrl) == None:
                    subpage = True   
                tags = form.cleaned_data['tag1'] + ', ' + form.cleaned_data['tag2'] + ', ' + form.cleaned_data['tag3'] + ', ' + form.cleaned_data['tag4'] + ', ' + form.cleaned_data['tag5']
                
                DAscore = checkMozDA(sellUrl, request)# check if subdomain
                if isinstance(DAscore, str):
                    return render(request, 'sell_links.html',{'btcPrice':btcPrice, 'form':form, 'success':DAscore})
                if 0 <= DAscore <= 9:
                    price = float(0.20/btcPrice * 1000)
                    tier = 1
                elif 10 <= DAscore <= 14:
                    price = float(1.0/btcPrice * 1000)
                    tier = 2
                elif 15 <= DAscore <= 19:
                    price = float(2.0/btcPrice * 1000)
                    tier = 3
                elif 20 <= DAscore <= 24:
                    price = float(3.0/btcPrice * 1000)
                    tier = 4
                elif 25 <= DAscore <= 29:
                    price = float(4.0/btcPrice * 1000)
                    tier = 5
                elif 30 <= DAscore <= 34:
                    price = float(6.0/btcPrice * 1000)
                    tier = 6
                elif 35 <= DAscore <= 39:
                    price = float(9.0/btcPrice * 1000)
                    tier = 7
                elif 40 <= DAscore <= 44:
                    price = float(20.0/btcPrice * 1000)
                    tier = 8
                elif 45 <= DAscore <= 100:
                    price = float(30.0/btcPrice * 1000)
                    tier = 9
                else: 
                    return render(request, 'sell_links.html',{'btcPrice':btcPrice, 'form':form, 'success':DAscore}) 
                #fail
                if subpage == True:
                    price = price*0.25# i can test for this on validation
                if sellUrls.objects.filter(user=request.user.username, website=sellUrl).exists():
                    taken = "you have already listed that website!"
                    return render(request, 'sell_links.html',{'btcPrice':btcPrice, 'form':form, 'success':taken}) 
                s = sellUrls(user=request.user.username, website=sellUrl,tags=tags,subpage=subpage,price=price,mozscore=DAscore,listed=True, tier=tier)
                s.save()
                form = sellUrlForm()
                success = "Success!"
                # check moz score with thier api
                return render(request, 'sell_links.html',{'btcPrice':btcPrice, 'form':form, 'success':success}) 
            else:
                try:
                    domains = sellUrls.objects.filter(user=request.user).values()
                except sellUrls.DoesNotExist:
                    domains = None
                return render(request, 'sell_links.html',{'btcPrice':btcPrice,'domains':domains, 'form':form}) 
        else:
            try:
                domains = sellUrls.objects.filter(user=request.user).values()
            except sellUrls.DoesNotExist:
                domains = None
            return render(request, 'sell_links.html',{'btcPrice':btcPrice,'domains':domains, 'form':form}) 
    else:
        sign_in_form = SignInForm()
        return render(request, 'sign_in.html',{'form':sign_in_form,'btcPrice':btcPrice })

def buy_links(request):
    getBtcPrice()
    price = sysvar.objects.get(pk=1)
    btcPrice = price.btcPrice
    form = buyUrlForm()
    if request.user.is_authenticated():## username credits btc withdrawal and btc deposit address
        profil = Profil.objects.get(user=request.user)
        if request.method == 'POST':
            form = buyUrlForm(request.POST)
            if form.is_valid():# check moz score, add to models!!
                #check moz score here with script
                DAscore = form.cleaned_data['mozFilter']
                search = form.cleaned_data['search']
                subPage = form.cleaned_data['subPage']
            
                print(search)
                print(subPage)
                DAscore = int(DAscore)
                print(DAscore)
                if DAscore == 0:
                    tier=0
                elif DAscore == 1:
                    tier=1
                elif DAscore == 2:
                    tier=2
                elif DAscore == 3:
                    tier=3
                elif DAscore == 4:
                    tier=4
                elif DAscore == 5:
                    tier=5
                elif DAscore == 6:
                    tier=6
                elif DAscore == 7:
                    tier=7
                elif DAscore == 8:
                    tier=8
                elif DAscore == 9:
                    tier=9
                else:
                    print("wut")
                if subPage == True:
                    subPage = True
               
                if search == "" and tier==0:
                    print("1")
                    domains = sellUrls.objects.filter(subpage=subPage,listed=True)
                    return render(request, 'buy_links.html',{'btcPrice':btcPrice,'domains':domains, 'form':form})
                elif search == "" and tier != 0:
                    print("2")
                    domains = sellUrls.objects.filter(tier=tier,subpage=subPage,listed=True)
                    return render(request, 'buy_links.html',{'btcPrice':btcPrice,'domains':domains, 'form':form})
                elif search != "" and tier != 0:
                    print("3")
                    domains = sellUrls.objects.filter(tier=tier,subpage=subPage,tags__contains=search,listed=True)
                    return render(request, 'buy_links.html',{'btcPrice':btcPrice,'domains':domains, 'form':form})
                elif search != "" and tier == 0:
                    print("4")
                    domains = sellUrls.objects.filter(subpage=subPage,tags__contains=search,listed=True)
                    return render(request, 'buy_links.html',{'btcPrice':btcPrice,'domains':domains, 'form':form})
                else:
                    print('5')
                    domains = sellUrls.objects.filter(subpage=subPage,listed=True)
                    return render(request, 'buy_links.html',{'btcPrice':btcPrice,'domains':domains, 'form':form})
        else:
            try:
                domains = sellUrls.objects.filter(listed=True)
            except sellUrls.DoesNotExist:
                domains = None
            return render(request, 'buy_links.html',{'btcPrice':btcPrice,'domains':domains, 'form':form})            
                
    else:
        sign_in_form = SignInForm()
        return render(request, 'sign_in.html',{'form':sign_in_form,'btcPrice':btcPrice })


def buy_link_confirmation(request, urluuid):####right heeeererererererere
    getBtcPrice()
    price = sysvar.objects.get(pk=1)
    btcPrice = price.btcPrice
    form = confirmBuy()
    if request.user.is_authenticated():## username credits btc withdrawal and btc deposit address
        profil = Profil.objects.get(user=request.user) 
        if request.method == 'POST':
            form = confirmBuy(request.POST)
            if form.is_valid():
                
        
                profil.account_balance = getcoinBalance(profil.deposit_add) - profil.in_escrow
        
                backlink =  form.cleaned_data['url']
                payerUUID = profil.myuuid
                sellUser = sellUrls.objects.get(urluuid=urluuid)
                price = sellUser.price
                myuser = sellUser.user
                sellUrl = sellUser.website
                p = Profil.objects.get(user=User.objects.get(username=myuser))
                e = User.objects.get(username=request.user)
                email = e.email
                email = [email]
                print(email)
                payeeUUID = p.myuuid
                if price > profil.account_balance:
                    domain = None
                    success = "you do not have enough funds available"
                    return render(request, 'buy_link_confirmation.html',{'btcPrice':btcPrice,'domain':domain,'form':form,'success':success})
                else:
                    
                    profil.in_escrow = profil.in_escrow + price
                    profil.save()
                    timestamp = timezone.now() + datetime.timedelta(days=3)
                    s = escrowPayoutLedger(sellUrlUUID=urluuid,escrow=True,payeeUUID=payeeUUID,payerUUID=payerUUID,backlink=backlink,price=price,timestamp=timestamp,domain=sellUrl)
                    s.save()
                    domain = None
                    success = "success your request has been sent to the seller, if he does not validate in three days your credits will be reimbursed"
                    send_mail('Validation request', "hello you are being requested to deny or validate a link on  http://bl4btc.io/buy_links/", 'con@bl4btc.io', email ,fail_silently=False) 
                    return render(request, 'buy_link_confirmation.html',{'btcPrice':btcPrice,'domain':domain,'form':form,'success':success})
            ## create ledger here, send email, add to dashboard, subtract from account balance
            else:
                try:
                    domain = sellUrls.objects.filter(urluuid=urluuid,listed=True)
                except sellUrls.DoesNotExist:
                    domain = None
                return render(request, 'buy_link_confirmation.html',{'btcPrice':btcPrice,'domain':domain,'form':form})
        else:
            try:
                domain = sellUrls.objects.filter(urluuid=urluuid,listed=True)
            except sellUrls.DoesNotExist:
                domain = None
            return render(request, 'buy_link_confirmation.html',{'btcPrice':btcPrice,'domain':domain,'form':form})
    else:
        sign_in_form = SignInForm()
        return render(request, 'sign_in.html',{'form':sign_in_form,'btcPrice':btcPrice })
    

def validate(request, UUID, var):
    getBtcPrice()
    price = sysvar.objects.get(pk=1)
    btcPrice = price.btcPrice 
    if request.user.is_authenticated():## username credits btc withdrawal and btc deposit address
        profil = Profil.objects.get(user=request.user) 

        p = escrowPayoutLedger.objects.get(ledgerUUID=UUID)
        timestamp = p.timestamp
        backlink = p.backlink
        payerUUID = p.payerUUID
        now = timezone.now()
        url = sellUrls.objects.get(urluuid=p.sellUrlUUID)
        url = url.website
       
        var = int(var)
        if var == 1:
            seoaPass(request, url)
            http = httplib2.Http() 
            status, response = http.request(url)

            soup = BeautifulSoup(response,'lxml')
            for link in soup.find_all('a'):
               
                
                
                if link.get('href') == backlink:
                    
                    
                    p.timestampofval = now
                    p.timestampofval30 = now + datetime.timedelta(days=30)
                    message = "success, I will check randomly throughout the next thirty days to make sure you are still hosting this link"
                    p.validated = True
                    p.save()
                    return render(request, 'validate.html', {'message':message,'btcPrice':btcPrice })
            message = "the backlink could not be found on your page please check to make sure it's there and try again" 
            return render(request, 'validate.html', {'message':message,'btcPrice':btcPrice })
        #go to website with uuid check for backlink in payoutescrowledger then change the time stamps, three day time limit
        
        else: 
            # send account balance back 
            profil = Profil.objects.get(myuuid=payerUUID)
            profil.in_escrow = profil.in_escrow - p.price
            profil.save()
            message = "the request has been denied and the ledger object in my database deleted" 
            escrowPayoutLedger.objects.filter(ledgerUUID=UUID).delete()
            return render(request, 'validate.html',{'message':message,'btcPrice':btcPrice })
    else:
        sign_in_form = SignInForm()
        return render(request, 'sign_in.html',{'form':sign_in_form,'btcPrice':btcPrice })
             
    
    ## change timestamps in escrowPayoutLedger, check for backlink, or delete; redirect to dashboard

def seoaPass(request, url):
    getBtcPrice()
    price = sysvar.objects.get(pk=1)
    btcPrice = price.btcPrice


    robotsUrl = re.findall(r'.*[.][a-zA-Z]{2,3}', url)
    robotsUrl = str(robotsUrl[0])
    robotsUrltxt = robotsUrl + '/robots.txt'
    rerp = robotexclusionrulesparser.RobotExclusionRulesParser()
    print(robotsUrltxt)
    print(url)
    try:
        rerp.fetch(robotsUrltxt)
        if rerp.is_allowed("hello this is https://bl4btc.io", url):
            print("true")
            return True
        else:
            message = "your robots.txt disallows indexing bots from visiting your url" 
            return render(request, 'validate.html',{'message':message,'btcPrice':btcPrice })
    
            
    except:
        return False




