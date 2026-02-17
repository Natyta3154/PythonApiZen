from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth import login
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authentication import SessionAuthentication
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import logout as django_logout
import datetime
from django.conf import settings
from .authentication import CookieTokenAuthentication


# ================= CSRF EXEMPT SESSION =================
class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return None


# ================= COOKIE CONFIG =================
COOKIE_SETTINGS = {
    "httponly": True,
    "secure": True,
    "samesite": "None",
    "max_age": 60 * 60 * 24 * 7,
    "path": "/",
}


def set_auth_cookie(response, token):
    response.set_cookie("auth_token", token, **COOKIE_SETTINGS)
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
    authentication_classes = [CsrfExemptSessionAuthentication]

    def post(self, request, *args, **kwargs):
        data = request.data.copy()
        email = data.get("email")

        if email:
            user_obj = User.objects.filter(email=email).first()
            if not user_obj:
                return Response({"error": "No existe un usuario con ese email"}, status=status.HTTP_400_BAD_REQUEST)
            data["username"] = user_obj.username

        serializer = self.serializer_class(data=data, context={"request": request})
        if not serializer.is_valid():
            return Response({"error": "Credenciales inválidas"}, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.validated_data["user"]
        token, _ = Token.objects.get_or_create(user=user)
        login(request, user)

        response = Response({
            "message": "Login exitoso",
            "username": user.username,
            "email": user.email,
            "is_staff": user.is_staff
        }, status=status.HTTP_200_OK)

        return set_auth_cookie(response, token.key)


# ================= LOGOUT =================
@csrf_exempt
@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def logout_api(request):
    django_logout(request)

    response = Response({"status": "success", "message": "Sesión cerrada"}, status=status.HTTP_200_OK)

    cookie_params = {
        "path": "/",
        "samesite": "None" if not settings.DEBUG else "Lax",
        "secure": not settings.DEBUG,
    }

    response.delete_cookie("auth_token", **cookie_params)
    response.delete_cookie("csrftoken", **cookie_params)
    response.delete_cookie("sessionid", **cookie_params)

    return response


# ================= ME =================
@api_view(["GET"])
@authentication_classes([CookieTokenAuthentication, CsrfExemptSessionAuthentication])
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

    return Response({"authenticated": False, "message": "No hay sesión activa"})


# ================= ACTUALIZAR PERFIL =================
@api_view(["PUT"])
@authentication_classes([CookieTokenAuthentication, CsrfExemptSessionAuthentication])
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
        return Response({"error": "No se pudo guardar la información"}, status=status.HTTP_400_BAD_REQUEST)