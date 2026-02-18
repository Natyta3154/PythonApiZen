from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import CompraLog, Producto, Categoria, ItemPedido, Pedido, Consulta
from blog.models import Post
# --- CONFIGURACIÓN DE ENCABEZADOS ---
admin.site.site_header = "Panel de Control - Sahumerios AromaZen"
admin.site.site_title = "AromaZen Admin"
admin.site.index_title = "Gestión de Ventas y Productos"

# --- PRODUCTOS ---
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('id', 'imagen_preview', 'nombre', 'aroma', 'precio_original_display', 'oferta_status', 'precio_oferta_display', 'stock_status')
    list_filter = ('en_oferta', 'categoria')
    search_fields = ('nombre', 'aroma')
    list_per_page = 20

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
            return format_html('<b style="color: red; font-weight: bold;">¡Solo {} unidades!</b>', obj.stock)
        return obj.stock
    stock_status.short_description = "Stock"

    def imagen_preview(self, obj):
        if obj.imagen:
            return format_html('<img src="{}" style="width: 45px; height: 45px; border-radius: 5px; object-fit: cover;" />', obj.imagen.url)
        return "🖼️"
    imagen_preview.short_description = 'Imagen'

# --- CATEGORÍAS ---
@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')
    search_fields = ('nombre',)

# --- GESTIÓN DE PEDIDOS ---
class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    readonly_fields = ('producto', 'cantidad', 'precio_unitario')
    extra = 0
    can_delete = False

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'fecha_venta', 'total_pagado', 'estado', 'estado_badge')
    list_editable = ('estado',) 
    list_filter = ('estado', 'fecha_venta')
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
            '<span style="color: white; background-color: {}; padding: 4px 10px; border-radius: 12px; font-weight: bold; font-size: 11px;">{}</span>',
            colores.get(obj.estado, '#000'),
            obj.get_estado_display()
        )
    estado_badge.short_description = "Visualización"


# --- AUDITORÍA Y LOGS DE COMPRA ---
@admin.register(CompraLog)
class CompraLogAdmin(admin.ModelAdmin):
    # ✅ Agregamos 'referencia_pago' a la lista principal
    list_display = ('id', 'usuario', 'referencia_display', 'monto', 'fecha_creacion', 'tipo_log_badge')
    list_filter = ('fecha_creacion',)
    search_fields = ('referencia_pago', 'usuario__username') # Permite buscar por el ID de MP
    readonly_fields = ('referencia_pago', 'usuario', 'pedido', 'detalle_log', 'monto', 'fecha_creacion')

    # ✨ Una función para que el ID de MP se vea más profesional
    def referencia_display(self, obj):
        if obj.referencia_pago and len(obj.referencia_pago) > 5:
            return format_html('<code style="color: #2e6da4; font-weight: bold;">{}</code>', obj.referencia_pago)
        return obj.referencia_pago or "-"
    referencia_display.short_description = "Referencia MP"

    def tipo_log_badge(self, obj):
        return mark_safe(
            '<span style="background-color: #5bc0de; color: white; padding: 3px 8px; border-radius: 5px; font-size: 10px; font-weight: bold;">LOG SISTEMA</span>'
        )
    tipo_log_badge.short_description = "Categoría Log"
# --- CONSULTAS ---
@admin.register(Consulta)
class ConsultaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'email', 'asunto', 'fecha', 'leido')
    list_filter = ('fecha', 'leido')
    list_editable = ('leido',)
    search_fields = ('nombre', 'email', 'asunto')
    ordering = ('-fecha',)