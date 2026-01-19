from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.models import User
from .models import Producto, Categoria, CompraLog

class ProductsTests(APITestCase):
    def setUp(self):
        # Crear usuario para pruebas
        self.user = User.objects.create_user(username='testuser', password='testpassword123')
        
        # Crear categoría
        self.categoria = Categoria.objects.create(nombre="Jabones", descripcion="Jabones artesanales")
        
        # Crear productos
        self.producto_normal = Producto.objects.create(
            nombre="Jabon Lavanda",
            categoria=self.categoria,
            precio=10.00,
            stock=5,
            descripcion="Huele rico"
        )
        
        self.producto_oferta = Producto.objects.create(
            nombre="Jabon 3x1",
            categoria=self.categoria,
            precio=30.00,
            en_oferta=True,
            precio_oferta=20.00,
            stock=10,
            descripcion="Super oferta"
        )
        
        self.producto_sin_stock = Producto.objects.create(
            nombre="Jabon Agotado",
            categoria=self.categoria,
            precio=10.00,
            stock=0,
            descripcion="No hay"
        )

        # Cliente autenticado simulado usando force_authenticate
        # Aunque la app usa cookies, force_authenticate es lo más directo para tests unitarios de DRF
        self.client_auth = APIClient()
        self.client_auth.force_authenticate(user=self.user)

    def test_listar_productos_publico(self):
        url = reverse('lista-productos')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Deberíamos recibir 3 productos
        self.assertEqual(len(response.data), 3)

    def test_listar_ofertas_publico(self):
        url = reverse('lista-ofertas')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Deberíamos recibir 1 producto
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['nombre'], "Jabon 3x1")

    def test_comprar_producto_exitoso(self):
        url = reverse('realizar_compra', args=[self.producto_normal.id])
        
        # Usamos el cliente autenticado
        response = self.client_auth.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.producto_normal.refresh_from_db()
        
        # Verificar stock reducido
        self.assertEqual(self.producto_normal.stock, 4)
        
        # Verificar log de compra
        self.assertTrue(CompraLog.objects.filter(usuario=self.user, producto=self.producto_normal).exists())

    def test_comprar_producto_oferta(self):
        url = reverse('realizar_compra', args=[self.producto_oferta.id])
        response = self.client_auth.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        log = CompraLog.objects.get(usuario=self.user, producto=self.producto_oferta)
        
        # Verificar que se cobró el precio de oferta
        self.assertEqual(float(log.precio_final), 20.00)

    def test_comprar_sin_stock(self):
        url = reverse('realizar_compra', args=[self.producto_sin_stock.id])
        response = self.client_auth.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], "No hay stock disponible")

    def test_comprar_sin_autenticacion(self):
        url = reverse('realizar_compra', args=[self.producto_normal.id])
        # Cliente NO autenticado
        response = self.client.post(url)
        
        # Puede ser 401 o 403 dependiendo de la configuración exacta de DRF
        self.assertTrue(response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])
