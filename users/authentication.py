#Como Django REST Framework espera el token en el Header. necesitamos un pequeño "traductor" que tome el token de la cookie y se lo dé a Django.


from rest_framework.authentication import TokenAuthentication

class CookieTokenAuthentication(TokenAuthentication):
    def authenticate(self, request):
        # Buscamos el token en las cookies en lugar de los headers
        token = request.COOKIES.get('auth_token')
        
        if not token:
            return None
            
        return self.authenticate_credentials(token)