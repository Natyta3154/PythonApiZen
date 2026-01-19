from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth import login
from rest_framework.authtoken.models import Token 
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import AllowAny 

# Configuración común de cookies para mantener la sesión
COOKIE_SETTINGS = {
    'key': 'auth_token',
    'httponly': True,
    'secure': False,  # Cambiar a True en producción (HTTPS)
    'samesite': 'Lax',
    'max_age': 60*60*24*7  # 7 días
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
@api_view(['POST'])
def logout_api(request):
    """
    Cierra la sesión y elimina la cookie.
    """
    response = Response({'message': 'Sesión cerrada'}, status=status.HTTP_200_OK)
    response.delete_cookie('auth_token', samesite='Lax')
    return response

# Obtener datos del usuario actual
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    """
    Devuelve los datos del usuario actual verificando el token/sesión.
    """
    return Response({
        'username': request.user.username,
        'email': request.user.email,
        'is_staff': request.user.is_staff  # Permite al front persistir el rol tras refrescar
    })

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def actualizar_perfil(request):
    user = request.user
    data = request.data
    
    # Actualizar campos de identidad
    user.username = data.get('username', user.username)
    user.email = data.get('email', user.email).lower()
    user.first_name = data.get('first_name', user.first_name) # Nombre
    user.last_name = data.get('last_name', user.last_name)   # Apellido
    
    password = data.get('password')
    if password and len(password) > 0:
        user.set_password(password)
        
    try:
        user.save()
        return Response({
            'message': 'Perfil actualizado',
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_staff': user.is_staff
        })
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
@permission_classes([AllowAny]) # Ahora permitimos que la petición llegue siempre
def me(request):
    # Verificamos manualmente si está logueado
    if request.user.is_authenticated:
        return Response({
            'username': request.user.username,
            'email': request.user.email,
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'is_staff': request.user.is_staff,
            'authenticated': True # Un extra para tu frontend
        })
    
    # Si no está logueado, devolvemos un 200 (OK) pero avisando que no hay usuario
    # Esto quita el error Forbidden (403) de tu consola
    return Response({
        'authenticated': False,
        'message': 'No hay sesión activa'
    }, status=200)
