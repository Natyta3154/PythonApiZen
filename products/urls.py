from products.views import webhook_mercadopago
from django.urls import path
from .views import lista_productos # La vista que creamos antes
from .views import lista_ofertas # La vista que creamos antes
from .views import realizar_compra_carrito # La vista que creamos antes
from .views import mis_compras # La vista que creamos antes
urlpatterns = [
    # La ruta real será: http://localhost:8000/api/products/lista/
    path('lista/', lista_productos, name='lista-productos'),
    path('ofertas/', lista_ofertas, name='lista-ofertas'),
    path('comprar/', realizar_compra_carrito, name='realizar_compra_carrito'),
    path('mis-compras/', mis_compras, name='mis-compras'),
    path('webhook/mercadopago/', webhook_mercadopago, name='webhook_mp'),
]