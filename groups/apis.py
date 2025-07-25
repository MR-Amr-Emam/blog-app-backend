import json
from re import A
from django.apps import apps
from django.db.models import Q
from django.core.exceptions import BadRequest

from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import (ListAPIView, CreateAPIView, RetrieveUpdateDestroyAPIView,
                                     DestroyAPIView)


from .models import Group, JoinRequest, Invite
from .serializers import GroupSerializer, MiniGroupSerializer, UserSerializer, InviteSerializer

User = apps.get_model("authentication", "User")

class CreateAPI(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GroupSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_serializer(self, instance=None, data=None, **kwargs):
        raw_data = data
        data = json.loads(raw_data.get("data"))
        data["image"] = raw_data.get(data.get("image"))
        serializer = self.serializer_class(data=data, context={"request": self.request})
        return serializer

    def perform_create(self, serializer):
        print(serializer.validated_data)
        obj = serializer.save()
        JoinRequest.objects.create(group=obj, member=self.request.user, status=True, admin=True)
        return super().perform_create(serializer)



class GroupsAPI(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MiniGroupSerializer

    def get_queryset(self, *args, **kwargs):
        user = User.objects.get(id=self.kwargs.get("id"))
        return Group.objects.filter(Q(joinrequest__member=user) & Q(joinrequest__status=True))

class GroupAPI(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GroupSerializer
    parser_classes = [MultiPartParser, FormParser]
    lookup_field = "id"
    queryset = Group.objects.all()

    def get_serializer(self, instance=None, data=None, **kwargs):
        raw_data = data
        context={"request":self.request, "group_id":self.kwargs.get("id")}
        if(raw_data):
            jr = JoinRequest.objects.filter(group=instance, member=self.request.user)
            if(not jr.exists() and not jr.first().admin):
                raise BadRequest()
            data = json.loads(raw_data.get("data"))
            data["image"] = raw_data[data["image"]]
            return self.serializer_class(instance, data, context=context)

        return self.serializer_class(instance, context=context)


class AdminStaffsAPI(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, group_id, type, **kwargs):
        jr = JoinRequest.objects.filter(Q(member=request.user) &
                        Q(admin=True) & Q(group__id=group_id))

        if not jr.exists():
            raise BadRequest()
        if type=="requests":
            users = User.objects.filter(Q(joinrequest__group__id=group_id) & Q(joinrequest__status=False))
            serializer = UserSerializer(users, many=True, context={"request":request})
            return Response(serializer.data)




class RequestsAPI(APIView):
    permission_classes = [IsAuthenticated]
    def put(self, request, group_id, type):
        group = Group.objects.get(id=group_id)
        member_id = request.data.get("id")
        jr = (JoinRequest.objects.filter(member__id=member_id, group=group) if member_id else "")
        if type=="join":
            group = Group.objects.get(id=group_id)
            group.members.add(request.user)
            return Response()
        elif type=="leave":
            jr = JoinRequest.objects.filter(member__id=request.user.id, group=group)
            if jr.exists():
                jr.first().delete()
            return Response()
        elif type=="accept":
            if (not User.objects.filter(Q(joinrequest__admin=True) & Q(joinrequest__group=group) &
            Q(id=request.user.id)).exists()) or (not jr.exists()):
                raise BadRequest()
            jr = jr.first()
            jr.status=True
            jr.save()
            return Response()
        elif type=="setadmin":
            if (not User.objects.filter(Q(joinrequest__admin=True) & Q(joinrequest__group=group) &
            Q(id=request.user.id)).exists()) or (not jr.exists()) or (not jr.first().status):
                raise BadRequest()
            jr = jr.first()
            jr.admin=True
            jr.save()
            return Response()
        elif type=="remove":
            if (not User.objects.filter(joinrequest__admin=True, id=request.user.id,
                            joinrequest__group=group).exists()) or (not jr.exists()) or jr.first().admin:
                raise BadRequest()
            jr = jr.first()
            jr.delete()
            return Response()
        elif type=="invite":
            members = User.objects.filter(id__in=self.request.data.get("ids"))
            qs = User.objects.filter(joinrequest__status=True, joinrequest__group=group, id=request.user.id)
            if (not qs.exists()):
                raise BadRequest()
            for member in members:
                jr = JoinRequest.objects.filter(member=member, group=group)
                if not jr.exists():
                    raise BadRequest()
                Invite.objects.get_or_create(group=group, inviter=request.user, invited=member)
            return Response()

class InvitesAPI(ListAPIView):
    serializer_class = InviteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Invite.objects.filter(invited=self.request.user)

class DeleteInviteAPI(DestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Invite.objects.all()
    serializer_class = InviteSerializer

    def get_object(self):
        invite = Invite.objects.get(id=self.kwargs.get("id"))
        if(invite.invited != self.request.user):
            raise BadRequest()
        else:
            return invite