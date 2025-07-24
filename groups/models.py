import os

from django.db import models


def user_images_dir(instance, filename):
    return os.path.join("groups",instance.name,filename)

default_user_images_dir = os.path.join("users","amr","amr.jpg")


class Group(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=250)
    image = models.ImageField(default=default_user_images_dir, upload_to=user_images_dir)
    members = models.ManyToManyField(to="authentication.User", through="JoinRequest")


class JoinRequest(models.Model):
    group = models.ForeignKey(to="groups.Group", on_delete=models.CASCADE)
    member = models.ForeignKey(to="authentication.User", on_delete=models.CASCADE)
    admin = models.BooleanField(default=False)
    status = models.BooleanField(default=False)


class Invite(models.Model):
    inviter = models.ForeignKey("authentication.user", related_name="inviting", on_delete=models.CASCADE)
    invited = models.ForeignKey("authentication.User", related_name="invited", on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)


"""
for shell

from django.db.models import Q
from authentication.models import User
from groups.models import Group, JoinRequest, Invite
import datetime
amr = User.objects.get(id=1)
from groups.serializers import UserSerializer, GroupSerializer
from blogs.models import Blog

data = {
    "name":"that is name",
    "description":"that is description",
    "members":[1],
}

"""