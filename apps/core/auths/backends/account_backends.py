from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class AccountBackend(ModelBackend):
    def get_user(self, user_id):
        return get_user_model().objects.filter(id=user_id).first()

    def get_user_by_username(self, username):
        return get_user_model().objects.filter(**{get_user_model().USERNAME_FIELD: username}).first()

    def authenticate(self, request, username=None, password=None, **kwargs):
        user = self.get_user_by_username(username=username)
        if user:
            if user.check_password(password):
                return user
        return None
