from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.models import Token

# ================= REGISTRO =================
@api_view(["POST"])
@permission_classes([AllowAny])
def registro_api(request):
    username = request.data.get("username", "").strip()
    password = request.data.get("password", "").strip()
    email = request.data.get("email", "").strip().lower()

    if not username or not password or not email:
        return Response({"error": "Faltan datos"}, status=400)

    if User.objects.filter(username__iexact=username).exists():
        return Response({"error": "El nombre de usuario ya está en uso"}, status=400)

    if User.objects.filter(email__iexact=email).exists():
        return Response({"error": "Este email ya está registrado"}, status=400)

    user = User.objects.create_user(username=username, password=password, email=email)
    
    # Creamos el Token para el nuevo usuario
    token, _ = Token.objects.get_or_create(user=user)
    login(request, user) 

    return Response({
        "message": "Usuario creado y logueado",
        "token": token.key, # ✅ Enviamos token
        "username": user.username,
        "email": user.email,
        "is_staff": user.is_staff
    }, status=201)


# ================= LOGIN =================
@api_view(["POST"])
@permission_classes([AllowAny])
def login_api(request):
    email = request.data.get("email") 
    password = request.data.get("password")

    if not email or not password:
        return Response({"error": "Email/Username y contraseña requeridos"}, status=400)

    user = User.objects.filter(email=email).first() or User.objects.filter(username=email).first()
    if not user:
        return Response({"error": "Usuario no encontrado"}, status=400)

    user = authenticate(request, username=user.username, password=password)
    if not user:
        return Response({"error": "Contraseña incorrecta"}, status=400)

    # Generamos o recuperamos el Token
    token_obj, _ = Token.objects.get_or_create(user=user)
    login(request, user) 

    return Response({
        "message": "Login exitoso",
        "token": token_obj.key, # ✅ Enviamos token
        "username": user.username,
        "email": user.email,
        "is_staff": user.is_staff
    })

# ... (El resto de tus funciones logout, me y actualizar_perfil se mantienen igual)


# ================= LOGOUT =================
@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny])
def logout_api(request):
    """
    Cierra sesión eliminando sessionid y CSRF cookie.
    """
    logout(request)  # elimina la sesión automáticamente

    response = Response({"status": "success", "message": "Sesión cerrada"})
    response.delete_cookie("csrftoken", path="/")  # opcional
    response.delete_cookie("sessionid", path="/")  # opcional
    return response


# ================= USUARIO ACTUAL =================
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    """
    Devuelve información del usuario logueado.
    """
    user = request.user
    return Response({
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "is_staff": user.is_staff,
        "authenticated": True
    })


# ================= ACTUALIZAR PERFIL =================
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def actualizar_perfil(request):
    """
    Permite al usuario actualizar su perfil y contraseña.
    """
    user = request.user
    data = request.data

    user.username = data.get("username", user.username).strip()
    user.email = data.get("email", user.email).strip().lower()
    user.first_name = data.get("first_name", user.first_name).strip()
    user.last_name = data.get("last_name", user.last_name).strip()

    password = data.get("password")
    if password:
        user.set_password(password)
        login(request, user)  # re-loguea al usuario si cambia contraseña

    user.save()

    return Response({
        "message": "Perfil actualizado correctamente",
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,

        "last_name": user.last_name,
        "is_staff": user.is_staff
    })
