from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Post, Reseña
from products.models import ItemPedido, Producto
from products.serializers import PostSerializer, ReseñaSerializer
from users.views import CsrfExemptSessionAuthentication # Importamos tu clase de seguridad

# 1. GESTIÓN DE POSTS (Listar y Crear)
@api_view(['GET', 'POST'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([AllowAny]) # GET es libre, POST se valida adentro
def gestionar_posts(request):
    if request.method == 'GET':
        posts = Post.objects.all().order_by('-fecha_publicacion')
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        # Solo permitimos crear a usuarios staff (Admin)
        if not request.user.is_authenticated or not request.user.is_staff:
            return Response({"error": "No tienes permisos para publicar posts."}, status=403)
            
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(autor=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 2. DETALLE DE POST
@api_view(['GET'])
@permission_classes([AllowAny])
def detalle_post(request, slug):
    try:
        post = Post.objects.get(slug=slug)
        serializer = PostSerializer(post)
        return Response(serializer.data)
    except Post.DoesNotExist:
        return Response({"error": "Post no encontrado"}, status=404)

# 3. TESTIMONIOS (Reseñas generales para la Home)
@api_view(['GET'])
@permission_classes([AllowAny])
def lista_testimonios(request):
    reseñas = Reseña.objects.filter(moderado=True).order_by('-fecha')[:6]
    serializer = ReseñaSerializer(reseñas, many=True)
    return Response(serializer.data)

# 4. CREAR RESEÑA (Con validación de compra de AromaZen)
@api_view(['POST'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([IsAuthenticated])
def crear_reseña(request, producto_id):
    # Verificamos que el producto exista primero
    if not Producto.objects.filter(id=producto_id).exists():
        return Response({"error": "El producto no existe."}, status=404)

    # Lógica de CompraLog: Verificar si el usuario realmente pagó por este producto
    compro = ItemPedido.objects.filter(
        pedido__usuario=request.user, 
        producto_id=producto_id,
        pedido__estado='PAGADO'
    ).exists()

    if not compro:
        return Response({"error": "Solo los clientes que han completado su compra pueden dejar reseñas."}, status=403)

    # Evitar duplicados: Un usuario, una reseña por producto
    if Reseña.objects.filter(usuario=request.user, producto_id=producto_id).exists():
        return Response({"error": "Ya has dejado una reseña para este producto."}, status=400)

    serializer = ReseñaSerializer(data=request.data)
    if serializer.is_valid():
        # El campo 'moderado' suele ser False por defecto en el modelo
        serializer.save(usuario=request.user, producto_id=producto_id)
        return Response({"mensaje": "¡Gracias! Tu reseña ha sido enviada a moderación."}, status=201)
        
    return Response(serializer.errors, status=400)