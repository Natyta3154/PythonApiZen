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
from rest_framework.authentication import SessionAuthentication

# Autenticación personalizada
from users.authentication import CookieTokenAuthentication, CsrfExemptSessionAuthentication

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

@api_view(['POST'])
@authentication_classes([CookieTokenAuthentication, CsrfExemptSessionAuthentication])
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

@api_view(['POST'])
@permission_classes([AllowAny])
def webhook_mercadopago(request):
    data = request.data
    # Obtenemos el ID del pago, ya sea por el cuerpo (POST) o por parámetros de URL (GET)
    payment_id = data.get("data", {}).get("id") or request.GET.get('data.id')
    
    if data.get("type") == "payment" and payment_id:
        try:
            sdk = mercadopago.SDK(settings.MP_ACCESS_TOKEN)
            payment_info = sdk.payment().get(payment_id)
            
            if payment_info["status"] == 200 and payment_info["response"]["status"] == "approved":
                pedido_id = payment_info["response"]["external_reference"]
                pedido = Pedido.objects.get(id=pedido_id)
                
                # Solo procesamos si el pedido no está pagado aún (evita duplicados)
                if pedido.estado in ['PENDIENTE', 'EN_PROCESO']:
                    pedido.estado = 'PAGADO'
                    pedido.save()
                    
                    # 1. ACTUALIZACIÓN DEL LOG DE COMPRA PERSISTENTE
                    log = CompraLog.objects.filter(referencia_pago=str(pedido.id)).first()
                    log_msg = " [PAGO APROBADO MP]"
                    
                    # 2. INTENTO DE ENVÍO DE EMAIL PROFESIONAL
                    try:
                        enviar_confirmacion_compra(pedido)
                        log_msg += " [EMAIL ENVIADO]"
                        print(f"--- [LOG] EMAIL ENVIADO EXITOSAMENTE A {pedido.usuario.email} ---")
                    except Exception as e_mail:
                        log_msg += f" [ERROR EMAIL: {str(e_mail)}]"
                        print(f"--- [ERROR LOG] Falló el envío de mail: {str(e_mail)} ---")

                    # Guardamos todo el historial en el detalle del log
                    if log:
                        log.detalle_log += log_msg
                        log.save()

                    print(f"--- [LOG] COMPRA #{pedido_id} FINALIZADA CON ÉXITO ---")

        except Exception as e:
            print(f"Error crítico en Webhook: {str(e)}")
            # No devolvemos error a MP para evitar que reintente infinitamente si es un error de nuestro código
    
    # Mercado Pago espera siempre un 200 o 201 para dejar de notificar
    return Response(status=200)

@api_view(['GET'])
@authentication_classes([CookieTokenAuthentication, CsrfExemptSessionAuthentication])
@permission_classes([IsAuthenticated])
def mis_compras(request):
    pedidos = Pedido.objects.filter(usuario=request.user).order_by('-fecha_venta')
    serializer = HistorialSerializer(pedidos, many=True)
    return Response(serializer.data)

# --- CONSULTAS ---

class UnsafeSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return 

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