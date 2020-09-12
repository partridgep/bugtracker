from django.contrib import admin
from .models import Project, Bug, Screenshot, Comment

# Register your models here.
admin.site.register(Project)
admin.site.register(Bug)
admin.site.register(Screenshot)
admin.site.register(Comment)
