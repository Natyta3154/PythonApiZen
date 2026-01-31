

# blog/urls.py
from django.urls import path
from . import views 

urlpatterns = [
    path('', views.lista_posts, name='blog-lista'),
    path('<slug:slug>/', views.detalle_post, name='blog-detalle'),
    path('testimonios/', views.lista_testimonios, name='lista-testimonios'),
    path('reseñas/crear/<int:producto_id>/', views.crear_reseña, name='crear-reseña'),
]
