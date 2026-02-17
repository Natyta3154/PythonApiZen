from rest_framework.authentication import BaseAuthentication
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import AnonymousUser


class CookieTokenAuthentication(BaseAuthentication):
    """
    Autenticación segura basada en cookie httpOnly.
    Lee auth_token desde el navegador y autentica al usuario.
    """

    def authenticate(self, request):

        token_key = request.COOKIES.get("auth_token")

        if not token_key:
            return None

        try:
            token = Token.objects.select_related("user").get(key=token_key)
        except Token.DoesNotExist:
            return None

        return (token.user, token)
