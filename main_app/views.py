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

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

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


def generate_username(email):
    username = email.split('@')[0]
    try:
      user_with_existing_username = User.objects.get(username = username)
      print(f'user with existing username = {user_with_existing_username}')
      if user_with_existing_username:
        username += '1'
    except:
      pass
    return username

@login_required
def add_project(request):
    # get all projects
    projects = Project.objects.filter(teammates=request.user)

    # if submitting the form
    if request.method == "POST":
      # create project in database
      project_name = request.POST.get("pname")
      p = Project(name=project_name)
      p.save()

      # add current user as teammate
      current_user = request.user
      p.teammates.add(current_user)
      p.save()

      print(request.POST.get("teammates"))
      # get string with all emails
      emailStr = request.POST.get("teammates")
      # separate emails
      emails = emailStr.split(", ")
      print(emails)
      # find ALL users in database
      users_already_signed_up = User.objects.all()
      # see if any match the list of emails
      found_users = User.objects.filter(email__in = emails)
      print(found_users)

      for user in found_users:
        # send invite email to all found users
        msg_plain = render_to_string('emails/added_to_project.txt', {'project_name': project_name})
        msg_html = render_to_string('emails/added_to_project.html', {'project_name': project_name})
        send_mail(
        f'BugTracker: You\'ve been invited to {project_name}',
        msg_plain,
        settings.EMAIL_HOST_USER,
        [f'{user.email}'],
        html_message=msg_html,
        fail_silently=False,
        )
        # add user to project
        user_object = User.objects.get(email=user.email)
        p.teammates.add(user_object)
        p.save()
        # finally remove email from list of emails
        emails.remove(user.email)

      if len(emails) and emails[0] != '':
        # remaining emails will be new users
        for email in emails:
          # create new user
          random_password = User.objects.make_random_password()
          generated_username = generate_username(email)
          new_user = User.objects.create_user(generated_username, email, random_password)
          new_user.save()
          # send invite email
          msg_plain = render_to_string('emails/new_user_email.txt', {'project_name': project_name, 'username': generated_username, 'password': random_password})
          msg_html = render_to_string('emails/new_user_email.html', {'project_name': project_name, 'username': generated_username, 'password': random_password})
          send_mail(
          f'BugTracker: You\'ve been invited to {project_name}',
          msg_plain,
          settings.EMAIL_HOST_USER,
          [f'{email}'],
          html_message=msg_html,
          fail_silently=False,
          )
          # add new user to project
          new_user_object = User.objects.get(email=email)
          p.teammates.add(new_user_object)
          p.save()

      # redirect to project page
      return redirect('project_detail', project_id=p.id)

    # if GET request, show the form
    return render(request, 'projects/create.html', {'projects': projects})

@login_required
def project_detail(request, project_id):
    projects = Project.objects.filter(teammates=request.user)
    project = Project.objects.get(id=project_id)
    return render(request, 'projects/detail.html', {
        'project': project,
        'projects': projects
    })