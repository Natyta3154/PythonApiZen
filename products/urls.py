
from products.views import webhook_mercadopago
from django.urls import path
from .views import crear_reseña, detalle_post, enviar_consulta, lista_categorias, lista_posts, lista_productos, lista_productos_destacdos, lista_testimonios # La vista que creamos antes
from .views import lista_ofertas # La vista que creamos antes
from .views import realizar_compra_carrito # La vista que creamos antes
from .views import mis_compras # La vista que creamos antes

urlpatterns = [
    path('lista/', lista_productos, name='lista-productos'),
    path('categorias/', lista_categorias, name='lista_categorias'),
    path('destacados/', lista_productos_destacdos, name='productos-destacados'),
    path('ofertas/', lista_ofertas, name='lista-ofertas'),
    path('comprar/', realizar_compra_carrito, name='realizar_compra_carrito'),
    path('mis-compras/', mis_compras, name='mis-compras'),
    path('webhook/mercadopago/', webhook_mercadopago, name='webhook_mp'),
    path('blog/', lista_posts, name='lista-blog'),
    path('blog/<slug:slug>/', detalle_post, name='detalle-blog'),
    path('consultas/', enviar_consulta, name='enviar_consulta'),
    
    # 1. ESTA ES PARA EL HOME (GET) - Es la que Axios busca ahora
    path('testimonios/', lista_testimonios, name='lista-testimonios'),

    # 2. ESTA ES PARA CREAR (POST) - Debes cambiarle el nombre a la URL
    # Además, la función crear_reseña necesita el producto_id
    path('reseñas/crear/<int:producto_id>/', crear_reseña, name='crear-reseña'),
]