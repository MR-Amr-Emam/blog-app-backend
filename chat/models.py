from django.db import models
from asgiref.sync import sync_to_async
# Create your models here.
from rest_framework import serializers
from rest_framework_simplejwt.authentication import JWTAuthentication


class MsgChat(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    msg = models.CharField(max_length=200)
    user_from = models.ForeignKey("authentication.User", related_name="msgs", on_delete=models.DO_NOTHING)
    user_to = models.ForeignKey("authentication.User", related_name="received_msgs", on_delete=models.DO_NOTHING)

class MsgChatSerializer(serializers.ModelSerializer):
    user_id = serializers.SerializerMethodField()
    def get_user_id(self, obj):
        return obj.user_from.id
    class Meta:
        model = MsgChat
        fields = ["date", "msg", "user_id"]

class CookiesAuthWS:
    def __init__(self, app):
        self.app = app
        
    async def __call__(self, scope, receive, send):
        user = scope.get("user")
        if(user and user.is_authenticated):
            return await self.app(scope, receive, send)
        raw_token = scope.get("cookies").get("access_token")
        if raw_token is None:
            return await self.app(scope, receive, send)
        jwt_auth_obj = JWTAuthentication()
        try:
            token = jwt_auth_obj.get_validated_token(raw_token)
        except:
            return await self.app(scope, receive, send)
        
        
        scope["user"] = await sync_to_async(jwt_auth_obj.get_user)(token)
        return await self.app(scope, receive, send)