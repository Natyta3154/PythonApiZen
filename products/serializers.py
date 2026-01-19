from rest_framework import serializers
from .models import Producto, Categoria, Pedido, ItemPedido # <--- IMPORTANTE: Añadir Pedido e ItemPedido aquí

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nombre', 'descripcion']

class ProductoSerializer(serializers.ModelSerializer):
    # Esto muestra el nombre de la categoría en lugar del ID
    categoria_nombre = serializers.ReadOnlyField(source='categoria.nombre')
    
    # Campo calculado para el Front: nos dice si hay stock sin enviar el número exacto
    hay_stock = serializers.SerializerMethodField()

    class Meta:
        model = Producto
        fields = [
            'id', 'nombre', 'categoria', 'categoria_nombre', 
            'aroma', 'precio', 'precio_oferta', 'en_oferta', 
            'stock', 'hay_stock', 'descripcion', 'imagen'
        ]

    def get_hay_stock(self, obj):
        return obj.stock > 0

class ItemPedidoSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.ReadOnlyField(source='producto.nombre')

    class Meta:
        model = ItemPedido
        # Quitamos 'pedido' de aquí para que no se repita la información dentro del historial
        fields = ['id', 'producto', 'producto_nombre', 'cantidad', 'precio_unitario']    

class HistorialSerializer(serializers.ModelSerializer):
    # Relacionamos los items que pertenecen a este pedido
    items = ItemPedidoSerializer(many=True, read_only=True)
    # get_estado_display devuelve el texto amigable (ej: "En Proceso") en vez de la clave
    estado_texto = serializers.CharField(source='get_estado_display', read_only=True)

    class Meta:
        model = Pedido
        fields = ['id', 'fecha_venta', 'total_pagado', 'estado', 'estado_texto', 'items']