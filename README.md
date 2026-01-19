# Back Python Sahu

Este es el backend del proyecto "Sahu", construido con **Django** y **Django Rest Framework (DRF)**. Proporciona una API para gestionar usuarios, productos (con categorías y ofertas) y un sistema de blog (en desarrollo).

## 🚀 Características

*   **API RESTful**: Endpoints para consumo desde frontend (React, Vue, etc.).
*   **Gestión de Usuarios**: Autenticación mediante Tokens y Cookies.
*   **Catálogo de Productos**:
    *   Gestión de Categorías.
    *   Productos con detalles como aroma, precio, stock e imágenes.
    *   Sistema de Ofertas y Precios Promocionales.
*   **Logs de Compras**: Registro histórico de ventas.
*   **Almacenamiento en la Nube**: Integración con **Cloudinary** para gestionar imágenes de productos.
*   **Base de Datos**: Configurado para usar **MySQL**.

## 🛠 Atajos Tecnológicos

*   **Lenguaje**: Python 3.10+
*   **Framework Web**: Django
*   **API Toolkit**: Django Rest Framework
*   **CORS**: `django-cors-headers` habilitado para permitir peticiones cruzadas.
*   **Variables de Entorno**: `python-dotenv`
*   **Storage**: `django-cloudinary-storage`

## 📋 Requisitos Previos

*   Python 3.x instalado.
*   Servidor MySQL (local o remoto).
*   Cuenta de Cloudinary (para almacenamiento de imágenes).

## 🔧 Instalación y Configuración

Sigue estos pasos para levantar el proyecto en tu entorno local.

### 1. Clonar el repositorio
```bash
git clone <url-del-repositorio>
cd back_python_sahu
```

### 2. Crear y activar entorno virtual
```bash
# Crear entorno
python -m venv venv

# Activar en Windows
venv\Scripts\Activate

# Activar en Linux/Mac
source venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno
Crea un archivo `.env` en la raíz del proyecto (junto a `manage.py`) y define las siguientes variables:

```env
# Base de Datos
DB_Name=nombre_de_tu_db
DB_USER=tu_usuario
DB_PASSWORD=tu_contraseña
DB_HOST=localhost
DB_PORT=3306

# Cloudinary (Imágenes)
CLOUDINARY_CLOUD_NAME=tu_cloud_name
CLOUDINARY_API_KEY=tu_api_key
CLOUDINARY_API_SECRET=tu_api_secret
```
*Nota: Asegúrate de crear la base de datos en tu servidor MySQL antes de correr las migraciones.*

### 5. Aplicar Migraciones
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Crear un Superusuario (Opcional)
Para acceder al panel de administración de Django:
```bash
python manage.py createsuperuser
```

### 7. Iniciar el Servidor
```bash
python manage.py runserver
```

La API estará disponible en `http://127.0.0.1:8000/`.

## 📂 Estructura del Proyecto

*   `core/`: Configuraciones principales del proyecto (settings, urls, wsgi).
*   `users/`: Gestión de usuarios y autenticación.
*   `products/`: Modelos de Productos, Categorías y Registro de Compras.
*   `blog/`: Aplicación para el blog (estructura inicial).
*   `manage.py`: Script de gestión de Django.

## 📝 Comandos Útiles

*   **Activar entorno:** `venv\Scripts\Activate`
*   **Correr servidor:** `python manage.py runserver`
*   **Crear migración:** `python manage.py makemigrations`
*   **Aplicar migración:** `python manage.py migrate`

---
Generado automáticamente por Antigravity.
