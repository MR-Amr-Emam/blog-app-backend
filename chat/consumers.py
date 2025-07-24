import datetime
import json
from django.db.models import Q
from django.apps import apps
from .models import MsgChat, MsgChatSerializer
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync

User = apps.get_model("authentication", "User")

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        if(self.scope["user"].is_anonymous):
            return
        self.accept()
        user = self.scope["user"]
        friend_id = self.scope['url_route']['kwargs']['id']
        self.friend = User.objects.get(id=friend_id)
        self.group_name = f"chat_{min(friend_id, user.id)}_{max(friend_id, user.id)}"
        msgs = MsgChat.objects.filter(Q(user_from=self.friend, user_to=user) |
                                    Q(user_from=user, user_to=self.friend)).order_by("date")
        msgs = MsgChatSerializer(msgs, many=True)
        async_to_sync(self.channel_layer.group_add)(
            self.group_name, self.channel_name
        )
        self.send(text_data=json.dumps(msgs.data))


    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        msg = text_data_json["msg"]
        MsgChat.objects.create(msg=msg, user_from=self.scope["user"], user_to=self.friend)
        async_to_sync(self.channel_layer.group_send)(
            self.group_name,
            {"type":"group.msg",
            "user_id":self.scope["user"].id,
            "msg":msg,}
        )
    
    def group_msg(self, event):
        data = {
            "msg":event["msg"],
            'user_id':event["user_id"],
            }
        self.send(text_data=json.dumps(data))