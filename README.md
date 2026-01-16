# Sistema de Gestión de Stock & API REST

![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![Django](https://img.shields.io/badge/django-5.0-green.svg)
![DRF](https://img.shields.io/badge/API-Django_REST_Framework-red)
![Swagger](https://img.shields.io/badge/docs-Swagger_UI-85ea2d.svg)
![Postgres](https://img.shields.io/badge/database-postgres-blue)
![Render](https://img.shields.io/badge/deploy-render-black)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)

> 🚀 **Demo En Vivo:** [LIVE](https://sistema-stock-alejo-rossi.onrender.com/)
>
> **Credenciales de Demo:**
> * **Usuario:** `admin`
> * **Contraseña:** `1234`

## 📋 Descripción del Proyecto

Sistema integral de gestión de inventarios desarrollado con **Django**. Diseñado para escalar, cuenta con una interfaz web para administración de oficina y una **API RESTful** completa lista para integrarse con aplicaciones móviles o clientes externos.

El sistema implementa lógica de negocio robusta, auditoría de movimientos de stock y autenticación segura basada en Tokens.

## ✨ Características Principales

### 🖥️ Módulo Web (Backend + Frontend)
* **Dashboard Administrativo:** Gestión visual de productos y categorías.
* **Control de Stock Transaccional:** Sistema de auditoría que registra cada entrada y salida (no permite edición directa del stock para garantizar trazabilidad).
* **Buscador Inteligente:** Filtrado en tiempo real por nombre, SKU o categoría usando QuerySets avanzados.
* **Seguridad:** Protección de rutas, CSRF tokens y login de usuarios.
* **Interfaz Responsiva:** Diseño adaptado a móviles con Bootstrap 5.

### 📱 Módulo API (Mobile Ready)
* **Endpoints RESTful:** CRUD completo accesible vía JSON (`/api/products/`).
* **Autenticación por Tokens:** Implementación de `TokenAuthentication` para clientes móviles (Android/iOS).
* **Documentación Automática:**
    * **Swagger UI:** Interfaz interactiva para probar endpoints (`/api/docs/`).
    * **Redoc:** Documentación técnica limpia (`/api/redoc/`).

### ⚡ Microservicio de Reportes (Arquitectura Distribuida)
* **Generación de PDFs:** Se separó la lógica de generación de documentos en un microservicio independiente construido con **FastAPI**.
* **Comunicación Síncrona:** Django se comunica vía HTTP (`requests`) con el microservicio, enviando datos en JSON y recibiendo el archivo binario generado al vuelo.

## 🛠️ Stack Tecnológico

* **Lenguaje:** Python 3
* **Framework Web:** Django 5
* **API Framework:** Django REST Framework (DRF)
* **Documentación API:** drf-spectacular (OpenAPI 3.0)
* **Base de Datos:** PostgreSQL (Producción) / SQLite (Dev)
* **Frontend:** Django Templates + Bootstrap 5
* **Infraestructura:** Gunicorn, Whitenoise, Render (PaaS), Neon (DBaaS)

## 🔧 Instalación Local

Si deseas clonar y correr este proyecto en tu máquina:

1. **Clonar el repositorio:**
   ```bash
   git clone [https://github.com/alejfrossi/sistema-gestion-stock.git](https://github.com/alejfrossi/sistema-gestion-stock.git)
   cd sistema-gestion-stock

2. **Crear y activar entorno virtual:**
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # Mac/Linux:
   source venv/bin/activate

3. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt

4. **Configurar variables de entorno: Crea un archivo .env en la raíz y define:**
   ```Ini, TOML
   DEBUG=True
   SECRET_KEY=tu_clave_secreta
   # Si usas Postgres local:
   DB_NAME=stock_db
   DB_USER=postgres
   DB_PASSWORD=tu_password

5. **Ejecutar el Sistema (Arquitectura de Microservicios):**

   El sistema requiere dos terminales abiertas simultáneamente:

   **Terminal 1 (Django - Core App):**
   ```bash
   python src/manage.py runserver
   
**Terminal 2 (FastAPI - Microservicio):** (Asegúrate de tener el entorno virtual activado)
   ```bash
   uvicorn microservice.main:app --reload --port 8001

Ahora ingresa a http://127.0.0.1:8000. Al solicitar un reporte, Django delegará la tarea al puerto 8001 automáticamente.

## 📖 Documentación de la API

Una vez iniciado el servidor, puedes acceder a la documentación interactiva en:

* **Swagger:** [http://127.0.0.1:8000/api/docs/](http://127.0.0.1:8000/api/docs/)
* **Redoc:** [http://127.0.0.1:8000/api/redoc/](http://127.0.0.1:8000/api/redoc/)

## 🧠 Decisiones de Arquitectura

* **Estructura 'src':** Se utilizó el patrón de carpeta src para mantener limpia la raíz del proyecto y separar la configuración del código fuente.
* **Fat Models:** La lógica de cálculo de stock se encapsuló en el método save() del modelo StockMovement para evitar inconsistencias de datos en las vistas.
* **CORS:** Configurado con django-cors-headers para permitir peticiones desde clientes externos en desarrollo.
