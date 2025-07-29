from PIL import Image, ImageOps

from django.core.files import File
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ObjectDoesNotExist
from django.apps import apps

from rest_framework import authentication
from rest_framework_simplejwt.authentication import JWTAuthentication

import os, io

def user_images_dir(instance, filename):
    return os.path.join("users",instance.username,filename)


default_user_images_dir = os.path.join("default","profile_image.png")


### custom friends object
class Friends:
    def __init__(self, friends, friends_request, user_requests):
        self.friends, self.friends_requests, self.user_requests = friends, friends_request, user_requests

class User(AbstractUser):
    bio = models.CharField(max_length=100, null=True, blank=True)
    profile_image = models.ImageField(upload_to=user_images_dir, default=default_user_images_dir)
    background_image = models.ImageField(upload_to=user_images_dir, default=default_user_images_dir)
    friends_number = models.IntegerField(default=0)
    friends = models.ManyToManyField("self", through="FriendShip", related_name="friends_set", symmetrical=False)

    def get_friends(self, own_user=False):
        friends = (self.friends.filter(friends2__user1=self, friends2__user1_status=True, friends2__user2_status=True) | 
                self.friends_set.filter(friends1__user2=self, friends1__user1_status=True, friends1__user2_status=True))
        friends_requests = []
        user_requests = []
        if(own_user):
            friends = friends.annotate(unseens=models.Count("msgs", filter=models.Q(msgs__user_to=self, msgs__viewed=False)))
            friends = friends.order_by("-unseens")
            friends_requests = (self.friends.filter(friends2__user1=self, friends2__user1_status=False, friends2__user2_status=True) | 
                    self.friends_set.filter(friends1__user2=self, friends1__user1_status=True, friends1__user2_status=False))

            user_requests = (self.friends.filter(friends2__user1=self, friends2__user1_status=True, friends2__user2_status=False) | 
                    self.friends_set.filter(friends1__user2=self, friends1__user1_status=False, friends1__user2_status=True))

        return Friends(friends, friends_requests, user_requests)
    
    def save(self, *args, **kwargs):
        if self.profile_image.file.size >= 1024*512:
            image = ImageOps.exif_transpose(Image.open(self.profile_image.file)).convert("RGB")
            bytes = io.BytesIO()
            image.save(bytes, format="jpeg", quality=40, optimize=True)
            image = File(bytes, name=self.profile_image.name)
            self.profile_image = image

        if self.background_image.file.size >= 1024*512:
            image = ImageOps.exif_transpose(Image.open(self.background_image.file)).convert("RGB")
            bytes = io.BytesIO()
            image.save(bytes, format="jpeg", quality=40, optimize=True)
            image = File(bytes, name=self.background_image.name)
            self.background_image = image

        return super().save(*args, **kwargs)
            
            
#### custom friendship manager
class FriendShipManager(models.Manager):
    def get_friend_ship(self, user1, user2):
        return self.get(models.Q(user1=user1, user2=user2)|models.Q(user1=user2, user2=user1))
        


class FriendShip(models.Model):
    user1 = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name="friends1")
    user2 = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name="friends2")
    user1_status = models.BooleanField(default=True)
    user2_status = models.BooleanField(default=False)
    objects = FriendShipManager()

    def is_requesting(self, user):
        if(user==self.user1):
            return self.user1_status
        elif(user==self.user2):
            return self.user2_status
        else:
            raise ObjectDoesNotExist()
    

    def save(self, *args, **kwargs):
        try:
            old_obj = FriendShip.objects.get(id=self.id)
            if not(old_obj.user1_status and old_obj.user2_status) and (self.user1_status and self.user2_status):
                self.user1.friends_number+=1
                self.user2.friends_number+=1
            elif not(self.user1_status and self.user2_status) and (old_obj.user1_status and old_obj.user2_status):
                self.user1.friends_number-=1
                self.user2.friends_number-=1
        except FriendShip.DoesNotExist:
            if(self.user1_status and self.user2_status):
                self.user1.friends_number+=1
                self.user2.friends_number+=1
        self.user1.save()
        self.user2.save()

        return super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        if self.user1_status and self.user2_status:
            self.user1.friends_number-=1
            self.user2.friends_number-=1
            self.user1.save()
            self.user2.save()
        return super().delete(*args, **kwargs)





class JWTAuthenticationCookies(authentication.BaseAuthentication):
    def authenticate(self, request):
        raw_token = request.COOKIES.get("access_token")
        if(raw_token is None):
            return None
        jwt_auth_obj = JWTAuthentication()
        try:
            token = jwt_auth_obj.get_validated_token(raw_token)
        except:
            return None
        user = jwt_auth_obj.get_user(token)
        return (user, None)
    