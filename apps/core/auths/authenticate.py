from rest_framework_simplejwt.authentication import JWTAuthentication
from django.utils import translation


class MyCustomJWTAuthenticate(JWTAuthentication):
    def authenticate(self, request):
        user, token = super().authenticate(request)
        if user and isinstance(user, self.user_model):
            translation.activate(user.language if user.language else 'vi')
        return user, token
