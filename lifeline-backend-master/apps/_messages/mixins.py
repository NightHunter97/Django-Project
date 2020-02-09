from apps._messages.utils import MessageHelper


class ReadByMixin:
    def update(self, instance, validated_data):
        user_uuid = self.context['request'].user.uuid
        if str(user_uuid) not in instance.read_by:
            instance.read_by.append(user_uuid)
        return super().update(instance, {})


class UpdateMetaMessageMixin:
    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        response.data['meta'] = MessageHelper().get_messages(request.user)
        return response
