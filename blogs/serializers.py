from rest_framework import serializers
from django.core.exceptions import BadRequest
from .models import Blog, Section, Comment, Category


from django.apps import apps
User = apps.get_model("authentication", "User")

class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ["image", "content"]

class UserSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    class Meta:
        model = User
        fields = ["id", "username", "profile_image"]
        read_only_fields = ["profile_image"]



class MiniBlogSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    liked = serializers.SerializerMethodField()
    def get_liked(self, obj):
        return obj.liked_people.filter(id=self.context.get("request").user.id).exists()

    class Meta:
        model = Blog
        fields = ["id", "user", "date", "category", "image", "title", "description", "is_video",
                "video", "likes_number", "views_number", "liked_people", "viewed_people", "liked",
                "for_group", "group"]



class BlogSerializer(MiniBlogSerializer):
    section_set = SectionSerializer(many=True)
    
    class Meta:
        model = MiniBlogSerializer.Meta.model
        fields = MiniBlogSerializer.Meta.fields + ["section_set"]

    def create(self, validated_data):
        user = validated_data.pop("user")
        sections = validated_data.pop("section_set")
        if(validated_data.get("is_video") and sections):
            raise BadRequest()
        try:
            user = User.objects.get(id=user["id"], username=user["username"])
        except:
            raise BadRequest()
        blog = Blog.objects.create(**validated_data, user=user)
        for section in sections:
            Section.objects.create(**section, blog=blog)
        return blog


class ParentCommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    liked = serializers.SerializerMethodField()
    likes_number = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ["id", "user", "blog", "date", "for_comment", "parent_comment", "content", "likes_number", "liked"]

    def get_liked(self, obj):
        return obj.likes.filter(id=self.context["request"].user.id).exists()
    def get_likes_number(self, obj):
        return obj.likes.count()

class CommentSerializer(ParentCommentSerializer):
    comment_set = ParentCommentSerializer(read_only=True, many=True)

    class Meta:
        model = ParentCommentSerializer.Meta.model
        fields = ParentCommentSerializer.Meta.fields + ["comment_set"]

    def create(self, validated_data):
        return Comment.objects.create(user=self.context.get("request").user, **validated_data)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"

class TinyBlogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blog
        fields = ["id", "title", "image"]
        read_only_fields = ["id", "title", "image"]
