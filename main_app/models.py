from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Project(models.Model):
    name = models.CharField(max_length=50)
    teammates = models.ManyToManyField(User)

    def __str__(self):
        return self.name

class Bug(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField(max_length=500)
    file_name = models.CharField(max_length=50)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Comment(models.Model):
    text = models.TextField(max_length=500)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bug = models.ForeignKey(Bug, on_delete=models.CASCADE)

    def __str__(self):
        return self.text


class Screenshot(models.Model):
    url = models.CharField(max_length=200)
    bug = models.ForeignKey(Bug, on_delete=models.CASCADE)

    def __str__(self):
        return f"Screenshot for bug_id: {self.bug_id} @{self.url}"

