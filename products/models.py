from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

class Categoria(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Nombre de la Categoría")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"

class Producto(models.Model):
    nombre = models.CharField(max_length=200, verbose_name="Nombre del Producto")
    # Relación con categoría: null y blank True para evitar el error que tenías en el Admin
    categoria = models.ForeignKey(
        Categoria, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='productos', 
        verbose_name="Categoría"
    )
    aroma = models.CharField(max_length=100, verbose_name="Aroma", blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio")
    stock = models.IntegerField(default=0, verbose_name="Cantidad en Stock")
    descripcion = models.TextField(verbose_name="Descripción")
    
    # Sistema de Ofertas (como el 3x1)
    en_oferta = models.BooleanField(default=False, verbose_name="¿En Oferta?")
    precio_oferta = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Precio Promo")
    
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} ({self.aroma})"


# ENDPOINT  DE COMPRAS (CARRITO)
class Pedido(models.Model):
    # Definimos las opciones de estado como una constante para mayor orden
    ESTADOS_ENTREGA = [
        ('PENDIENTE', 'Pendiente'),
        ('EN_PROCESO', 'En Proceso'),
        ('PAGADO', 'Pagado - Preparando Envío'),
        ('ENTREGADO', 'Entregado'),
        ('CANCELADO', 'Cancelado'),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        verbose_name="Cliente"
    )
    fecha_venta = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Fecha de Venta"
    )
    total_pagado = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0, 
        verbose_name="Monto Total"
    )

    # El campo de estado con tus opciones específicas
    estado = models.CharField(
        max_length=20,
        choices=ESTADOS_ENTREGA,
        default='PENDIENTE',
        verbose_name="Estado de Entrega"
    )

    class Meta:
        verbose_name = "Venta Realizada"
        verbose_name_plural = "Ventas Realizadas"

    def __str__(self):
        # Ahora el nombre del pedido también mostrará el estado para identificarlo rápido
        return f"Venta #{self.id} - {self.usuario.username} ({self.get_estado_display()})"

# ENDPOINT DE DETALLE DE LA VENTA
class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, related_name='items', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2) # Precio capturado al momento de la venta

    class Meta:
        verbose_name = "Producto Vendido"
        verbose_name_plural = "Productos Vendidos"

    def __str__(self):
        return f"{self.producto.nombre} x {self.cantidad}"

# --- LOGS DE COMPRA (MySQL AlwaysData) ---
class CompraLog(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    pedido = models.ForeignKey(
        Pedido, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Pedido Relacionado"
    )
    referencia_pago = models.CharField(max_length=255, null=True, blank=True, verbose_name="Referencia MP")
    detalle_log = models.TextField(verbose_name="Detalle de la Actividad")
    monto = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Monto Registrado")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha del Log")

    class Meta:
        verbose_name = "Log de Compra"
        verbose_name_plural = "Logs de Compras"
        db_table = 'compras_logs' # Nombre exacto en MySQL

    def __str__(self):
        return f"LOG {self.id} | {self.usuario.username} | {self.fecha_creacion.strftime('%d/%m/%Y %H:%M')}"


class Consulta(models.Model):
    nombre = models.CharField(max_length=100)
    email = models.EmailField()
    asunto = models.CharField(max_length=200)
    mensaje = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)
    leido = models.BooleanField(default=False)

    def __str__(self):
        return f"Consulta de {self.nombre} - {self.asunto}"