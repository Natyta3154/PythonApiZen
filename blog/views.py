from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

# Importamos los modelos LOCALES (ahora que Post y Reseña viven aquí)
from .models import Post, Reseña 

# Importamos los serializers desde products (donde los corregimos hace un momento)
from products.serializers import PostSerializer, ReseñaSerializer

# --- VISTAS DEL BLOG ---

@api_view(['GET'])
@permission_classes([AllowAny])
def lista_posts(request):
    posts = Post.objects.all().order_by('-fecha_publicacion')
    serializer = PostSerializer(posts, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def detalle_post(request, slug):
    try:
        post = Post.objects.get(slug=slug)
        serializer = PostSerializer(post)
        return Response(serializer.data)
    except Post.DoesNotExist:
        return Response(
            {"error": "Post no encontrado"},
            status=status.HTTP_404_NOT_FOUND
        )

# --- VISTAS DE TESTIMONIOS (RESEÑAS) ---

@api_view(['GET'])
@permission_classes([AllowAny])
def lista_testimonios(request):
    # Ahora Reseña se busca en el modelo local de blog
    reseñas = Reseña.objects.filter(moderado=True).order_by('-fecha')[:6]
    serializer = ReseñaSerializer(reseñas, many=True)
    return Response(serializer.data)