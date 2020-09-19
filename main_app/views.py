from django.shortcuts import render, redirect
from .models import Project, Bug, Screenshot
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from .forms import SignUpForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

import uuid
import boto3

from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

S3_BASE_URL = "https://pp-bugtracker.s3.amazonaws.com/"
BUCKET = "pp-bugtracker"

# HELPER FUNCTION

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


# VIEWS

def home(request):
  return redirect('index')

def signup(request):
    error_message = ''
    if request.method == 'POST':
        print(request.POST)
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
    unresolved_bugs = []
    resolved_bugs = []
    for project in projects:
      for bug in project.bug_set.all():
        if bug.resolved == False:
          unresolved_bugs.append(bug)
        else:
          resolved_bugs.append(bug)
    return render(request, 'projects/index.html', {
      'projects': projects, 
      'unresolved_bugs': unresolved_bugs,
      'resolved_bugs': resolved_bugs
      })

@login_required
def add_teammates(request, project_id):
    projects = Project.objects.filter(teammates=request.user)
    project = Project.objects.get(id=project_id)
    user = current_user = request.user
    teammates = []
    for teammate in project.teammates.all():
      if teammate.id != user.id:
        teammates.append(teammate)

    # if submitting the form
    if request.method == "POST":
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
        msg_plain = render_to_string('emails/added_to_project.txt', {'project_name': project.name})
        msg_html = render_to_string('emails/added_to_project.html', {'project_name': project.name})
        send_mail(
        f'BugTracker: You\'ve been added to {project.name}',
        msg_plain,
        settings.EMAIL_HOST_USER,
        [f'{user.email}'],
        html_message=msg_html,
        fail_silently=False,
        )
        # add user to project
        user_object = User.objects.get(email=user.email)
        project.teammates.add(user_object)
        project.save()
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
          msg_plain = render_to_string('emails/new_user_email.txt', {'project_name': project.name, 'username': generated_username, 'password': random_password})
          msg_html = render_to_string('emails/new_user_email.html', {'project_name': project.name, 'username': generated_username, 'password': random_password})
          send_mail(
          f'BugTracker: You\'ve been invited to {project.name}',
          msg_plain,
          settings.EMAIL_HOST_USER,
          [f'{email}'],
          html_message=msg_html,
          fail_silently=False,
          )
          # add new user to project
          new_user_object = User.objects.get(email=email)
          project.teammates.add(new_user_object)
          project.save()

          # redirect to project page
          return redirect('project_detail', project_id=project.id)

    # if GET request, show the form
    return render(request, 'projects/add_teammates.html', {
      'project': project,
      'projects': projects
      })




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
    does_have_teammates = project.teammates.all().count() > 1
    current_user = request.user
    print(project.teammates.all())
    return render(request, 'projects/detail.html', {
        'project': project,
        'does_have_teammates': does_have_teammates,
        'current_user': current_user,
        'projects': projects
    })

@login_required
def add_bug_to_project(request, project_id):
    projects = Project.objects.filter(teammates=request.user)
    project = Project.objects.get(id=project_id)
    user = request.user

    # if submitting the form
    if request.method == "POST":
      # create project in database
      title = request.POST.get("bug_title")
      description = request.POST.get("description")
      file_name = request.POST.get("file_name")
      bug = Bug(title=title, description=description, file_name=file_name, project=project, user=user)
      bug.save()
      # print(bug.seen_by_bug_set.all())

      # redirect to bug detail page
      return redirect('bug_detail', bug_id=bug.id)

    # if GET request, show the form
    return render(request, 'bugs/create_project_bug.html', {'project': project, 'projects': projects})

@login_required
def bug_detail(request, bug_id):
  projects = Project.objects.filter(teammates=request.user)
  bug = Bug.objects.get(id=bug_id)
  user = request.user
  return render(request, 'bugs/detail.html', {
    'bug': bug,
    'projects': projects
  })

@login_required
def resolve_bug(request, bug_id):
  projects = Project.objects.filter(teammates=request.user)
  # would be good to log who resolved it
  # user = request.user
  bug = Bug.objects.get(id=bug_id)
  bug.resolved = True
  bug.save()
  return redirect('bug_detail', bug_id=bug_id)

@login_required
def add_screenshot(request, bug_id):
  projects = Project.objects.filter(teammates=request.user)
  user = request.user
  bug = Bug.objects.get(id=bug_id)
  photo_file = request.FILES.get('photo-file', None)
  if photo_file:
    s3 = boto3.client('s3')
    key = uuid.uuid4().hex[:6] + photo_file.name[photo_file.name.rfind('.'):]
    try:
        s3.upload_fileobj(photo_file, BUCKET, key)
        url = f"{S3_BASE_URL}{key}"
        screenshot = Screenshot(url=url, bug_id=bug_id, user_id=user.id)
        screenshot.save()
    except ClientError as e:
        logging.error(e)
        print(e)
  return redirect('bug_detail', bug_id=bug_id)

@login_required
def add_comment(request, bug_id):
  projects = Project.objects.filter(teammates=request.user)
  user = request.user
  bug = Bug.objects.get(id=bug_id)
  text = request.POST.get("text")
  print(text)
  bug.comment_set.create(text=text, user_id=user.id)
  bug.save()
  return redirect('bug_detail', bug_id=bug_id)
