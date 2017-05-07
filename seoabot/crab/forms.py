from django import forms
import datetime



class URLForm(forms.Form):
    url = forms.URLField(max_length=255, required = True)
