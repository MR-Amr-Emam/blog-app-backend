from django.conf import settings
from django.apps import apps
from rest_framework import serializers
from .models import User


MsgChat = apps.get_model("chat", "MsgChat")

class blogs_number_func:
    requires_context = True

    def __call__(self, serializer_field):
        return (serializer_field.context["request"].user.blog_set.count())

class UserProfSerializer(serializers.ModelSerializer):
    friend_status = serializers.IntegerField(required=False, read_only=True)
    blogs_number = serializers.IntegerField(read_only=True, default=blogs_number_func())
    class Meta:
        model = User
        fields = ["id", "username", "bio", "profile_image", "background_image", "friends_number",
                  "blogs_number", "friend_status", "date_joined"]
        read_only_fields = ["id", "friends_number"]
        extra_kwargs = {'username': {'required': False}}
    
    def update(self, instance, validated_data):
        return super().update(instance, validated_data)

class MiniUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "profile_image"]
        read_only_fields = ["id", "username", "profile_image"]
    

### custom field

class Friend(serializers.Field):
    def to_representation(self, value):
        obj = {
            "id":value.id,
            "username":value.username,
            "profile_image":settings.DOMAIN_ORIGIN + value.profile_image.url,
        }
        if hasattr(value, "unseens"):
            obj["unseens"] = value.unseens
        return obj


class FriendsSerializer(serializers.Serializer):
    friends = serializers.ListField(child=Friend(), allow_empty=True, read_only=True)
    friends_requests = serializers.ListField(child=Friend(), allow_empty=True, read_only=True)
    user_requests = serializers.ListField(child=Friend(), allow_empty=True, read_only=True)
