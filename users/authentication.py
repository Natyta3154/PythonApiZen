from rest_framework.authentication import TokenAuthentication, SessionAuthentication

class CookieTokenAuthentication(TokenAuthentication):
    """
    Traductor: Toma el token de la cookie 'auth_token' (del login)
    y lo valida para que request.user sea el usuario real.
    """
    def authenticate(self, request):
        token_key = request.COOKIES.get('auth_token')
        if not token_key:
            return None
        return self.authenticate_credentials(token_key)

class CsrfExemptSessionAuthentication(SessionAuthentication):
    """
    Desactiva la verificación CSRF para permitir peticiones POST 
    desde el frontend de React (localhost:5173).
    """
    def enforce_csrf(self, request):
        return None