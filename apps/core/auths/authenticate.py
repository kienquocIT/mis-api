from rest_framework_simplejwt.authentication import JWTAuthentication
from django.utils import translation


class MyCustomJWTAuthenticate(JWTAuthentication):
    def authenticate(self, request):
        data = super().authenticate(request)
        if data and isinstance(data, tuple) and isinstance(data[0], self.user_model):
            translation.activate(data[0].language if data[0].language else 'vi')
        return data
