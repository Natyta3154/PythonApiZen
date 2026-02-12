

# blog/urls.py
from django.urls import path
from . import views 

urlpatterns = [
    path('posts/', views.gestionar_posts, name='blog-lista'), # Agregamos /posts/ para orden
    path('testimonios/', views.lista_testimonios, name='lista-testimonios'),
    path('reseñas/crear/<int:producto_id>/', views.crear_reseña, name='crear-reseña'),
    path('posts/<slug:slug>/', views.detalle_post, name='blog-detalle'),
]
