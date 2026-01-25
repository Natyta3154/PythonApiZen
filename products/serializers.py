from rest_framework import serializers
from django.db.models import Avg
from .models import Consulta, Post, Producto, Categoria, Pedido, ItemPedido, Reseña

# 1. CATEGORÍAS
class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nombre', 'descripcion']

# 2. RESEÑAS (Debe ir antes de ProductoSerializer)
class ReseñaSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.ReadOnlyField(source='usuario.username')

    class Meta:
        model = Reseña
        fields = ['id', 'usuario_nombre', 'puntuacion', 'comentario', 'fecha']

# 3. PRODUCTOS (Unificado: Categoría + Reseñas + Stats)
class ProductoSerializer(serializers.ModelSerializer):
    # Relación con categoría
    categoria_nombre = serializers.ReadOnlyField(source='categoria.nombre')
    
    # Campos calculados y métodos
    hay_stock = serializers.SerializerMethodField()
    promedio_estrellas = serializers.SerializerMethodField()
    total_reseñas = serializers.SerializerMethodField()
    reseñas = serializers.SerializerMethodField()

    class Meta:
        model = Producto
        fields = [
            'id', 'nombre', 'categoria', 'categoria_nombre', 
            'aroma', 'precio', 'precio_oferta', 'en_oferta', 
            'stock', 'hay_stock', 'descripcion', 'imagen',
            'promedio_estrellas', 'total_reseñas', 'reseñas'
        ]

    def get_hay_stock(self, obj):
        return obj.stock > 0

    def get_reseñas(self, obj):
        # Solo reseñas aprobadas (moderado=True)
        queryset = obj.reseñas.filter(moderado=True)
        return ReseñaSerializer(queryset, many=True).data

    def get_promedio_estrellas(self, obj):
        promedio = obj.reseñas.filter(moderado=True).aggregate(Avg('puntuacion'))['puntuacion__avg']
        return round(promedio, 1) if promedio else 0

    def get_total_reseñas(self, obj):
        return obj.reseñas.filter(moderado=True).count()

# 4. CARRITO Y PEDIDOS
class ItemPedidoSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.ReadOnlyField(source='producto.nombre')

    class Meta:
        model = ItemPedido
        fields = ['id', 'producto', 'producto_nombre', 'cantidad', 'precio_unitario']

class HistorialSerializer(serializers.ModelSerializer):
    items = ItemPedidoSerializer(many=True, read_only=True)
    estado_texto = serializers.CharField(source='get_estado_display', read_only=True)

    class Meta:
        model = Pedido
        fields = ['id', 'fecha_venta', 'total_pagado', 'estado', 'estado_texto', 'items']

# 5. BLOG
class PostSerializer(serializers.ModelSerializer):
    fecha = serializers.DateTimeField(source='fecha_publicacion', format="%Y-%m-%d %H:%M:%S", read_only=True)
    autor_nombre = serializers.ReadOnlyField(source='autor.username')
   
    class Meta:
        model = Post
        fields = ['id', 'titulo', 'slug', 'imagen', 'contenido', 'fecha', 'autor_nombre']

# 6. CONSULTAS
class ConsultaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consulta
        fields = '__all__'