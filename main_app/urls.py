from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('account/signup', views.signup, name='signup'),
    path('projects/', views.projects_index, name='index'),
    path('projects/create/', views.add_project, name='project_create'),
    path('projects/<int:project_id>/', views.project_detail, name='project_detail'),
]