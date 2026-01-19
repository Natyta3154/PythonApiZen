from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User

class UserTests(APITestCase):
    def test_registro_usuario(self):
        url = reverse('registro')
        data = {
            'username': 'newuser',
            'password': 'securepassword123',
            'email': 'new@mail.com'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='newuser').exists())
        # Verificar cookie set
        self.assertIn('auth_token', response.cookies)

    def test_login_usuario(self):
        # Crear usuario primero
        User.objects.create_user(username='loginuser', password='loginpass123')
        
        url = reverse('login')
        data = {
            'username': 'loginuser',
            'password': 'loginpass123'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verificar cookie set
        self.assertIn('auth_token', response.cookies)
        self.assertEqual(response.data['username'], 'loginuser')

    def test_registro_usuario_existente(self):
        User.objects.create_user(username='existing', password='pass')
        url = reverse('registro')
        data = {
            'username': 'existing',
            'password': 'newpass'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_credenciales_invalidas(self):
        User.objects.create_user(username='loginuser', password='loginpass123')
        url = reverse('login')
        data = {
            'username': 'loginuser',
            'password': 'wrongpassword'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
