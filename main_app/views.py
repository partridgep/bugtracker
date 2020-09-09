from django.shortcuts import render, redirect
from .models import Project
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from .forms import SignUpForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

def home(request):
  return redirect('index')

def signup(request):
    error_message = ''
    if request.method == 'POST':
         # Create a user form object
         # that includes data from the browser
        form = SignUpForm(request.POST)
        if form.is_valid():
            # add user to database
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('index')
        else:
            error_message = 'Invalid sign up, try again!'
    # either a bad POST request, or a GET request
    # just render the empty form
    form = SignUpForm()
    context = {'form': form, 'error_message': error_message}
    return render(request, 'registration/signup.html', context)

@login_required
def projects_index(request):
    projects = Project.objects.filter(teammates=request.user)
    return render(request, 'projects/index.html', {'projects': projects})

def add_project(request):
    if request.method == "POST":
      print(request.POST.get("teammates"))
      emailStr = request.POST.get("teammates")
      emails = emailStr.split(", ")
      print(emails)
      users_already_signed_up = User.objects.all()
      found_users = User.objects.filter(email__in = emails)
      print(found_users)
      for user in found_users:
        emails.remove(user.email)


    

    return render(request, 'projects/create.html')

