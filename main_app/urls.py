from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('account/signup', views.signup, name='signup'),
    path('projects/', views.projects_index, name='index'),
]