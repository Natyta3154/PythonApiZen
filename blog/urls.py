


from django.urls import path

from products.views import lista_testimonios

from django.urls import path
from .views import lista_posts, detalle_post

urlpatterns = [
    path('', lista_posts, name='blog-lista'),
    path('<slug:slug>/', detalle_post, name='blog-detalle'),
    path('testimonios/', lista_testimonios, name='testimonios'),
]


