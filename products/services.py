import mercadopago
from django.conf import settings
from django.db import transaction
from .models import Producto, Pedido, ItemPedido

class CompraService:
    @staticmethod
    def ejecutar_pago_mercadopago(usuario, items_carrito):
        # 1. Validar que el Token exista en settings
        token = getattr(settings, 'MP_ACCESS_TOKEN', None)
        if not token:
            raise ValueError("Error de configuración: MP_ACCESS_TOKEN no encontrado en settings.")

        sdk = mercadopago.SDK(token)
        
        with transaction.atomic():
            # 2. Crear Pedido (estado por defecto PENDIENTE según tu modelo)
            nuevo_pedido = Pedido.objects.create(
                usuario=usuario, 
                total_pagado=0
            )
            
            total_acumulado = 0
            items_mp = []

            for item in items_carrito:
                p_id = item.get('producto_id')
                try:
                    producto = Producto.objects.select_for_update().get(pk=p_id)
                except Producto.DoesNotExist:
                    raise ValueError(f"El producto con ID {p_id} no existe.")

                cant = int(item.get('cantidad', 1))

                if producto.stock < cant:
                    raise ValueError(f"Stock insuficiente para {producto.nombre}. Disponible: {producto.stock}")

                precio = producto.precio_oferta if producto.en_oferta else producto.precio
                subtotal = precio * cant
                total_acumulado += subtotal

                # Guardar detalle de la venta
                ItemPedido.objects.create(
                    pedido=nuevo_pedido, 
                    producto=producto,
                    precio_unitario=precio, 
                    cantidad=cant
                )

                # Descontar stock
                producto.stock -= cant
                producto.save()

                # Preparar item para Mercado Pago
                items_mp.append({
                    "title": producto.nombre,
                    "quantity": cant,
                    "unit_price": float(precio), # MP exige float o decimal
                    "currency_id": "ARS"
                })

            # Actualizar el total final del pedido
            nuevo_pedido.total_pagado = total_acumulado
            nuevo_pedido.save()

            # 3. Crear Preferencia de Mercado Pago
            preference_data = {
                "items": items_mp,
                "external_reference": str(nuevo_pedido.id),
                "back_urls": {
                    # ASEGÚRATE DE QUE ESTAS URLS SEAN ACCESIBLES O ESTÉN BIEN FORMADAS
                    "success": "https://www.tu-sitio.com/success", 
                    "failure": "https://www.tu-sitio.com/failure",
                    "pending": "https://www.tu-sitio.com/pending"
                },
                "auto_return": "approved", # Requiere que 'success' esté definido arriba
                "notification_url": "https://tu-dominio.com/api/productos/webhook/mercadopago/", # Opcional si usas IPN
            }
            
            # Llamada al SDK
            preference_result = sdk.preference().create(preference_data)
            response = preference_result["response"]

            # --- VALIDACIÓN DE RESPUESTA DE MP ---
            if "init_point" not in response:
                # Si llegamos aquí, MP rechazó la petición (probablemente el Token)
                error_detalle = response.get("message", "Error desconocido de Mercado Pago")
                raise ValueError(f"Mercado Pago Error: {error_detalle}")
            
            return nuevo_pedido, preference_result["response"]