from django.urls import path
from .views import registro_api, CustomLogin, logout_api, me

urlpatterns = [
    path('registro/', registro_api, name='registro'),
    path('login/', CustomLogin.as_view(), name='login'),
    path('logout/', logout_api, name='logout'),
    path('me/', me, name='user-me'),
]