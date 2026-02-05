from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth import login
from rest_framework.authtoken.models import Token 
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import AllowAny 
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from django.views.decorators.csrf import csrf_exempt 
from django.contrib.auth import authenticate
from django.contrib.auth import logout as django_logout
import datetime
from django.conf import settings

# --- CLASE PARA SOLUCIONAR EL ERROR CSRF ---

class CsrfExemptSessionAuthentication(SessionAuthentication):
    """
    Esta clase evita que Django pida el token CSRF.
    Es necesaria porque estás usando cookies y login() de Django.
    """
    def enforce_csrf(self, request):
        return None

# Configuración común de cookies para mantener la sesión
COOKIE_SETTINGS = {
    'key': 'auth_token',
    'httponly': True,
    'secure': not settings.DEBUG, # True si no estamos en modo debug
    'samesite': 'None' if not settings.DEBUG else 'Lax', # None para Vercel
    'max_age': 60*60*24*7
}

#registro de usuario
@api_view(['POST'])
@permission_classes([AllowAny])
def registro_api(request):
    """
    Registra un nuevo usuario y devuelve sus datos junto con el rol.
    """
    username = request.data.get('username', '').strip()
    password = request.data.get('password', '').strip()
    email = request.data.get('email', '').strip().lower()

    if not username or not password or not email:
        return Response({'error': 'Faltan datos (username, email o password)'}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username__iexact=username).exists():
        return Response({'error': 'El nombre de usuario ya está en uso'}, status=status.HTTP_400_BAD_REQUEST)
    
    if User.objects.filter(email__iexact=email).exists():
        return Response({'error': 'Este email ya está registrado'}, status=status.HTTP_400_BAD_REQUEST)

    # Crear usuario
    user = User.objects.create_user(username=username, password=password, email=email)
    token, _ = Token.objects.get_or_create(user=user)

    response = Response({
        'message': 'Usuario creado con éxito',
        'username': user.username,
        'email': user.email,
        'is_staff': user.is_staff  # Indica si es admin
    }, status=status.HTTP_201_CREATED)

    response.set_cookie(value=token.key, **COOKIE_SETTINGS)
    return response

#login personalizado de usuario
class CustomLogin(ObtainAuthToken):
    """
    Login personalizado que permite entrar con Email y devuelve el rol is_staff.


    """
# Esto soluciona el error de CSRF al intentar loguearse
    authentication_classes = [CsrfExemptSessionAuthentication]


    def post(self, request, *args, **kwargs):
        data = request.data.copy()
        email = data.get('email')
        
        if email:
            user_obj = User.objects.filter(email=email).first()
            if user_obj:
                data['username'] = user_obj.username 
            else:
                return Response({'error': 'No existe un usuario con ese email'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(data=data, context={'request': request})
        
        if not serializer.is_valid():
            return Response({'error': 'Contraseña incorrecta o datos inválidos'}, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)

        # Importante: Iniciar sesión en Django para que las cookies de sesión también funcionen
        login(request, user)

        response = Response({
            'message': 'Login exitoso',
            'username': user.username,
            'email': user.email,
            'is_staff': user.is_staff  # <--- Crucial para el panel de admin en el front
        }, status=status.HTTP_200_OK)

        response.set_cookie(value=token.key, **COOKIE_SETTINGS)
        return response


#logout personalizado de usuario
@csrf_exempt
@api_view(['GET', 'POST']) # <--- Habilitamos ambos para matar el 405
@authentication_classes([]) # Evita que pida Token para salir
@permission_classes([AllowAny])
def logout_api(request):
    """
    Cierra la sesión de forma profesional, invalida en DB y limpia el navegador.
    """
    user_identity = f"{request.user.username}" if request.user.is_authenticated else "Anónimo"
    
    print(f"\n--- [SISTEMA DE SEGURIDAD: LOGOUT] {datetime.datetime.now().strftime('%H:%M:%S')} ---")
    print(f"ESTADO: Procesando salida para {user_identity}")

    # 1. Invalida la sesión en Django (Servidor)
    django_logout(request)

    response = Response(
        {"status": "success", "message": "Sesión cerrada de forma segura"}, 
        status=status.HTTP_200_OK
    )

    # 2. Borrado de Cookies (Mismos parámetros que usas en el Login)
    # Importante: El path '/' asegura que se borren globalmente
    cookie_params = {
    'path': '/', 
    'samesite': 'None' if not settings.DEBUG else 'Lax',
    'secure': not settings.DEBUG
}
    
    response.delete_cookie('auth_token', **cookie_params)
    response.delete_cookie('csrftoken', **cookie_params)
    response.delete_cookie('sessionid', **cookie_params)

    print(f"RESULTADO: Cookies eliminadas. herny3154@gmail.com ha salido del sistema.")
    print("-" * 50 + "\n")
    
    return response

# Obtener datos del usuario actual
@api_view(['GET'])
@authentication_classes([CsrfExemptSessionAuthentication]) # Para que reconozca la sesión de la cookie
@permission_classes([AllowAny]) 
def me(request):
    """
    Esta es la vista que usa tu Front al cargar la página de Perfil.
    """
    if request.user.is_authenticated:
        return Response({
            'username': request.user.username,
            'email': request.user.email,
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'is_staff': request.user.is_staff,
            'authenticated': True
        }, status=status.HTTP_200_OK)
    
    return Response({
        'authenticated': False,
        'message': 'No hay sesión activa'
    }, status=status.HTTP_200_OK)

@api_view(['PUT'])
# AGREGAMOS ESTO: Es vital para que herede la exención de CSRF y reconozca la sesión
@authentication_classes([CsrfExemptSessionAuthentication]) 
@permission_classes([IsAuthenticated])
def actualizar_perfil(request):
    user = request.user
    data = request.data

    # LOG DE INICIO DE OPERACIÓN [2026-01-19]
    print(f"--- [LOG PERFIL] Intento de actualización: Usuario ID {user.id} ({user.username}) ---")

    # Actualizar campos de identidad
    # Usamos data.get('campo', user.campo) para que si el campo no viene, no lo ponga en blanco
    user.username = data.get('username', user.username).strip()
    user.email = data.get('email', user.email).strip().lower()
    user.first_name = data.get('first_name', user.first_name).strip()
    user.last_name = data.get('last_name', user.last_name).strip()
    
    password = data.get('password')
    if password and len(password.strip()) > 0:
        user.set_password(password)
        print(f"--- [LOG PERFIL] El usuario {user.username} cambió su contraseña ---")
        
    try:
        user.save() # GUARDADO EN DB    
        # LOG DE ÉXITO
        print(f"--- [LOG PERFIL] ÉXITO: Base de datos actualizada para {user.username} ---")
        
        return Response({
            'message': 'Perfil actualizado correctamente',
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_staff': user.is_staff
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        print(f"--- [LOG PERFIL] ERROR al guardar: {str(e)} ---")
        return Response({
            'error': 'No se pudo guardar la información. Verifique que el nombre de usuario o email no existan.'
        }, status=status.HTTP_400_BAD_REQUEST)




