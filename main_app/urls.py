from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('account/signup', views.signup, name='signup'),
    path('projects/', views.projects_index, name='index'),
    path('projects/create/', views.add_project, name='project_create'),
    path('projects/<int:project_id>/', views.project_detail, name='project_detail'),
    path('projects/<int:project_id>/add_teammates', views.add_teammates, name='add_teammates'),
    path('bugs/create/<int:project_id>/', views.add_bug_to_project, name='project_bug_create'),
    path('bugs/<int:bug_id>/resolve/', views.resolve_bug, name='resolve_bug'),
    path('bugs/<int:bug_id>/add_screenshot/', views.add_screenshot, name='add_screenshot'),
    path('bugs/<int:bug_id>/add_comment/', views.add_comment, name='add_comment'),
    path('bugs/<int:bug_id>/', views.bug_detail, name='bug_detail'),
]