from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer


class BulletinNoticeConsumer(JsonWebsocketConsumer):
    def connect(self):
        user = self.scope['user']
        if not user.is_authenticated or not user.is_active:
            self.close(code=4401)
            return
        self.group = f'bulletins_user_{user.pk}'
        async_to_sync(self.channel_layer.group_add)(self.group, self.channel_name)
        self.accept()

    def disconnect(self, code):
        if hasattr(self, 'group'):
            async_to_sync(self.channel_layer.group_discard)(self.group, self.channel_name)

    def bulletin_notice(self, event):
        self.send_json({'event': 'new_bulletin', 'bulletin': event['bulletin']})

    def bulletin_progress(self, event):
        self.send_json({'event': 'bulletin_progress', 'bulletin_id': event['bulletin_id']})
