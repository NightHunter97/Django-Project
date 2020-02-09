from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from apps._messages.services import get_about_patient_messages, get_user_messages


class MessageHelper:
    def get_messages(self, user=None):
        about = self._get_unread_count(get_about_patient_messages(user), user)
        team = self._get_unread_count(get_user_messages(user.pk), user)
        return {'all': about + team, 'about': about, 'team': team}

    @staticmethod
    def _get_unread_count(sequence, user):
        return len([message for message in sequence if str(user.uuid) not in message.read_by])

    def send(self, receivers, user=None):
        layer = get_channel_layer()
        for receiver in receivers:
            if not user or receiver.uuid != user.uuid:
                async_to_sync(layer.group_send)(str(receiver.uuid), {
                    'type': 'messages',
                    'message': self.get_messages(receiver)
                })
