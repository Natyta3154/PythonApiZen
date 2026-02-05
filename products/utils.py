# products/utils.py
from django.core.mail import send_mail
from django.conf import settings

def enviar_confirmacion_compra(pedido):
    asunto = f"🧘 ¡Gracias por tu compra en Aroma Zen! (Pedido #{pedido.id})"
    mensaje = f"""
    Hola {pedido.usuario.first_name or pedido.usuario.username},
    
    ¡Tu pago ha sido confirmado con éxito! 
    
    Detalles de tu pedido:
    - ID: #{pedido.id}
    - Total: ${pedido.total_pagado}
    - Fecha: {pedido.fecha_venta.strftime('%d/%m/%Y')}
    
    Estamos preparando tu envío con toda la calma y energía zen.
    Te avisaremos cuando esté en camino.
    """
    
    send_mail(
        asunto,
        mensaje,
        settings.DEFAULT_FROM_EMAIL,
        [pedido.usuario.email],
        fail_silently=False,
    )