from django.db import models
from django.contrib.auth.models import AbstractUser

from rest_framework import authentication
from rest_framework import exceptions
from rest_framework_simplejwt.authentication import JWTAuthentication


class User(AbstractUser):
    pass





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