from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.utils.html import format_html
from .models import Post, Reseña  # Importación local, más limpia

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'imagen_preview', 'titulo', 'autor', 'fecha_publicacion')
    prepopulated_fields = {'slug': ('titulo',)}
    search_fields = ('titulo', 'contenido')
    list_filter = ('fecha_publicacion', 'autor')
    fields = ('titulo', 'slug', 'autor', 'imagen', 'contenido', 'fecha_publicacion')

    def imagen_preview(self, obj):
        if obj.imagen:
            return format_html('<img src="{}" style="width: 50px; height: auto; border-radius: 5px;" />', obj.imagen.url)
        return "📝"
    imagen_preview.short_description = 'Vista'



@admin.register(Reseña)
class ReseñaAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'producto', 'puntuacion', 'moderado', 'fecha')
    list_filter = ('moderado', 'puntuacion')
    list_editable = ('moderado',)
    actions = ['aprobar_reseñas']

    @admin.action(description='Aprobar reseñas seleccionadas')
    def aprobar_reseñas(self, request, queryset):
        queryset.update(moderado=True)