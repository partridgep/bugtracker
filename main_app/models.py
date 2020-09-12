from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.CharField(max_length=254)


class Project(models.Model):
    name = models.CharField(max_length=50)
    teammates = models.ManyToManyField(User)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('project_detail', kwargs={'project_id': self.id})

class Bug(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField(max_length=500)
    file_name = models.CharField(max_length=50)
    resolved = models.BooleanField(default=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    # mark as new bug for users
    seen_by = models.ManyToManyField(User, related_name='seen_by_bug_set')
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('bug_detail', kwargs={'bug_id': self.id})

class Comment(models.Model):
    text = models.TextField(max_length=500)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bug = models.ForeignKey(Bug, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text

    class Meta:
        ordering = ['created_at']


class Screenshot(models.Model):
    url = models.CharField(max_length=200)
    bug = models.ForeignKey(Bug, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Screenshot for bug_id: {self.bug_id} @{self.url}"

    class Meta:
        ordering = ['created_at']

