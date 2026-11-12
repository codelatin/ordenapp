import json
from channels.generic.websocket import JsonWebsocketConsumer
from asgiref.sync import async_to_sync
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import Message
from .policies import can_message

class ChatConsumer(JsonWebsocketConsumer):
    def connect(self):
        self.user = self.scope['user']
        if not self.user.is_authenticated:
            self.close(code=4401)
            return
        try:
            self.other = get_user_model().objects.get(pk=int(self.scope['url_route']['kwargs']['user_id']), is_active=True)
        except get_user_model().DoesNotExist:
            self.close(code=4404)
            return
        if not (can_message(self.user, self.other) or can_message(self.other, self.user)):
            self.close(code=4403)
            return
        self.group = f'user_{self.user.pk}'
        async_to_sync(self.channel_layer.group_add)(self.group, self.channel_name)
        self.accept()

    def disconnect(self, close_code):
        if hasattr(self, 'group'):
            async_to_sync(self.channel_layer.group_discard)(self.group, self.channel_name)

    def receive_json(self, content, **kwargs):
        body = content.get('body', '')
        if not isinstance(body, str):
            self.send_json({'error': 'Formato inválido.'})
            return
        body = body.strip()
        if not body or len(body) > 2000:
            self.send_json({'error': 'El mensaje debe tener entre 1 y 2000 caracteres.'})
            return
        # Permiso comprobado nuevamente en cada envío.
        self.other.refresh_from_db()
        self.user.refresh_from_db()
        if not can_message(self.user, self.other):
            self.send_json({'error': 'No tienes permiso para enviar este mensaje.'})
            return
        msg = Message.objects.create(sender=self.user, recipient=self.other, body=body)
        payload = {'id': msg.pk, 'sender_id': self.user.pk, 'recipient_id': self.other.pk, 'sender': self.user.username,
                   'body': msg.body, 'timestamp': msg.created_at.isoformat()}
        for user_id in (self.user.pk, self.other.pk):
            async_to_sync(self.channel_layer.group_send)(f'user_{user_id}', {'type': 'message.event', 'message': payload})

    def message_event(self, event):
        m = event['message']
        if {m['sender_id'], m['recipient_id']} == {self.user.pk, self.other.pk}:
            self.send_json({'message': m})
