from django.urls import path
from . import views

urlpatterns = [
    # --- PRODUCTOS Y CATEGORÍAS ---
    path('lista/', views.lista_productos, name='lista-productos'),
    path('categorias/', views.lista_categorias, name='lista_categorias'),
    path('destacados/', views.lista_productos_destacados, name='productos-destacados'),
    path('ofertas/', views.lista_ofertas, name='lista-ofertas'),

    # --- PROCESO DE COMPRA Y LOGS (Instrucción 2026-01-06) ---
    path('comprar/', views.realizar_compra_carrito, name='realizar_compra_carrito'),
    path('mis-compras/', views.mis_compras, name='mis-compras'),
    path('webhook/mercadopago/', views.webhook_mercadopago, name='webhook_mp'),

    # --- CONTACTO ---
    path('consultas/', views.enviar_consulta, name='enviar_consulta'),
]