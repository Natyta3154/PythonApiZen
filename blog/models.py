from django.utils import timezone
from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from products.models import Producto

# Modelo para el Blog
class Post(models.Model):
    titulo = models.CharField(max_length=200, verbose_name="Título")
    slug = models.SlugField(unique=True, max_length=200, blank=True)
    imagen = models.ImageField(upload_to='posts/', null=True, blank=True)
    contenido = models.TextField(verbose_name="Contenido del Post")
    fecha_publicacion = models.DateTimeField(default=timezone.now, verbose_name="Fecha de publicación")
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Autor del Post")

    #parra lo que se ve en el admin izquierda
    class Meta:
        verbose_name = "Blog "
        verbose_name_plural = "Blogs"
        ordering = ['-fecha_publicacion']

    def __str__(self):
        return self.titulo
    
    

class Reseña(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='reseñas')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    puntuacion = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Estrellas"
    )
    comentario = models.TextField(max_length=500)
    fecha = models.DateTimeField(auto_now_add=True)

    # Campo para moderación de reseñas primero se ve ne el admin luego se publica 
    moderado = models.BooleanField(default=False) 
