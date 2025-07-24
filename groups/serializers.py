from django.apps import apps
from rest_framework import serializers

from .models import Group, JoinRequest, Invite

User = apps.get_model("authentication", "User")
Blog = apps.get_model("blogs", "Blog")



class UserSerializer(serializers.ModelSerializer):
    admin = serializers.SerializerMethodField()
    def get_admin(self, obj):
        group_id = self.context.get("group_id")
        if group_id:
            jr = JoinRequest.objects.filter(group__id=group_id, member=obj)
            if jr.exists():
                return jr.first().admin
        return None

    class Meta:
        model = User
        fields = ["id", "username", "profile_image", "admin"]


class MiniBlogSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    liked = serializers.SerializerMethodField()
    def get_liked(self, obj):
        return obj.liked_people.filter(id=self.context.get("request").user.id).exists()

    class Meta:
        model = Blog
        fields = ["id", "user", "date", "category", "image", "title", "description", "is_video",
                "video", "likes_number", "views_number", "liked_people", "viewed_people", "liked"]




class GroupSerializer(serializers.ModelSerializer):
    members = serializers.SerializerMethodField()
    blogs = serializers.SerializerMethodField()
    members_number = serializers.SerializerMethodField()
    user_status = serializers.SerializerMethodField()
    def get_members(self, obj):
        qs = obj.members.filter(joinrequest__status=True).order_by("-joinrequest__admin")
        serializer = UserSerializer(qs,context=self.context, many=True)
        return serializer.data
    
    def get_blogs(self, obj):
        jr = JoinRequest.objects.filter(group=obj).filter(member=self.context.get("request").user)
        if not jr.exists() or not jr.first().status:
            return []
        serializer = MiniBlogSerializer(Blog.objects.filter(group=obj).order_by("-date"),
                                    context=self.context, many=True)
        return serializer.data

    def get_members_number(self, obj):
        return obj.members.filter(joinrequest__status=True).count()
    
    def get_user_status(self, obj):
        state = 0
        jr = JoinRequest.objects.filter(group=obj, member=self.context.get("request").user)
        if jr.exists():
            state = 1
            if jr.first().status:
                state = 2
                if jr.first().admin:
                    state= 3
        return state


    class Meta:
        model = Group
        fields = "__all__"


class MiniGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ["id", "name", "image"]


class InviteSerializer(serializers.ModelSerializer):
    inviter = serializers.SerializerMethodField()
    group = serializers.SerializerMethodField()
    def get_inviter(self, obj):
        return {"id":obj.inviter.id, "username":obj.inviter.username}
    def get_group(self, obj):
        return {"id":obj.group.id, "name":obj.group.name}
    class Meta:
        model = Invite
        fields = ["id", "inviter", "group"]