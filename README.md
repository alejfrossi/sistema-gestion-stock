# 📦 Sistema de Gestión de Stock

Sistema profesional de control de inventarios desarrollado con Python y Django. Permite la gestión completa (CRUD) de productos, categorías y control de stock en tiempo real.

> 🚀 **Demo En Vivo:** [LINK](https://sistema-stock-alejo-rossi.onrender.com)
>
> *Usuario de prueba:* `admin`
> *Contraseña:* `1234`

## 💻 Tecnologías Utilizadas

* **Backend:** Python 3, Django 5
* **Base de Datos:** PostgreSQL
* **Frontend:** Django Templates, Bootstrap 5 (Responsive Design)
* **Herramientas:** Git, Virtualenv

## 🧠 Arquitectura y Decisiones Técnicas

* **Modelo Transaccional (Audit Trail):** El stock no se edita manualmente. Se utiliza un modelo `StockMovement` que registra entradas y salidas.
* **Encapsulamiento de Lógica:** Sobreescritura del método `save()` en el modelo para recalcular el stock automáticamente tras cada transacción, garantizando consistencia.
* **Seguridad en Profundidad:**
    * Protección de rutas con decoradores `@login_required`.
    * Variables de entorno (`.env`) para credenciales sensibles.
    * Validación de formularios con protección CSRF.
* **Diseño Escalable:** Estructura de carpetas profesional tipo `src/` separando configuración (`config`) de lógica de negocio (`apps`).
* **Database Optimization:** Uso de QuerySets avanzados con objetos `Q` para búsquedas complejas y filtrado eficiente.
* **Campos Calculados:** Propiedades dinámicas (`@property`) para cálculos de valoración de inventario en tiempo real sin impactar la base de datos.

## 🗄️ Esquema de Base de Datos

El sistema utiliza **PostgreSQL** con las siguientes relaciones clave:

* **User (Auth):** Administradores y empleados del sistema.
* **Category:** Clasificación de productos.
* **Product:** Entidad principal (contiene SKU, Precio, Stock Actual).
* **StockMovement:** Tabla histórica. Cada fila representa una alteración del stock (Entrada/Salida), vinculada a un *Usuario* (responsable) y un *Producto*.
    * *Relación:* 1 Producto tiene N Movimientos (One-to-Many).

## ✨ Funcionalidades Principales

* ✅ **Dashboard Administrativo:** Panel de control seguro (Django Admin).
* ✅ **Gestión de Inventario:** Crear, leer, editar y eliminar productos.
* ✅ **Buscador Inteligente:** Filtrado por nombre y categoría en tiempo real.
* ✅ **Categorización:** Organización de productos por familias.
* ✅ **Control de Stock:** Visualización de alertas de stock.

## 🧑🏻‍💻 Roadmap y Futuras Mejoras

* [ ] **Reportes en PDF:** Generación de albaranes de entrada/salida.
* [ ] **Gráficos Estadísticos:** Dashboard con Chart.js para visualizar ventas mensuales.
* [ ] **API REST:** Implementación de Django REST Framework para conectar con Apps Móviles.
* [ ] **Alertas por Email:** Notificación automática a proveedores cuando el stock es crítico.

## 🔧 Instalación y Configuración

1. **Clonar el repositorio:**
   ```bash
   git clone [https://github.com/TU_USUARIO/sistema-gestion-stock.git](https://github.com/TU_USUARIO/sistema-gestion-stock.git)
   cd sistema-gestion-stock
