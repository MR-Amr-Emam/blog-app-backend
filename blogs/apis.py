import json
from django.apps import apps
from django.db.models import F, Q
from django.core.exceptions import BadRequest

from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework.exceptions import NotFound, NotAcceptable, MethodNotAllowed
from rest_framework.parsers import MultiPartParser, FormParser


from .models import Blog, Comment, Category
from .serializers import BlogSerializer, MiniBlogSerializer, CommentSerializer, CategorySerializer

User = apps.get_model("authentication", "User")
FriendShip = apps.get_model("authentication", "FriendShip")
Group = apps.get_model("groups", "Group")


class CreateBlogApi(CreateAPIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]
    serializer_class = BlogSerializer
    queryset = Blog.objects.all()

    def get_serializer(self, *args, **kwargs):
        request_data = self.request.data
        user = self.request.user
        user_dict = {"id":user.id, "username":user.username, "profile_image":None}
        data = json.loads(request_data.get("data"))

        data["user"] = user_dict
        data["image"] = request_data.get(data.get("image"))
        if data.get("is_video"):
            data["video"] = request_data["video"]
        else:
            for section in data["section_set"]:
                if(request_data.get(section["image"])):
                    section["image"] = request_data.get(section["image"])
                else:
                    section["image"] = None

                    
        if data.get("for_group"):
            group = Group.objects.filter(id=data.get("group"))
            if (not group.exists() or not user.joinrequest_set.filter(group=group.first(), status=True).exists()):
                raise BadRequest()
        serializer = self.serializer_class(data=data, context={"request":self.request})
        return serializer

        

class BlogApi(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Blog.objects.all()
    lookup_field = "id"
    
    def perform_update(self, serializer):
        request = self.request
        obj = serializer.instance
        try:
            obj.liked_people.get(id=request.user.id)
            obj.liked_people.remove(request.user)
            obj.likes_number -= 1
        except User.DoesNotExist:
            obj.liked_people.add(request.user)
            obj.likes_number += 1
        return obj.save()

    def get_serializer_class(self):
        if(self.kwargs.get("mini") and 
           self.kwargs.get("mini")=="mini"):
            return MiniBlogSerializer
        else:
            return BlogSerializer


    def get_object(self):
        obj = super().get_object()
        if(self.request.method not in SAFE_METHODS and self.request.user != obj.user):
            raise MethodNotAllowed()

        try:
            obj.viewed_people.get(id = self.request.user.id)
        except User.DoesNotExist:
            obj.viewed_people.add(self.request.user)
            obj.views_number += 1
            obj.save()
        return obj
    

class BlogsApi(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MiniBlogSerializer

    def get_queryset(self):
        if(self.kwargs.get("type")=="top"):
            return (Blog.objects.filter(user__id = self.kwargs.get("id"))
                    .annotate(reactions=F("likes_number")+F("views_number"))
                    .order_by("-reactions")[:3])
        elif(self.kwargs.get("type")=="video"):
            return Blog.objects.filter(user__id=self.kwargs.get("id")).filter(is_video=True)
        elif(self.kwargs.get("type")=="related"):
            try:
                category = Category.objects.get(id = self.kwargs.get("id"))
            except Category.DoesNotExist:
                category=None
            return ( Blog.objects.filter(category=category)
                .annotate(reactions=F("likes_number")+F("views_number")).order_by("-reactions")[:3] )
        else:
            return Blog.objects.filter(Q(user__id=self.kwargs.get("id"))&Q(for_group=False)).order_by("-date")

class HomeBlogsApi(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MiniBlogSerializer

    def get_queryset(self):
        user=self.request.user
        friends = user.get_friends(True)
        categroy_id = self.kwargs.get("id")
        qs = (Blog.objects.filter(Q(user=user) | Q(user__in=friends.friends)
            | Q(user__in=friends.user_requests)).order_by("-date"))
        if(categroy_id):
            return qs.filter(category__id=categroy_id)
        else:
            return qs
    
class AddCommentAPI(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CommentSerializer

    def get_serializer(self, instance=None, data=None, *args, **kwargs):
        data["blog"] = self.kwargs.get("id")
        blog = Blog.objects.get(id=self.kwargs.get("id"))
        try:
            if(blog.user != self.request.user):
                friendShip = FriendShip.objects.get_friend_ship(self.request.user, blog.user)
                if(not friendShip.user1_status or not friendShip.user2_status):
                    raise BadRequest()
        except FriendShip.DoesNotExist:
            raise BadRequest()
        
        if(data.get("for_comment") and Comment.objects.get(id=data.get("parent_comment")).for_comment):
            raise BadRequest()

        return self.serializer_class(instance=instance, data=data, context={
            "request":self.request,
        })

class CommentsAPI(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CommentSerializer

    def get_queryset(self):
        return Blog.objects.get(id=self.kwargs.get("id")).comment_set.filter(for_comment=False).order_by("-date")
    
class CommentAPI(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CommentSerializer
    lookup_field = "id"
    queryset = Comment.objects.all()

    def perform_update(self, serializer):
        user = self.request.user
        (self.get_object().likes.remove(user) if self.get_object().likes.filter(id=user.id).exists()
        else self.get_object().likes.add(user))

class CategorysAPI(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CategorySerializer
    queryset = Category.objects.all()