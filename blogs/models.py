import os

from django.db import models
from django.core.exceptions import ValidationError


def validate_file_extension(value):
    """
    Custom validator to check the file extension of an uploaded file.
    """
    if(not value):
        pass
    ext = os.path.splitext(value.name)[1]  # Get the file extension
    valid_extensions = ['.mp4'] # Define allowed extensions
    if not ext.lower() in valid_extensions:
        raise ValidationError('Unsupported file extension.')


class Blog(models.Model):
    user = models.ForeignKey(to="authentication.User", on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    is_video = models.BooleanField(default=False)
    category = models.ForeignKey(to="blogs.category", on_delete=models.DO_NOTHING, null=True, blank=True)
    image = models.ImageField()
    video = models.FileField(null=True, blank=True, validators=[validate_file_extension])
    title = models.CharField(max_length=70)
    description = models.CharField(max_length=200)
    likes_number = models.IntegerField(default=0)
    views_number = models.IntegerField(default=0)
    liked_people = models.ManyToManyField(to="authentication.User", related_name="liked_blogs", blank=True)
    viewed_people = models.ManyToManyField(to="authentication.User", related_name="viewed_blogs", blank=True)
    for_group = models.BooleanField(default=False)
    group = models.ForeignKey(to="groups.Group", on_delete=models.DO_NOTHING, null=True)


    def clean(self):
        super().clean()
        if(self.is_video and (not self.video)):
            raise ValidationError("must uplaod a video")
        if(self.for_group and (not self.group)):
            raise ValidationError("must set a group")
        

class Section(models.Model):
    blog = models.ForeignKey(to=Blog, on_delete=models.CASCADE)
    image = models.ImageField(null=True)
    content = models.TextField(null=False)

class Comment(models.Model):
    user = models.ForeignKey(to="authentication.User", on_delete=models.CASCADE)
    blog = models.ForeignKey(to=Blog, on_delete=models.CASCADE)
    for_comment = models.BooleanField(default=False)
    parent_comment = models.ForeignKey(to="self", on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    content = models.TextField(null=False, blank=False)
    likes = models.ManyToManyField(to="authentication.User", blank=True, related_name="liked_comments")

    def clean(self):
        super().clean()
        if(self.for_comment and (not self.parent_comment)):
            raise ValidationError("must have a parent comment")

class Category(models.Model):
    category = models.CharField(max_length=50)

"""
for shell

from authentication.models import User
from blogs.models import Blog
from blogs.serializers import BlogSerializer
import datetime
blog = Blog.objects.get(id=1)
amr = User.objects.get(id=1)
blog_data = BlogSerializer(instance=blog)   

user = {"id":1, "username":"amrrr", "profile_image":None}
sections = [{"image":None, "content":"that is content"}]

data = {"user":user, "date":datetime.datetime.now(), "category":None, "image":amr.profile_image, "title":"that is title for blog two", "description":"that is descriptiton", "section_set":sections}
serializer = BlogSerializer(data=data)

"""