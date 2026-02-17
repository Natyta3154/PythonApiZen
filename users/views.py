from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from django.conf import settings
from .authentication import CookieTokenAuthentication


# ================= CONFIG COOKIE =================

COOKIE_SETTINGS = {
    "key": "auth_token",
    "httponly": True,
    "secure": True,          # obligatorio en Railway
    "samesite": "None",      # obligatorio para Vercel -> Railway
    "max_age": 60 * 60 * 24 * 7,
    "path": "/",
    "domain": ".up.railway.app",           # Se ajustará dinámicamente en producción
}


def set_auth_cookie(response, token):
    response.set_cookie(value=token, **COOKIE_SETTINGS)
    return response


# ================= REGISTRO =================

@api_view(["POST"])
@permission_classes([AllowAny])
def registro_api(request):

    username = request.data.get("username", "").strip()
    password = request.data.get("password", "").strip()
    email = request.data.get("email", "").strip().lower()

    if not username or not password or not email:
        return Response({"error": "Faltan datos"}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username__iexact=username).exists():
        return Response({"error": "El nombre de usuario ya está en uso"}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(email__iexact=email).exists():
        return Response({"error": "Este email ya está registrado"}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(username=username, password=password, email=email)
    token, _ = Token.objects.get_or_create(user=user)

    response = Response({
        "message": "Usuario creado con éxito",
        "username": user.username,
        "email": user.email,
        "is_staff": user.is_staff
    }, status=status.HTTP_201_CREATED)

    return set_auth_cookie(response, token.key)


# ================= LOGIN =================

class CustomLogin(ObtainAuthToken):
    permission_classes = [AllowAny]
    authentication_classes = []  # importante: sin sesión

    def post(self, request, *args, **kwargs):

        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response({"error": "Email y contraseña requeridos"}, status=400)

        user = User.objects.filter(email=email).first()
        if not user:
            return Response({"error": "Usuario no encontrado"}, status=400)

        user = authenticate(username=user.username, password=password)
        if not user:
            return Response({"error": "Contraseña incorrecta"}, status=400)

        token, _ = Token.objects.get_or_create(user=user)

        response = Response({
            "message": "Login exitoso",
            "username": user.username,
            "email": user.email,
            "is_staff": user.is_staff
        })

        return set_auth_cookie(response, token.key)


# ================= LOGOUT =================

@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny])
def logout_api(request):

    response = Response({"status": "success", "message": "Sesión cerrada"})

    response.delete_cookie("auth_token", path="/", samesite="None", secure=True)
    response.delete_cookie("csrftoken", path="/", samesite="None", secure=True)
    response.delete_cookie("sessionid", path="/", samesite="None", secure=True)

    return response


# ================= ME =================

@api_view(["GET"])
@authentication_classes([CookieTokenAuthentication])
@permission_classes([AllowAny])
def me(request):

    if request.user.is_authenticated:
        return Response({
            "username": request.user.username,
            "email": request.user.email,
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
            "is_staff": request.user.is_staff,
            "authenticated": True
        })

    return Response({"authenticated": False})


# ================= ACTUALIZAR PERFIL =================

@api_view(["PUT"])
@authentication_classes([CookieTokenAuthentication])
@permission_classes([IsAuthenticated])
def actualizar_perfil(request):

    user = request.user
    data = request.data

    user.username = data.get("username", user.username).strip()
    user.email = data.get("email", user.email).strip().lower()
    user.first_name = data.get("first_name", user.first_name).strip()
    user.last_name = data.get("last_name", user.last_name).strip()

    password = data.get("password")
    if password and password.strip():
        user.set_password(password)

    try:
        user.save()
        return Response({
            "message": "Perfil actualizado correctamente",
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_staff": user.is_staff
        })

    except Exception:
        return Response(
            {"error": "No se pudo guardar la información"},
            status=status.HTTP_400_BAD_REQUEST
        )
