from django import forms
from django.core.validators import EmailValidator, URLValidator
from django.template import Context, Template
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.models import User
from btc.models import Profil
import datetime
from django.utils import timezone
import re 
from django.core.exceptions import ValidationError
from nocaptcha_recaptcha.fields import NoReCaptchaField


class RegistrationForm(forms.Form):
    username = forms.CharField(required=True,label="",widget=forms.TextInput(attrs={'id':'username_input','placeholder': 'username','class':'form-control input-perso'}),max_length=30,min_length=3)#,validators=[isValidUsername, validators.validate_slug])
    email = forms.EmailField(required=True,label="",widget=forms.EmailInput(attrs={'placeholder': 'Email','class':'form-control input-perso','id':'email_input'}),max_length=100,error_messages={'invalid': ("Email invalid")},validators=[EmailValidator])
    password1 = forms.CharField(required=True,label="",max_length=50,min_length=6,widget=forms.PasswordInput(attrs={'placeholder': 'choose a password','class':'form-control input-perso', 'id':'password1'}))
    password2 = forms.CharField(required=True,label="",max_length=50,min_length=6,widget=forms.PasswordInput(attrs={'placeholder': 'confirm password','class':'form-control input-perso','id':'password2'}))
    captcha = NoReCaptchaField()



    #Override of clean method for password check
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if not password2:
            raise forms.ValidationError("You must confirm your password")
        if password1 != password2:
            raise forms.ValidationError("Your passwords do not match")
        return password2

    #Override of save method for saving both User and Profil objects
    def save(self, datas):
        u = User.objects.create_user(datas['username'],
                                     datas['email'],
                                     datas['password1'])
        
        u.is_active = False
        u.save()
        profil=Profil()
        profil.user=u
        profil.referer=datas['referer']
        profil.deposit_add=datas['deposit_add']
        profil.wif=datas['wif']
        profil.activation_key=datas['activation_key']
        profil.key_expires=timezone.now() + datetime.timedelta(days=1)
        
        profil.save()
        return u

    #Handling of activation email sending ------>>>!! Warning : Domain name is hardcoded below !!<<<------
    #I am using a text file to write the email (I write my email in the text file with templatetags and then populate it with the method below)
    def sendEmail(self, datas):
        link="http://bl4btc.io/activate/"+datas['activation_key']
        c=Context({'activation_link':link,'email':datas['email']})
        f = open(datas['email_path'], 'r')
        t = Template(f.read())
        f.close()
        message=t.render(c)
        #print unicode(message).encode('utf8')
        
        send_mail(datas['email_subject'], message, 'con@bl4btc.io', [datas['email']], fail_silently=False)


class SignInForm(forms.Form):
    username = forms.CharField(required=True,label="",widget=forms.TextInput(attrs={'id':'username_input','placeholder': 'username','class':'form-control input-perso'}),max_length=30,min_length=3)#,validators=[isValidUsername, validators.validate_slug])
    password1 = forms.CharField(required=True,label="",max_length=50,min_length=6,widget=forms.PasswordInput(attrs={'placeholder': 'choose a password','class':'form-control input-perso', 'id':'password_input'}))
    #captcha = NoReCaptchaField()

class ChangePassForm(forms.Form):
    password1 = forms.CharField(required=True,label="",max_length=50,min_length=6,widget=forms.PasswordInput(attrs={'placeholder': 'choose a password','class':'form-control input-perso', 'id':'password_input1'}))
    newpassword1 = forms.CharField(required=True,label="",max_length=50,min_length=6,widget=forms.PasswordInput(attrs={'placeholder': 'choose a password','class':'form-control input-perso', 'id':'password_input2'}))
    newpassword2 = forms.CharField(required=True,label="",max_length=50,min_length=6,widget=forms.PasswordInput(attrs={'placeholder': 'choose a password','class':'form-control input-perso', 'id':'password_input3'}))
    captcha = NoReCaptchaField()


class EmailNewPass(forms.Form):
    email = forms.EmailField(required=True,label="",widget=forms.EmailInput(attrs={'placeholder': 'Email','class':'form-control input-perso','id':'email_input'}),max_length=100,error_messages={'invalid': ("Email invalid")},validators=[EmailValidator])
    captcha = NoReCaptchaField()

MOZNUMBERS = (  
    (0, 'Any'),
    (1, '0-9'),
    (2, '10-14'),
    (3, '15-19'),
    (4, '20-24'),
    (5, '25-29'),
    (6, '30-34'),
    (7, '35-39'),
    (8, '40-44'),
    (9, '45-100'),
)

class buyUrlForm(forms.Form):
    mozFilter = forms.ChoiceField(required=False,label="",initial=0,choices=MOZNUMBERS)
    search = forms.CharField(required=False,label="",widget=forms.TextInput(attrs={'id':'username_input','placeholder': 'search tags','class':'form-control input-perso'}),max_length=30,min_length=3)
    subPage = forms.BooleanField(required=False, initial=False)

class confirmBuy(forms.Form):
    url = forms.URLField(required=True, error_messages={'invalid': ("Invalid Url")}, validators=[URLValidator],widget=forms.TextInput(attrs={'placeholder': 'URL','id':'url_input'} ))
    
    
    

class sellUrlForm(forms.Form):
    sellUrl = forms.URLField(required=True, error_messages={'invalid': ("Invalid Url")}, validators=[URLValidator],widget=forms.TextInput(attrs={'id':'sell_url_input','placeholder' : "your domain's url"} ))
    tag1 = forms.CharField(required=False,label="",widget=forms.TextInput(attrs={'id':'tag','placeholder': 'tag1','class':'form-control'}),max_length=30,min_length=3)
    tag2 = forms.CharField(required=False,label="",widget=forms.TextInput(attrs={'id':'tag','placeholder': 'tag2','class':'form-control input-perso'}),max_length=30,min_length=3)
    tag3 = forms.CharField(required=False,label="",widget=forms.TextInput(attrs={'id':'tag','placeholder': 'tag3','class':'form-control input-perso'}),max_length=30,min_length=3)
    tag4 = forms.CharField(required=False,label="",widget=forms.TextInput(attrs={'id':'tag','placeholder': 'tag4','class':'form-control input-perso'}),max_length=30,min_length=3)
    tag5 = forms.CharField(required=False,label="",widget=forms.TextInput(attrs={'id':'tag','placeholder': 'tag5','class':'form-control input-perso'}),max_length=30,min_length=3)
    captcha = NoReCaptchaField()



class btcWithdrawalForm(forms.Form):
    amount = forms.FloatField(required=True,label="",widget=forms.NumberInput(attrs={'id':'username_input','placeholder': 'amount','class':'form-control input-perso'}))  
    btcAddress = forms.CharField(required=True,label="",widget=forms.TextInput(attrs={'id':'username_input','placeholder': 'btc address','class':'form-control input-perso'}),max_length=34,min_length=26)  
    captcha = NoReCaptchaField()
    
    #def clean(self):
        #cleaned_data = super(btcWithdrawalForm, self).clean()
        #btc_re = (r'^[13][a-km-zA-HJ-NP-Z0-9]{26,33}$')
        #btcAddress = cleaned_data.get('btcAddress')

        #try:
         #   if re.match(r'^[13][a-km-zA-HJ-NP-Z0-9]{26,33}$', btcAddress) == None:
        #        raise ValidationError("invalid btc address")
        #except:
        #    raise ValidationError("invalid btc address")


class emailForm(forms.Form):
    fromfield = forms.CharField(required=True,label="",widget=forms.TextInput(attrs={'id':'emailform','placeholder': 'Your email','class':'form-control input-perso'}),max_length=50,min_length=3)
    subject = forms.CharField(required=True,label="",widget=forms.TextInput(attrs={'id':'emailform','placeholder': 'Subject','class':'form-control input-perso'}),max_length=50,min_length=3)
    body = forms.CharField(required=True,label="",widget=forms.Textarea(attrs={'id':'message','placeholder': 'message','class':'form-control input-perso'}),min_length=3)
  




