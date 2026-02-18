from django.db import transaction
import mercadopago
import datetime
import traceback
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from .utils import enviar_confirmacion_compra
# Rest Framework
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny 
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication, SessionAuthentication 


# MODELOS LOCALES (Solo de productos)
from .models import CompraLog, ItemPedido, Producto, Pedido, Consulta, Categoria

# SERIALIZERS LOCALES
from .serializers import (
    ConsultaSerializer, ProductoSerializer, HistorialSerializer, 
    CategoriaSerializer
)

from .services import CompraService

# --- LISTADOS DE TIENDA ---

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

@api_view(['GET'])
@permission_classes([AllowAny])
def lista_categorias(request):
    categorias = Categoria.objects.all()
    serializer = CategoriaSerializer(categorias, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def lista_productos_destacados(request): # Corregido el nombre (agregada la 'i')
    productos = Producto.objects.filter(stock__gt=0).order_by('-fecha_creacion')[:3]
    serializer = ProductoSerializer(productos, many=True)
    return Response(serializer.data)

# --- PROCESO DE COMPRA Y LOGS ---
# ----En realizar_compra_carrito: Creas el pedido, descuentas el stock y generas el primer Log Persistente en MySQL y en consola. Aquí el pedido nace como PENDIENTE.-----
@api_view(['POST'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def realizar_compra_carrito(request):
    items = request.data.get('items', [])
    if not items:
        return Response({"error": "Carrito vacío"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # 📝 LOG DE CONSOLA (Instrucción 2026-01-06)
        print(f"\n--- [LOG DE COMPRA] {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")
        print(f"USUARIO: {request.user.username} (ID: {request.user.id})")
        
        pedido, mp_response = CompraService.ejecutar_pago_mercadopago(request.user, items)
        
        # 📝 LOG PERSISTENTE EN MYSQL
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

    except Exception as e:
        traceback.print_exc()
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

from .utils import enviar_confirmacion_compra # Importa la función que creamos



#---En webhook_mercadopago: Cuando el pago se aprueba, el servidor de Mercado Pago avisa a tu API. Tu código busca el pedido por external_reference, lo marca como PAGADO y actualiza el log indicando que el email fue enviado.
@csrf_exempt
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
                payment_id_real = payment_info["response"]["id"]
                pedido = Pedido.objects.get(id=pedido_id)
                
                if pedido.estado in ['PENDIENTE', 'EN_PROCESO']:
                    # --- NUEVA LÓGICA DE STOCK ---
                    with transaction.atomic():
                        # Buscamos los items que el usuario compró en este pedido
                        items_pedido = ItemPedido.objects.filter(pedido=pedido)
                        for item in items_pedido:
                            producto = item.producto
                            # Descontamos el stock aquí, al confirmar el pago
                            producto.stock -= item.cantidad
                            producto.save()
                            print(f"[LOG STOCK] Descontados {item.cantidad} de {producto.nombre}")

                        # Ahora sí, marcamos como pagado
                        pedido.estado = 'PAGADO'
                        pedido.save()
                    
                    # 1. ACTUALIZACIÓN DEL LOG (Instrucción 2026-01-06)
                    # Buscamos el log que creamos al inicio (que tiene el ID del pedido como referencia temporal)
                    log = CompraLog.objects.filter(referencia_pago=str(pedido.id)).first()
                    if log:
                        log.referencia_pago = str(payment_id_real)  # Actualizamos con el ID real de MP
                        log.detalle_log += " [PAGO APROBADO]"
                        log.save()


                    log_msg = " [PAGO APROBADO Y STOCK ACTUALIZADO]"
                    
                    # 2. ENVÍO DE EMAIL
                    try:
                        enviar_confirmacion_compra(pedido)
                        log_msg += " [EMAIL ENVIADO]"
                    except Exception as e_mail:
                        log_msg += f" [ERROR EMAIL: {str(e_mail)}]"

                    if log:
                        log.detalle_log += log_msg
                        log.save()

        except Exception as e:
            print(f"Error crítico en Webhook: {str(e)}")
    
    return Response(status=200)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mis_compras(request):
    pedidos = Pedido.objects.filter(usuario=request.user).order_by('-fecha_venta')
    serializer = HistorialSerializer(pedidos, many=True)
    return Response(serializer.data)

 


@api_view(['POST'])
@permission_classes([AllowAny])
def enviar_consulta(request):
    serializer = ConsultaSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"mensaje": "Consulta enviada con éxito."}, status=201)
    return Response(serializer.errors, status=400)