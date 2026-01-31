import mercadopago
import datetime
import traceback
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

# Rest Framework
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny 
from rest_framework.response import Response
from rest_framework import status, serializers, viewsets
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from django.contrib.auth import logout as django_logout

# Autenticación personalizada
from users.authentication import CookieTokenAuthentication, CsrfExemptSessionAuthentication

# MODELOS
# 1. Importamos lo que quedó en products
from .models import CompraLog, ItemPedido, Producto, Pedido, Consulta, Categoria
# 2. Importamos lo que se movió a blog (CORRECCIÓN VITAL)
from blog.models import Post, Reseña 

# SERIALIZERS
from .serializers import (
    ConsultaSerializer, ProductoSerializer, HistorialSerializer, 
    CategoriaSerializer, PostSerializer, ReseñaSerializer
)

from .services import CompraService


# --- LISTADOS ---
@api_view(['GET'])
@permission_classes([AllowAny])
def lista_productos(request):
    serializer = ProductoSerializer(Producto.objects.all(), many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny]) 
def lista_ofertas(request):
    serializer = ProductoSerializer(Producto.objects.filter(en_oferta=True), many=True)
    return Response(serializer.data)



# --- LISTADO DE CATEGORÍAS (Faltaba esta vista) ---
@api_view(['GET'])
@permission_classes([AllowAny])
def lista_categorias(request):
    """
    Retorna todas las categorías disponibles para los filtros del frontend.
    """
    from .models import Categoria
    from .serializers import CategoriaSerializer
    
    categorias = Categoria.objects.all()
    serializer = CategoriaSerializer(categorias, many=True)
    return Response(serializer.data)



# --- PROCESAR COMPRA REAL ---
@api_view(['POST'])
@authentication_classes([CookieTokenAuthentication, CsrfExemptSessionAuthentication])
@permission_classes([IsAuthenticated])
def realizar_compra_carrito(request):
    items = request.data.get('items', [])
    if not items:
        return Response({"error": "Carrito vacío"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # 📝 LOG DE COMPRA
        print(f"\n--- [LOG DE COMPRA] {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")
        print(f"USUARIO: {request.user.username} (ID: {request.user.id})")
        
        # 1. Llamada al servicio que integra Mercado Pago
        pedido, mp_response = CompraService.ejecutar_pago_mercadopago(request.user, items)
        
        # 2. LOG DE COMPRA PERSISTENTE (MySQL)
        CompraLog.objects.create(
            usuario=request.user,
            pedido=pedido,
            detalle_log=f"Iniciado pago MP. Pedido #{pedido.id}. Items: {len(items)}",
            monto=pedido.total_pagado,
            referencia_pago=str(pedido.id)
        )

        return Response({
            "pedido_id": pedido.id,
            "preference_id": mp_response.get("id"),
            "url_pago": mp_response.get("init_point"),
            "total": pedido.total_pagado
        }, status=status.HTTP_201_CREATED)

    except ValueError as ve:
        return Response({"error": str(ve)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        traceback.print_exc()
        return Response({
            "error": "Error al procesar el pago",
            "detalle_tecnico": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# --- HISTORIAL ---

@api_view(['GET'])
@authentication_classes([CookieTokenAuthentication, CsrfExemptSessionAuthentication])
@permission_classes([IsAuthenticated])
def mis_compras(request):
    pedidos = Pedido.objects.filter(usuario=request.user).order_by('-fecha_venta')
    serializer = HistorialSerializer(pedidos, many=True)
    return Response(serializer.data)

# --- WEBHOOK MERCADO PAGO ---

@api_view(['POST'])
@permission_classes([AllowAny])
def webhook_mercadopago(request):
    data = request.data
    payment_id = data.get("data", {}).get("id") or request.GET.get('data.id')
    
    if data.get("type") == "payment" and payment_id:
        try:
            sdk = mercadopago.SDK(settings.MP_ACCESS_TOKEN)
            payment_info = sdk.payment().get(payment_id)
            
            if payment_info["status"] == 200 and payment_info["response"]["status"] == "approved":
                pedido_id = payment_info["response"]["external_reference"]
                pedido = Pedido.objects.get(id=pedido_id)
                
                if pedido.estado in ['PENDIENTE', 'EN_PROCESO']:
                    pedido.estado = 'PAGADO'
                    pedido.save()
                    
                    # LOG DE COMPRA EXITOSA (MySQL)
                    log = CompraLog.objects.filter(referencia_pago=str(pedido.id)).first()
                    if log:
                        log.detalle_log += " [PAGO COMPLETADO EXITOSAMENTE]"
                        log.save()

                    print(f"--- [LOG] COMPRA #{pedido_id} FINALIZADA CON ÉXITO ---")

        except Exception as e:
            print(f"Error en Webhook: {str(e)}")

    return Response(status=200)


# vista de la lista de blog 
@api_view(['GET'])
@permission_classes([AllowAny]) # Ahora permitimos que la petición llegue siempre
def lista_posts(request):
    posts = Post.objects.all()
    serializer = PostSerializer(posts, many=True)
    return Response(serializer.data)

# vista del detalle de un post
@api_view(['GET'])
@permission_classes([AllowAny]) # Ahora permitimos que la petición llegue siempre
def detalle_post(request, slug):
    try:
        post = Post.objects.get(slug=slug)
        serializer = PostSerializer(post)
        return Response(serializer.data)
    except Post.DoesNotExist:
        return Response({"error": "Post no encontrado"}, status=status.HTTP_404_NOT_FOUND)
    


    # creacion de reseña 
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crear_reseña(request, producto_id):
    usuario = request.user
    # 1. Verificar si el usuario compró el producto alguna vez
    compro = ItemPedido.objects.filter(
        pedido__usuario=usuario, 
        producto_id=producto_id,
        pedido__estado='PAGADO' # Solo si el pedido está pago
    ).exists()

    if not compro:
        return Response(
            {"error": "Debes comprar el producto para dejar una reseña."}, 
            status=status.HTTP_403_FORBIDDEN
        )

    # 2. Guardar la reseña
    serializer = ReseñaSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(usuario=usuario, producto_id=producto_id)
        
        # LOG DE COMPRA (Instrucción 2026-01-06)
        print(f"LOG: Nueva reseña pendiente de moderación para producto ID {producto_id} por {usuario.email}")
        
        return Response({"mensaje": "Reseña enviada. Será visible tras moderación."}, status=201)
    
    return Response(serializer.errors, status=400)


@api_view(['GET'])
@permission_classes([AllowAny]) # Esto permite que React vea los testimonios sin loguearse
def lista_testimonios(request):
    # Traemos las reseñas moderadas
    reseñas = Reseña.objects.filter(moderado=True).order_by('-fecha')[:6]
    serializer = ReseñaSerializer(reseñas, many=True)
    return Response(serializer.data)



#Vista de productos destacados
@api_view(['GET'])
@permission_classes([AllowAny])
def lista_productos_destacdos(request):
    """
    Retorna los 4 productos mas reciente con stock.
    """
    productos = Producto.objects.filter(stock__gt=0).order_by('-fecha_creacion')[:3]

    #pasamos los datos para el serelizer 
    serializer = ProductoSerializer(productos, many=True)
    return Response(serializer.data)




# 1. Creamos una clase que NO valida el CSRF solo para envio de consultas 
class UnsafeSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return  # No hace nada, permitiendo el POST sin token

#vista parra las consultas de clientes
@csrf_exempt
@api_view(['POST'])
@authentication_classes([UnsafeSessionAuthentication])
@permission_classes([AllowAny])
def enviar_consulta(request):
    serializer = ConsultaSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"mensaje": "Consulta enviada con éxito."}, status=201)
    return Response(serializer.errors, status=400)