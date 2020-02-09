from django.contrib.auth.models import UserManager


class AccountManager(UserManager):

    def _create_user(self, username, email, password, **extra_fields):
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        return super().create_superuser('', email, password)
