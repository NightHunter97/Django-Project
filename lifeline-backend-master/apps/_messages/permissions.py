from apps.accounts.permissions import LifeLinePermissions


class MessagePermissions(LifeLinePermissions):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.perms_map['PATCH'] = ['%(app_label)s.view_%(model_name)s']
