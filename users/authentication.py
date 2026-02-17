from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
from django.contrib.auth.models import AnonymousUser
from rest_framework.authtoken.models import Token


class CookieTokenAuthentication(BaseAuthentication):

    def authenticate(self, request):
        token_key = request.COOKIES.get("auth_token")

        # 🔹 Usuario no logueado → dejar pasar
        if not token_key:
            return None

        try:
            token = Token.objects.select_related("user").get(key=token_key)
        except Token.DoesNotExist:
            raise exceptions.AuthenticationFailed("Token inválido")

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed("Usuario inactivo")

        return (token.user, token)
