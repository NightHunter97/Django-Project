from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
import json

from rest_framework.exceptions import ValidationError
from rest_framework_jwt.serializers import VerifyJSONWebTokenSerializer


class MessageConsumer(AsyncWebsocketConsumer):

    @database_sync_to_async
    def get_data(self, data):
        return VerifyJSONWebTokenSerializer().validate(data)

    async def connect(self):
        data = {'token': self.scope['url_route']['kwargs']['jwt']}
        try:
            valid_data = await self.get_data(data)
            self.user = valid_data['user']
        except ValidationError as v:
            return v
        await self.channel_layer.group_add(str(self.user.uuid), self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            str(self.user.uuid),
            self.channel_name
        )

    async def messages(self, event):
        await self.send(text_data=json.dumps(event['message']))
