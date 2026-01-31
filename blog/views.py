from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Post, Reseña
from products.models import ItemPedido
from products.serializers import PostSerializer, ReseñaSerializer

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
        return Response({"error": "Post no encontrado"}, status=404)

@api_view(['GET'])
@permission_classes([AllowAny])
def lista_testimonios(request):
    reseñas = Reseña.objects.filter(moderado=True).order_by('-fecha')[:6]
    serializer = ReseñaSerializer(reseñas, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crear_reseña(request, producto_id):
    # Lógica para verificar compra antes de dejar reseña
    compro = ItemPedido.objects.filter(
        pedido__usuario=request.user, 
        producto_id=producto_id,
        pedido__estado='PAGADO'
    ).exists()

    if not compro:
        return Response({"error": "Debes comprar para reseñar."}, status=403)

    serializer = ReseñaSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(usuario=request.user, producto_id=producto_id)
        return Response({"mensaje": "Reseña enviada a moderación"}, status=201)
    return Response(serializer.errors, status=400)