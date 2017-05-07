from django.shortcuts import render
from crab.forms import URLForm
import crab.seoaScript as seoaScript



def home(request):
    if request.method == 'POST': # If the form has been submitted...
        form = URLForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass

            cleanForm = form.cleaned_data
            url = cleanForm['url']
            workingd = seoaScript.controller(url)
            
            if not workingd:
                workingd = {'no links found':''}
                return render(request, 'home.html', {'form': form, 'workingd': workingd}) 
            form = URLForm()
            return render(request, 'home.html', {'form': form, 'workingd': workingd}) 
        else:
            form = URLForm() 
    else:
        form = URLForm()
    return render(request, 'home.html', {'form': form})  

def about(request):
    return render(request, 'about.html')  

def robots(request):
    return render(request, 'robot.html')  
