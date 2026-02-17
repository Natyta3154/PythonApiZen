from django.urls import path
from .views import actualizar_perfil, registro_api, login_api, logout_api, me

urlpatterns = [
    path('registro/', registro_api, name='registro'),
    path('login/', login_api, name='login'),
    path('logout/', logout_api, name='logout'),
    path('me/', me, name='user-me'),
    path('actualizar-perfil/', actualizar_perfil, name='actualizar-perfil'),
]