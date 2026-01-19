"""
Script de Pruebas para la API del Backend Django
Ejecutar: python test_api.py
"""

import requests
import json

BASE_URL = "http://localhost:8000"

# Colores para la terminal
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_test(name, passed, details=""):
    status = f"{Colors.GREEN}✓ PASÓ{Colors.END}" if passed else f"{Colors.RED}✗ FALLÓ{Colors.END}"
    print(f"{status} - {name}")
    if details:
        print(f"   {Colors.YELLOW}{details}{Colors.END}")
    print()

def test_productos_lista():
    """Prueba GET /api/productos/lista/"""
    try:
        response = requests.get(f"{BASE_URL}/api/productos/lista/")
        passed = response.status_code == 200
        details = f"Status: {response.status_code}, Productos encontrados: {len(response.json())}"
        print_test("GET /api/productos/lista/", passed, details)
        return response.json() if passed else []
    except Exception as e:
        print_test("GET /api/productos/lista/", False, f"Error: {str(e)}")
        return []

def test_productos_ofertas():
    """Prueba GET /api/productos/ofertas/"""
    try:
        response = requests.get(f"{BASE_URL}/api/productos/ofertas/")
        passed = response.status_code == 200
        details = f"Status: {response.status_code}, Ofertas encontradas: {len(response.json())}"
        print_test("GET /api/productos/ofertas/", passed, details)
        return response.json() if passed else []
    except Exception as e:
        print_test("GET /api/productos/ofertas/", False, f"Error: {str(e)}")
        return []

def test_registro():
    """Prueba POST /api/usuarios/registro/"""
    try:
        # Usar un timestamp para evitar duplicados
        import time
        timestamp = int(time.time())
        
        data = {
            "username": f"test_user_{timestamp}",
            "password": "test123456",
            "email": f"test_{timestamp}@example.com"
        }
        
        response = requests.post(f"{BASE_URL}/api/usuarios/registro/", json=data)
        passed = response.status_code == 201
        
        if passed:
            details = f"Status: {response.status_code}, Usuario creado: {response.json().get('username')}"
        else:
            details = f"Status: {response.status_code}, Error: {response.json()}"
        
        print_test("POST /api/usuarios/registro/", passed, details)
        return response.json() if passed else None
    except Exception as e:
        print_test("POST /api/usuarios/registro/", False, f"Error: {str(e)}")
        return None

def test_login(username="admin", password="admin"):
    """Prueba POST /api/usuarios/login/"""
    try:
        data = {
            "username": username,
            "password": password
        }
        
        response = requests.post(f"{BASE_URL}/api/usuarios/login/", json=data)
        passed = response.status_code == 200
        
        if passed:
            details = f"Status: {response.status_code}, Login exitoso para: {response.json().get('username')}"
            # Guardar cookies para pruebas autenticadas
            return response.cookies
        else:
            details = f"Status: {response.status_code}, Error: {response.json()}"
            print_test("POST /api/usuarios/login/", passed, details)
            return None
        
        print_test("POST /api/usuarios/login/", passed, details)
    except Exception as e:
        print_test("POST /api/usuarios/login/", False, f"Error: {str(e)}")
        return None

def test_mis_compras(cookies=None):
    """Prueba GET /api/productos/mis-compras/ (requiere autenticación)"""
    try:
        response = requests.get(f"{BASE_URL}/api/productos/mis-compras/", cookies=cookies)
        passed = response.status_code == 200
        
        if passed:
            compras = response.json()
            details = f"Status: {response.status_code}, Compras encontradas: {len(compras)}"
        else:
            details = f"Status: {response.status_code}, Error: {response.text}"
        
        print_test("GET /api/productos/mis-compras/", passed, details)
        return response.json() if passed else []
    except Exception as e:
        print_test("GET /api/productos/mis-compras/", False, f"Error: {str(e)}")
        return []

def test_realizar_compra(cookies=None, producto_id=1):
    """Prueba POST /api/productos/comprar/ (requiere autenticación)"""
    try:
        data = {
            "items": [
                {
                    "producto_id": producto_id,
                    "cantidad": 1
                }
            ]
        }
        
        response = requests.post(f"{BASE_URL}/api/productos/comprar/", json=data, cookies=cookies)
        passed = response.status_code in [200, 201]
        
        if passed:
            result = response.json()
            details = f"Status: {response.status_code}, Pedido ID: {result.get('pedido_id')}, Total: ${result.get('total')}"
        else:
            details = f"Status: {response.status_code}, Error: {response.json()}"
        
        print_test("POST /api/productos/comprar/", passed, details)
        return response.json() if passed else None
    except Exception as e:
        print_test("POST /api/productos/comprar/", False, f"Error: {str(e)}")
        return None

def main():
    print(f"\n{Colors.BLUE}{'='*60}")
    print("🧪 PRUEBAS DE LA API - Backend Django")
    print(f"{'='*60}{Colors.END}\n")
    
    print(f"{Colors.BLUE}📋 Pruebas de Endpoints Públicos{Colors.END}\n")
    
    # 1. Probar listado de productos
    productos = test_productos_lista()
    
    # 2. Probar listado de ofertas
    ofertas = test_productos_ofertas()
    
    print(f"{Colors.BLUE}👤 Pruebas de Autenticación{Colors.END}\n")
    
    # 3. Probar registro de usuario
    nuevo_usuario = test_registro()
    
    # 4. Probar login (intentar con usuario admin por defecto)
    print(f"{Colors.YELLOW}Nota: Intentando login con usuario 'admin'. Si falla, crea un superusuario primero.{Colors.END}\n")
    cookies = test_login("admin", "admin")
    
    if cookies:
        print(f"{Colors.BLUE}🛒 Pruebas de Funcionalidad Autenticada{Colors.END}\n")
        
        # 5. Probar historial de compras
        compras = test_mis_compras(cookies)
        
        # 6. Probar realizar compra (solo si hay productos)
        if productos and len(productos) > 0:
            producto_id = productos[0]['id']
            print(f"{Colors.YELLOW}Intentando comprar producto ID: {producto_id}{Colors.END}\n")
            test_realizar_compra(cookies, producto_id)
        else:
            print(f"{Colors.YELLOW}⚠ No hay productos para probar la compra{Colors.END}\n")
    else:
        print(f"{Colors.RED}⚠ No se pudo autenticar. Saltando pruebas autenticadas.{Colors.END}\n")
        print(f"{Colors.YELLOW}Crea un superusuario con: python manage.py createsuperuser{Colors.END}\n")
    
    print(f"{Colors.BLUE}{'='*60}")
    print("✅ Pruebas completadas")
    print(f"{'='*60}{Colors.END}\n")

if __name__ == "__main__":
    main()
