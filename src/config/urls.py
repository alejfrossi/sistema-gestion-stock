"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    
    # Rutas Web (HTML)
    path('productos/', include('apps.inventory.urls')),
    # Rutas API (JSON)
    path('api/', include('apps.inventory.urls_api')),

    # RUTAS DE DOCUMENTACIÓN DE API
    # 1. El archivo schema.yml (la "receta" cruda de tu API)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    
    # 2. Swagger UI (La interfaz interactiva para devs)
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    
    # 3. Redoc (Otra interfaz más limpia, solo lectura)
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # Redirigir la raíz al listado de productos
    path('', RedirectView.as_view(url='/productos/', permanent=True)),
]