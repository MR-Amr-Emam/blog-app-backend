from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.generics import RetrieveAPIView, RetrieveUpdateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed, NotFound, NotAcceptable
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.parsers import MultiPartParser, FormParser

from .models import User, FriendShip
from .serializers import UserProfSerializer, MiniUserSerializer, FriendsSerializer


class GetPairTokenAPI(APIView):
    def post(self, request):
        user = authenticate(username=request.POST.get("username"), password=request.POST.get("password"))
        if user is not None:
            refresh = RefreshToken.for_user(user)
            access = refresh.access_token
            response = Response()
            response.set_cookie(
                key="refresh_token",
                value=str(refresh),
                secure=False,
                httponly=False,
                samesite="Lax",
                path="/auth/token/refresh/",
            )
            response.set_cookie(
                key="access_token",
                value=str(access),
                secure=False,
                httponly=False,
                samesite="Lax",
                path="/",
            )
            return response
        else:
            raise AuthenticationFailed()


class RefreshTokenAPI(APIView):
    def post(self, request):
        raw_token = request.COOKIES.get("refresh_token")
        if raw_token is None:
            raise AuthenticationFailed()
        jwtauth_obj = JWTAuthentication()
        try:
            refresh_token = jwtauth_obj.get_validated_token(raw_token)
        except:
            raise AuthenticationFailed()
        access_token = refresh_token.access_token
        response = Response()
        response.set_cookie(
            key="access_token",
            value=str(access_token),
            secure=False,
            httponly=False,
            samesite="Lax",
            path="/",
        )
        return response


class UserProfileAPI(RetrieveUpdateAPIView):
    serializer_class = UserProfSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)
    def get_object(self):
        try:
            if self.kwargs["id"] == 0:
                return self.request.user
            else:
                user = User.objects.get(id=self.kwargs["id"])
                if self.request.method not in SAFE_METHODS and self.request.user != user:
                    raise NotAcceptable
                return user
        except:
            raise NotFound()
    def get_serializer(self, *args, **kwargs):
        serializer = super().get_serializer(*args, **kwargs)
        try:
            friend_ship = FriendShip.objects.get_friend_ship(self.request.user, serializer.instance)
            if(friend_ship.user1_status and friend_ship.user2_status):
                friend_status=1
            elif(friend_ship.is_requesting(serializer.instance)):
                friend_status=2
            else:
                friend_status=3
        except:
            friend_status=0
        
        serializer.instance.friend_status=friend_status
        return serializer



class SearchUsers(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MiniUserSerializer

    def get_queryset(self):
        search_param = self.kwargs.get("search_param")
        return User.objects.filter(username__contains=search_param)

class SearchUsersById(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        ids = request.data.get("ids")
        users = User.objects.filter(id__in=ids)
        users_serialized = []
        for user in users:
            serializer = MiniUserSerializer(user, context={"request":request})
            users_serialized.append(serializer.data)
        return Response(users_serialized)

class UserFriendsAPI(RetrieveUpdateDestroyAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class = FriendsSerializer
    def get_object(self):
        if(self.request.method in SAFE_METHODS):
            id = self.kwargs.get("id")
            if(id==0):
                return self.request.user.get_friends(True)
            else:
                user = User.objects.get(id=id)
                return user.get_friends(user==self.request.user)
        else:
            return None
        
    def perform_update(self, serializer):
        user=self.request.user
        friend=User.objects.get(id=self.request.data.get("id"))
        try:  ### update
            friend_ship = FriendShip.objects.get_friend_ship(user, friend)
            if(friend_ship.user2==user):
                friend_ship.user2_status=True
                friend_ship.save()
            else:

                raise NotAcceptable()
        except FriendShip.DoesNotExist: ### create
            if(user==friend):
                raise NotAcceptable()
            FriendShip.objects.create(user1=user, user2=friend)
    
    def perform_destroy(self, serializer):
        user=self.request.user
        friend=User.objects.get(id=self.request.data.get("id"))
        try:  ### delete
            friend_ship = FriendShip.objects.get_friend_ship(user, friend)
            friend_ship.delete()
        except FriendShip.DoesNotExist:
            raise NotAcceptable()


class Public(RetrieveAPIView):
    serializer_class = UserProfSerializer
    def get_object(self):
        return User.objects.get(id=1)