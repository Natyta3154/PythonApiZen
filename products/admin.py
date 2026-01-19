from django.contrib import admin
from django.utils.html import format_html
from .models import CompraLog, Producto, Categoria, ItemPedido, Pedido
# Nuevas importaciones para las métricas
from django.db.models import Sum
from django.utils import timezone

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'aroma', 'precio_original_display', 'oferta_status', 'precio_oferta_display', 'stock_status', 'imagen_preview')
    list_filter = ('en_oferta', 'categoria')
    search_fields = ('nombre',)

    def precio_original_display(self, obj):
        return f"${obj.precio}"
    precio_original_display.short_description = 'Precio Base'

    def oferta_status(self, obj):
        if obj.en_oferta:
            return format_html('<span style="color: #d9534f; font-weight: bold;">🔥 EN OFERTA</span>')
        return "Normal"
    oferta_status.short_description = 'Estado'

    def precio_oferta_display(self, obj):
        if obj.en_oferta and obj.precio_oferta:
            return format_html('<b style="color: #5cb85c;">${}</b>', obj.precio_oferta)
        return "-"
    precio_oferta_display.short_description = 'Precio Promo'

    def stock_status(self, obj):
        if obj.stock <= 5:
            return format_html('<b style="color: red;">¡Solo {}!</b>', obj.stock)
        return obj.stock
    stock_status.short_description = "Stock"

    def imagen_preview(self, obj):
        if obj.imagen:
            return format_html('<img src="{}" style="width: 50px; height: auto; border-radius: 5px;" />', obj.imagen.url)
        return "Sin imagen"
    imagen_preview.short_description = 'Vista'

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')
    search_fields = ('nombre',)

class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    readonly_fields = ('producto', 'cantidad', 'precio_unitario')
    extra = 0
    can_delete = False

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'fecha_venta', 'total_pagado', 'estado', 'estado_badge')
    list_editable = ('estado',) 
    list_filter = ('estado', 'fecha_venta', 'usuario')
    inlines = [ItemPedidoInline]
    readonly_fields = ('usuario', 'fecha_venta', 'total_pagado')

    def estado_badge(self, obj):
        colores = {
            'PENDIENTE': '#d9534f',
            'EN_PROCESO': '#f0ad4e',
            'ENTREGADO': '#5cb85c',
            'CANCELADO': '#777',
        }
        return format_html(
            '<span style="color: white; background-color: {}; padding: 3px 10px; border-radius: 10px; font-weight: bold; font-size: 10px;">{}</span>',
            colores.get(obj.estado, '#000'),
            obj.get_estado_display()
        )
    estado_badge.short_description = "Visual"

# --- LÓGICA DEL DASHBOARD DE MÉTRICAS ---

# Guardamos la función original de index para no perderla
original_index = admin.site.index

def custom_index(request, extra_context=None):
    # 1. Ventas del mes actual
    hoy = timezone.now()
    inicio_mes = hoy.replace(day=1, hour=0, minute=0, second=0)
    total_mes = Pedido.objects.filter(fecha_venta__gte=inicio_mes).exclude(estado='CANCELADO').aggregate(Sum('total_pagado'))['total_pagado__sum'] or 0

    # 2. Conteo de pedidos críticos
    pendientes = Pedido.objects.filter(estado='PENDIENTE').count()

    # 3. Producto Estrella
    top_item = ItemPedido.objects.values('producto__nombre').annotate(total=Sum('cantidad')).order_by('-total').first()

    # Creamos el diccionario de métricas
    metricas = {
        'total_mes': total_mes,
        'pendientes': pendientes,
        'top_nombre': top_item['producto__nombre'] if top_item else "N/A",
        'top_cantidad': top_item['total'] if top_item else 0,
    }

    # Lo añadimos al contexto
    extra_context = extra_context or {}
    extra_context['metricas'] = metricas
    
    return original_index(request, extra_context)



# Reemplazamos el index original por el nuestro
admin.site.index = custom_index

# Configuración final
admin.site.site_header = "Panel de Control - Sahumerios"
admin.site.site_title = "Sahumerios Admin"
admin.site.index_title = "Gestión de Ventas y Productos"



@admin.register(CompraLog)
class CompraLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'monto', 'fecha_creacion', 'tipo_log_badge')
    list_filter = ('fecha_creacion', 'usuario')
    readonly_fields = ('usuario', 'pedido', 'detalle_log', 'monto', 'fecha_creacion')

    def tipo_log_badge(self, obj):
        # Esto le da color a tus logs para diferenciarlos de las ventas
        return format_html(
            '<span style="background-color: #5bc0de; color: white; padding: 2px 8px; border-radius: 5px; font-size: 10px;">LOG TÉCNICO</span>'
        )
    tipo_log_badge.short_description = "Tipo"