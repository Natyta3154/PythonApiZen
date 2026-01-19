import mercadopago
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny 
from rest_framework.response import Response
from rest_framework import status
from .models import CompraLog, Producto, Pedido
from .serializers import ProductoSerializer, HistorialSerializer
from .services import CompraService
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.authentication import SessionAuthentication



# --- LISTADOS ---
@api_view(['GET'])
@permission_classes([AllowAny])
def lista_productos(request):
    serializer = ProductoSerializer(Producto.objects.all(), many=True)
    return Response(serializer.data)


# Coloca esta clase arriba de tu función
class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return  # Esto desactiva la verificación CSRF para esta petición

@api_view(['GET'])
@permission_classes([AllowAny]) 
def lista_ofertas(request):
    serializer = ProductoSerializer(Producto.objects.filter(en_oferta=True), many=True)
    return Response(serializer.data)

# --- PROCESAR COMPRA REAL ---
@api_view(['POST'])
@authentication_classes([CsrfExemptSessionAuthentication]) # 1. Primero identificamos quién es
@permission_classes([IsAuthenticated])
def realizar_compra_carrito(request):
    items = request.data.get('items', [])
    if not items:
        return Response({"error": "Carrito vacío"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # 1. Llamada al servicio que integra Mercado Pago
        pedido, mp_response = CompraService.ejecutar_pago_mercadopago(request.user, items)
        
        # 2. LOG DE COMPRA PERSISTENTE (MySQL)
        # Ajustado a los nombres de campos que definimos en models.py
        CompraLog.objects.create(
            usuario=request.user,
            pedido=pedido,
            detalle_log=f"Iniciado pago de Pedido #{pedido.id} via Mercado Pago. Contiene {len(items)} productos.",
            monto=pedido.total_pagado,
            referencia_pago=str(pedido.id) 
        )

        return Response({
            "pedido_id": pedido.id,
            "preference_id": mp_response.get("id"), # <--- ESTO ES LO QUE NECESITA REACT
            "url_pago": mp_response.get("init_point"), # Por si quieres usar redirección simple
            "total": pedido.total_pagado
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        import traceback
        traceback.print_exc()
        
        # También registramos el error en los Logs si quieres trazabilidad de fallos
        # (Opcional, pero muy útil para soporte)
        return Response({
            "error": "Error al procesar el pago",
            "detalle_tecnico": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# --- HISTORIAL ---
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mis_compras(request):
    pedidos = Pedido.objects.filter(usuario=request.user).order_by('-fecha_venta')
    serializer = HistorialSerializer(pedidos, many=True)
    return Response(serializer.data)





#El Webhook es el endpoint que recibe las notificaciones de Mercado Pago cuando Mercado Pago nos confirma el éxito.
@api_view(['POST'])
@permission_classes([AllowAny])
def webhook_mercadopago(request):
    data = request.data
    payment_id = data.get("data", {}).get("id") or request.GET.get('data.id')
    
    if data.get("type") == "payment" and payment_id:
        try:
            sdk = mercadopago.SDK(settings.MP_ACCESS_TOKEN)
            payment_info = sdk.payment().get(payment_id)
            
            if payment_info["response"]["status"] == "approved":
                # Obtenemos el ID de nuestra "Venta Realizada"
                pedido_id = payment_info["response"]["external_reference"]
                pedido = Pedido.objects.get(id=pedido_id)
                
                # Solo actualizamos si está en PENDIENTE o EN_PROCESO
                if pedido.estado in ['PENDIENTE', 'EN_PROCESO']:
                    pedido.estado = 'PAGADO' # Tu opción: 'Pagado - Preparando Envío'
                    pedido.save()
                    
                    # LOG DE COMPRA (Instrucción 2026-01-06)
            log = CompraLog.objects.filter(referencia_pago=str(pedido.id)).first()
            if log:
                log.producto_nombre += " [PAGADO COMPLETADO]"
                log.save()

            print(f"--- [LOG] COMPRA FINALIZADA EN BASE DE DATOS ---")

        except Pedido.DoesNotExist:
            print(f"Error: Venta #{pedido_id} no encontrada en la base de datos.")
        except Exception as e:
            print(f"Error en Webhook: {str(e)}")

    return Response(status=200)